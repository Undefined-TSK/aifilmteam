# -*- coding: utf-8 -*-
"""mcp_pilot_agent —— R17-8a 试点：LLM 经自研 MCP 层直接操控 Blender（1-2 镜）

SPDX-License-Identifier: GPL-2.0-or-later

老板裁定 R17-8a：白模环节执行方式 = "LLM 经 MCP 直接操控 Blender"——
不做 intent→固定代码的预设翻译，LLM 像人一样调工具摆场景/机位/灯光/动画。

数据流：
  本脚本（MCP 客户端，stdio）
    → baimo_mcp_server.py（MCP 协议翻译，交付物 2）
    → baimo_mcp_addon（JSON-RPC socket，交付物 1）
    → Blender 5.2.2 headless

闭环（≤8 轮）：
  简报(master_v2.json 1-2 已签数据 + 36项提案 camera 建议, 仅参考)
    → qwen3.8-max(high_deep) Function Calling 调工具
    → render_preview 截图 → qwen3-vl-flash(vision) 自检不符点
    → 修正迭代 → 定稿 render_playblast(72帧 MP4) + save_blend

可复现：每轮 LLM 决策与工具调用全部落 outputs/mcp_pilot/。

用法：
  python mcp_pilot_agent.py run                 # 全闭环（需 Blender 服务端已启动）
  python mcp_pilot_agent.py run --max-rounds 8 --dry-vision
  python mcp_pilot_agent.py measure <video>     # 首/中/尾帧像素 diff 动感量化
  python mcp_pilot_agent.py measure-compare     # 试点版 vs 脚本版对照
"""
import argparse
import base64
import json
import os
import subprocess
import sys
import time
from pathlib import Path

# 维度25：根路径由文件位置反推（原硬编码 D:/aifilmteam/...，换机即失效）
V2_ROOT = str(Path(__file__).resolve().parents[1])
ROOT = str(Path(V2_ROOT).parent)
sys.path.insert(0, os.path.join(V2_ROOT, "tools"))
import llm_gateway  # noqa: E402

# ---- 兼容补丁（不改 llm_gateway.py 文件）----
# 既有 bug：Gateway._run_chain 网络异常分支调 _slide(i, reason, code) 少传
# switches（llm_gateway.py:279），一遇网络超时即 TypeError 崩溃。
# 此处运行时补默认值，保留滑链+切换留痕语义不变。
_orig_slide = llm_gateway.Gateway._slide


def _slide_compat(self, fail_idx, reason, error_code, switches=None):
    if switches is None:
        switches = []
    return _orig_slide(self, fail_idx, reason, error_code, switches)


llm_gateway.Gateway._slide = _slide_compat

MASTER_JSON = os.path.join(V2_ROOT, "projects", "雨夜寻猫", "00_brief",
                           "timeline", "master_v2.json")
PROPOSALS_MD = os.path.join(ROOT, "docs", "07-交接与日志",
                            "R0-T4-批次1-创作提案-36项.md")
MCP_SERVER = os.path.join(V2_ROOT, "mcp_blender", "baimo_mcp_server.py")
PILOT_DIR = os.path.join(ROOT, "outputs", "mcp_pilot")
SHOT_OUT_DIR = os.path.join(ROOT, "outputs", "blockout", "1-2_mcp")
SHOT_ID = "1-2"
MAX_ROUNDS = 8


def _set_out_dirs(pilot_dir=None, shot_out_dir=None):
    """CLI 覆盖输出目录（R17-9-3 重跑用 v2 目录，v1 产物保持不动）。"""
    global PILOT_DIR, SHOT_OUT_DIR
    if pilot_dir:
        PILOT_DIR = pilot_dir if os.path.isabs(pilot_dir) \
            else os.path.join(ROOT, pilot_dir)
    if shot_out_dir:
        SHOT_OUT_DIR = shot_out_dir if os.path.isabs(shot_out_dir) \
            else os.path.join(ROOT, shot_out_dir)


# ============================ MCP 客户端（stdio） ============================

class McpClient:
    """最小 MCP 客户端：spawn baimo_mcp_server.py，换行分隔 JSON 通信。"""

    def __init__(self, server_script=MCP_SERVER):
        self.proc = subprocess.Popen(
            [sys.executable, server_script],
            stdin=subprocess.PIPE, stdout=subprocess.PIPE,
            stderr=subprocess.DEVNULL, text=True, encoding="utf-8", bufsize=1)
        self._id = 0

    def _next_id(self):
        self._id += 1
        return self._id

    def request(self, method, params=None):
        rid = self._next_id()
        msg = {"jsonrpc": "2.0", "id": rid, "method": method}
        if params is not None:
            msg["params"] = params
        self.proc.stdin.write(json.dumps(msg, ensure_ascii=False) + "\n")
        self.proc.stdin.flush()
        while True:
            line = self.proc.stdout.readline()
            if not line:
                raise ConnectionError("MCP server stdout 关闭")
            resp = json.loads(line)
            if resp.get("id") == rid:
                if "error" in resp:
                    raise RuntimeError("MCP error: %s" % resp["error"])
                return resp.get("result")

    def notify(self, method, params=None):
        msg = {"jsonrpc": "2.0", "method": method}
        if params is not None:
            msg["params"] = params
        self.proc.stdin.write(json.dumps(msg, ensure_ascii=False) + "\n")
        self.proc.stdin.flush()

    def handshake(self):
        self.request("initialize", {"protocolVersion": "2025-06-18",
                                    "capabilities": {},
                                    "clientInfo": {"name": "mcp_pilot_agent",
                                                   "version": "0.1.0"}})
        self.notify("notifications/initialized")

    def tools_list(self):
        return self.request("tools/list")["tools"]

    def call_tool(self, name, arguments=None, log_path=None):
        r = self.request("tools/call", {"name": name,
                                        "arguments": arguments or {}})
        text = r["content"][0]["text"]
        if log_path:
            with open(log_path, "a", encoding="utf-8") as f:
                f.write(json.dumps({"ts": time.strftime("%H:%M:%S"),
                                    "via": "mcp", "tool": name,
                                    "arguments": arguments, "result": text[:2000]},
                                   ensure_ascii=False) + "\n")
        if r.get("isError"):
            raise RuntimeError("tool %s 失败: %s" % (name, text))
        try:
            return json.loads(text)
        except ValueError:
            return text

    def close(self):
        try:
            self.proc.stdin.close()
        except Exception:
            pass
        try:
            self.proc.wait(timeout=5)
        except Exception:
            self.proc.kill()


# ============================ 简报装载 ============================

def load_brief():
    """1-2 镜简报：master_v2.json 已签轨数据 + 36项提案 camera 建议节选。

    ⚠️ 简报仅作参考输入（R17-8a 纪律：禁止硬编码成脚本步骤——场景怎么摆
    由 LLM 自行决定工具调用序列）。
    """
    d = json.load(open(MASTER_JSON, encoding="utf-8"))
    brief = {}
    for tname in ("camera", "gauge", "light", "edit", "clock", "ambience"):
        for it in d["tracks"].get(tname, {}).get("items", []):
            if it.get("shot_id") == SHOT_ID:
                it = {k: v for k, v in it.items() if k != "signoff"}
                brief[tname] = it
                break
    dur = brief["edit"]["out_f"] - brief["edit"]["in_f"] + 1
    brief["duration_frames"] = dur
    # 36 项提案 1-2 节选（camera 建议参考）
    excerpt = ""
    try:
        txt = open(PROPOSALS_MD, encoding="utf-8").read()
        lines = txt.splitlines()
        idx = [i for i, l in enumerate(lines) if l.startswith("**1-2 camera")]
        if idx:
            excerpt = "\n".join(lines[idx[0]:idx[0] + 18])
    except OSError:
        pass
    brief["proposals_1_2_excerpt"] = excerpt
    return brief


def brief_text(b):
    return (
        "【1-2 镜简报（签核数据，仅供参考——你自行决定工具调用序列）】\n"
        "场景：出租屋内。叙事意图：空猫窝 = “丢失的第一信号”，镜头缓推逼近空窝。\n"
        "camera 轨（已签）：%s\n"
        "light 轨（已签）：%s（色温 8500K 为冷蓝，参考 RGB≈[0.6,0.75,1.0]；"
        "主光经窗户方向打在空窝上，辅光为主光 1/3）\n"
        "gauge 轨：%s\n"
        "剪辑轨：本镜 %d 帧（fps 24）。动画要求：dolly 推进——相机从起始位缓慢推向空窝，"
        "首尾两帧都要打相机关键帧（keyframe_camera），推进幅度参考 fps_move=0.25（缓推不越过主体）。\n"
        "白模要求：占位几何即可，但要能读出“窗台上空猫窝”的构图层级（窗/窗台/窝/窝口），"
        "配人形与四足占位可选（本镜 ECU 特写可不放）。\n"
        "36项提案 camera 建议节选：\n%s\n"
        % (json.dumps(b.get("camera", {}), ensure_ascii=False),
           json.dumps(b.get("light", {}), ensure_ascii=False),
           json.dumps(b.get("gauge", {}), ensure_ascii=False),
           b["duration_frames"], b.get("proposals_1_2_excerpt", "(缺)")))


# ============================ 自研 MCP 工具执行 ============================

def openai_tools_from_mcp(mcp_tools):
    """MCP inputSchema → OpenAI/DashScope function 定义。"""
    out = []
    for t in mcp_tools:
        out.append({"type": "function", "function": {
            "name": t["name"], "description": t["description"],
            "parameters": t.get("inputSchema", {"type": "object"})}})
    return out


# ============================ 视觉自检 ============================

VL_PROMPT = (
    "你是白模 QC。判断这张 Blender 白模渲染帧是否符合以下意图与简报：\n"
    "意图：出租屋内，冷蓝窗光打在窗台上的空猫窝（Ecu 特写层级：窗/窗台/空窝），"
    "构图指向空窝（此帧为 dolly 推镜一帧）。\n"
    "白模标准：占位几何允许，但需读出窗-窗台-空窝层级、冷蓝色调主光、"
    "画面无穿模/无相机打入物体内部/主体未被完全遮挡。\n"
    "输出 JSON：{\"pass\": true/false, \"issues\": [\"不符点…\"], "
    "\"notes\": \"一句话总评\"}。宁可严格：构图层级缺失或全冷黑不可读都算不通过。")


def vl_check(png_path):
    with open(png_path, "rb") as f:
        b64 = base64.b64encode(f.read()).decode("ascii")
    g = llm_gateway.Gateway("vision")
    r = g.chat([{"role": "user", "content": [
        {"type": "text", "text": VL_PROMPT},
        {"type": "image_url", "image_url": {"url": "data:image/png;base64," + b64}},
    ]}], max_tokens=800)
    verdict = llm_gateway.parse_json_content(r["content"])
    tokens = _usage_tokens(r)
    return verdict, r["model"], tokens


def _usage_tokens(resp):
    u = (resp.get("raw") or {}).get("usage") or {}
    return int(u.get("prompt_tokens") or 0), int(u.get("completion_tokens") or 0)


# ---- 末帧防怼脸软护栏（R17-9-2）：VL 判"贴脸/穿模"→自动回撤一步重打末帧 ----

GUARD_PROMPT = (
    "你是运镜 QC。判断这张渲染帧中相机是否\"贴脸/穿模\"：判定为真的标准——"
    "单一曲面占满画面几乎无环境参照、或相机明显贴着/穿入几何体表面。"
    "正常的近景构图（主体清晰但仍有环境层次）判 false。"
    "输出 JSON：{\"too_close\": true/false, \"reason\": \"一句话\"}。")


def vl_guard_check(png_path):
    with open(png_path, "rb") as f:
        b64 = base64.b64encode(f.read()).decode("ascii")
    g = llm_gateway.Gateway("vision")
    r = g.chat([{"role": "user", "content": [
        {"type": "text", "text": GUARD_PROMPT},
        {"type": "image_url", "image_url": {"url": "data:image/png;base64," + b64}},
    ]}], max_tokens=500)
    return llm_gateway.parse_json_content(r["content"])


def guard_last_frame(mcp, cam_name, frames):
    """末帧 preview → VL 判贴脸 → 判是则沿视线反方向回撤 0.5m 重打末帧关键帧。

    软护栏：任何失败都不阻塞出片，只留档（R17-9 裁定）。"""
    out = {"checked": True, "camera": cam_name, "frame": frames}
    try:
        gpath = os.path.join(PILOT_DIR, "guard_lastframe.png")
        mcp.call_tool("render_preview", {"camera": cam_name,
                                         "output_path": gpath,
                                         "frame": frames, "res": [640, 360]})
        v = vl_guard_check(gpath)
        out["verdict"] = v
        out["image"] = gpath
        log_agent({"event": "guard_check", "verdict": v, "image": gpath})
        if v.get("too_close"):
            st = mcp.call_tool("scene_state")
            camo = next((o for o in st["objects"]
                         if o["name"] == cam_name and o["type"] == "CAMERA"), None)
            if camo is None:
                raise ValueError("护栏找不到相机 %r" % cam_name)
            tgt = next((o for o in st["objects"]
                        if o["name"] == "target_%s" % cam_name), None)
            loc = camo["location"]
            aim = tgt["location"] if tgt else [0.0, 0.6, 0.55]
            d = [aim[i] - loc[i] for i in range(3)]
            L = (d[0] ** 2 + d[1] ** 2 + d[2] ** 2) ** 0.5 or 1.0
            back = [round(loc[i] - d[i] / L * 0.3, 4) for i in range(3)]
            r2 = mcp.call_tool("keyframe_camera", {"name": cam_name,
                                                   "frame": frames,
                                                   "location": back,
                                                   "aim": aim})
            out["retreat"] = {"new_location": back, "result": r2}
            gpath2 = gpath.replace(".png", "_after.png")
            mcp.call_tool("render_preview", {"camera": cam_name,
                                             "output_path": gpath2,
                                             "frame": frames, "res": [640, 360]})
            v2 = vl_guard_check(gpath2)
            out["verdict_after"] = v2
            out["image_after"] = gpath2
            log_agent({"event": "guard_recheck", "retreat_to": back,
                       "verdict": v2})
    except Exception as exc:   # 软护栏：失败不阻塞
        out["error"] = str(exc)
        log_agent({"event": "guard_error", "error": str(exc)})
    return out


# ============================ 主闭环 ============================

def log_agent(rec):
    p = os.path.join(PILOT_DIR, "agent_log.jsonl")
    with open(p, "a", encoding="utf-8") as f:
        rec["ts"] = time.strftime("%Y-%m-%dT%H:%M:%S")
        f.write(json.dumps(rec, ensure_ascii=False) + "\n")


def dump_messages(round_no, messages):
    p = os.path.join(PILOT_DIR, "messages_round%d.json" % round_no)
    with open(p, "w", encoding="utf-8") as f:
        json.dump(messages, f, ensure_ascii=False, indent=1)


def run(max_rounds=MAX_ROUNDS, dry_vision=False):
    os.makedirs(PILOT_DIR, exist_ok=True)
    brief = load_brief()
    mcp = McpClient()
    try:
        mcp.handshake()
        tools = mcp.tools_list()
        log_agent({"event": "mcp_ready", "tools": [t["name"] for t in tools]})
        oa_tools = openai_tools_from_mcp(tools)

        system = (
            "你是白模场景操作员：通过工具在 Blender 里从零搭出指定镜头的白模场景、"
            "机位、灯光与相机动画。像人类美工一样工作：先 scene_state 观察，逐步搭建，"
            "不确定就再观察。轮次预算很紧（共 %d 轮）：场景搭建控制在 4 轮内，"
            "之后必须 render_preview（camera=你的相机名, "
            "output_path=D:/aifilmteam/outputs/mcp_pilot_v2/preview.png, frame=帧区间中点）"
            "出检查图收尾。相机必须有 aim（TRACK_TO 靶）；"
            "dolly 运镜必须调两次 keyframe_camera：frame=1 起点位、frame=末帧 推近位"
            "（两处 location 必须不同）；行程尽量拉大（建议首尾位移 ≥1.5m，"
            "末帧停在距主体表面 0.3m 之外，既保证动感又不穿模）。"
            "默认场景的 Cube/Light/Camera 是遗留物：用 place_object 把 Cube 挪出画面"
            "（如 location=[-30,-30,-30]），不要删除（无删除工具）。"
            "工具经 MCP 层执行。每轮只做一轮工具调用。"
            % max_rounds)
        messages = [
            {"role": "system", "content": system},
            {"role": "user", "content": brief_text(brief)
             + "\n\n现在开始。目标：搭好 1-2 镜白模（含 dolly 相机动画与冷蓝窗光），"
               "出 preview 检查图。"
               "\n\n【硬性验收要求（本轮拍板）】首尾相机位移 ≥2.5m——具体起始点、"
               "路径与机位高度你自行设计（这是性能指标不是步骤指令）；"
               "末帧防怼脸有自动护栏兜底（判贴脸会帮你回撤重打末帧），"
               "所以大胆推近，不必保守。"},
        ]

        last_preview = None
        last_preview_cam = None
        vl_history = []
        tok_in = tok_out = 0
        passed = False
        g = llm_gateway.Gateway("high_deep")

        for rnd in range(1, max_rounds + 1):
            t0 = time.time()
            resp = g.chat(messages, tools=oa_tools, max_tokens=6144)
            pt, ct = _usage_tokens(resp)
            tok_in += pt
            tok_out += ct
            msg = resp["raw"]["choices"][0]["message"]
            calls = msg.get("tool_calls") or []
            log_agent({"event": "llm_round", "round": rnd,
                       "model": resp["model"], "provider": resp["provider"],
                       "tool_calls": [c["function"]["name"] for c in calls],
                       "content": (msg.get("content") or "")[:500],
                       "tokens": [pt, ct], "seconds": round(time.time() - t0, 1)})
            messages.append({"role": "assistant", "content": msg.get("content"),
                             "tool_calls": msg.get("tool_calls")})
            if not calls:
                messages.append({"role": "user", "content":
                                 "请继续用工具操作（scene_state/create_primitive/…），"
                                 "完成后 render_preview 出检查图。"})
                dump_messages(rnd, messages)
                continue
            for c in calls:
                fn = c["function"]
                name = fn["name"]
                try:
                    args = json.loads(fn["arguments"] or "{}")
                except ValueError:
                    args = {}
                try:
                    result = mcp.call_tool(name, args,
                                           log_path=os.path.join(PILOT_DIR,
                                                                 "agent_log.jsonl"))
                    text = json.dumps(result, ensure_ascii=False)
                except Exception as exc:
                    text = "ERROR: %s" % exc
                    log_agent({"event": "tool_error", "round": rnd,
                               "tool": name, "error": str(exc)})
                if name == "render_preview" and isinstance(result, dict):
                    last_preview = result.get("saved")
                    last_preview_cam = args.get("camera")
                messages.append({"role": "tool", "tool_call_id": c["id"],
                                 "content": text[:4000]})
            dump_messages(rnd, messages)
            # ---- 轮次预算提醒（未出过 preview 且轮次过半时）----
            if last_preview is None and rnd >= max_rounds // 2:
                messages.append({"role": "user", "content":
                                 "⚠️ 已用 %d/%d 轮且尚未出 render_preview 检查图。"
                                 "请立即完成：① dolly 相机动画（keyframe_camera "
                                 "frame=1 起点位 + frame=%d 推近位，两处 location "
                                 "必须不同）② render_preview 出图。"
                                 % (rnd, max_rounds, brief["duration_frames"])})
            # ---- VL 自检（本轮出过 preview 才检）----
            if last_preview and os.path.exists(last_preview):
                if dry_vision:
                    verdict, vl_model, vtok = {"pass": True, "issues": [],
                                               "notes": "dry-run"}, "dry", (0, 0)
                else:
                    verdict, vl_model, vtok = vl_check(last_preview)
                tok_in += vtok[0]
                tok_out += vtok[1]
                vl_history.append({"round": rnd, "verdict": verdict,
                                   "model": vl_model, "image": last_preview})
                log_agent({"event": "vl_check", "round": rnd,
                           "verdict": verdict, "model": vl_model,
                           "image": last_preview})
                if verdict.get("pass"):
                    passed = True
                    print("VL_PASS at round %d" % rnd)
                    break
                issues = json.dumps(verdict.get("issues", []), ensure_ascii=False)
                messages.append({"role": "user", "content":
                                 "QC 不通过，不符点：%s。请修正场景/灯光/构图后重新 "
                                 "render_preview。室内全黑的常见原因（按经验排查）："
                                 "① 无环境光——set_world(strength=0.4~0.8, 冷灰"
                                 "[0.5,0.55,0.65]) 打基础照明；"
                                 "② 窗玻璃是不透光灰板——把窗玻璃挪到墙外侧或缩小，"
                                 "③ 室外 SUN 照不进室内——改用大能量 AREA 灯贴在窗口"
                                 "朝室内（energy≥1000，size≥1.5，颜色冷蓝[0.6,0.75,1]），"
                                 "④ 相机贴墙/穿模——place_object 拉开相机与墙距离。"
                                 % issues})
        rounds_used = len(vl_history) or max_rounds
        print("LOOP_DONE passed=%s rounds=%d tokens_in=%d tokens_out=%d"
              % (passed, rounds_used, tok_in, tok_out))

        # ---- 定稿：末帧防怼脸软护栏 → playblast + save_blend ----
        frames = brief["duration_frames"]
        guard = guard_last_frame(mcp, _pick_camera(mcp, last_preview_cam), frames)
        play = mcp.call_tool("render_playblast", {
            "camera": guard.get("camera") or _pick_camera(mcp, last_preview_cam),
            "output_dir": SHOT_OUT_DIR,
            "start": 1, "end": frames, "fps": 24, "res": [832, 480]})
        log_agent({"event": "playblast", "result": play})
        save = mcp.call_tool("save_blend", {
            "path": os.path.join(PILOT_DIR, "shot_%s.blend" % SHOT_ID.replace("-", "-"))})
        log_agent({"event": "save_blend", "result": save})
        summary = {"shot": SHOT_ID, "vl_passed": passed,
                   "vl_semantics": "reference_only(R17-9-1)：判定留档不阻塞出片",
                   "vl_rounds": rounds_used, "vl_history": vl_history,
                   "guard": guard,
                   "tokens_in": tok_in, "tokens_out": tok_out,
                   "frames": frames, "playblast": play, "save_blend": save}
        with open(os.path.join(PILOT_DIR, "pilot_summary.json"), "w",
                  encoding="utf-8") as f:
            json.dump(summary, f, ensure_ascii=False, indent=1)
        print(json.dumps(summary, ensure_ascii=False)[:1500])
        return 0
    finally:
        mcp.close()


def _pick_camera(mcp, preferred=None):
    """优先用 render_preview 验证过的相机；否则场景活动相机。
    （教训：LLM 重复 add_camera 会产生无关键帧的新相机，取最新会静帧。）"""
    if preferred:
        return preferred
    st = mcp.call_tool("scene_state")
    cams = [o["name"] for o in st.get("objects", []) if o["type"] == "CAMERA"]
    active = st.get("active_camera")
    if active in cams:
        return active
    return cams[-1] if cams else "cam"


# ============================ 动感量化（首/中/尾帧像素 diff） ============================

def _ff():
    import shutil
    return shutil.which("ffmpeg")


def _ffprobe():
    """ffprobe 不在 PATH 时从 ffmpeg 同目录解析。"""
    ff = _ff()
    fp = ff.replace("ffmpeg", "ffprobe") if ff else None
    import shutil
    return fp if fp and os.path.exists(fp) else shutil.which("ffprobe")


def _probe_size(video):
    r = subprocess.run([_ffprobe(), "-v", "error",
                        "-select_streams", "v:0", "-show_entries",
                        "stream=width,height,nb_frames,avg_frame_rate",
                        "-show_entries", "format=duration",
                        "-of", "json", video],
                       capture_output=True, text=True)
    d = json.loads(r.stdout)
    st = d["streams"][0]
    try:
        fps = eval(st.get("avg_frame_rate") or "24") or 24.0
    except Exception:
        fps = 24.0
    dur = float(d.get("format", {}).get("duration") or 0) or None
    if dur is None and st.get("nb_frames"):
        dur = int(st["nb_frames"]) / fps
    return st["width"], st["height"], st.get("nb_frames"), dur, fps


def _grab(video, t, wh):
    w, h = wh
    out = os.path.join(PILOT_DIR, "_grab.raw")
    subprocess.run([_ff(), "-y", "-ss", "%.3f" % t, "-i", video, "-frames:v", "1",
                    "-f", "rawvideo", "-pix_fmt", "gray", out],
                   capture_output=True)
    d = open(out, "rb").read()
    return d if len(d) == w * h else None


def measure(video):
    """首/中/尾帧像素 diff：pct = mean|a-b|/255*100。返回三对 + 均值。"""
    w, h, nb, dur_s, fps = _probe_size(video)
    wh = (w, h)
    f0 = _grab(video, 0.0, wh)
    fm = _grab(video, (dur_s or 0) / 2.0, wh)
    fl = _grab(video, max(0.0, (dur_s or 1.0) - 0.5), wh)

    def diff(a, b):
        if a is None or b is None:
            return None, None
        n = len(a)
        idx = range(0, n, 7)                     # 1/7 抽样
        s = cnt = changed = 0
        for i in idx:
            d = abs(a[i] - b[i])
            s += d
            cnt += 1
            changed += d >= 8                    # 可见变化阈值(8/255)
        return (round(s / cnt / 255.0 * 100.0, 2),       # mean-abs 口径
                round(changed / cnt * 100.0, 2))         # 变化像素占比口径

    m0m, c0m = diff(f0, fm)
    mml, cml = diff(fm, fl)
    m0l, c0l = diff(f0, fl)
    r = {"video": video, "frames": nb, "duration_s": round(dur_s or 0, 2),
         "mean_abs_pct": {"first_mid": m0m, "mid_last": mml,
                          "first_last": m0l},
         "changed_pct": {"first_mid": c0m, "mid_last": cml,
                         "first_last": c0l}}

    def avg(d):
        vals = [v for v in d.values() if v is not None]
        return round(sum(vals) / len(vals), 2) if vals else None

    r["avg_mean_abs_pct"] = avg(r["mean_abs_pct"])
    r["avg_changed_pct"] = avg(r["changed_pct"])
    return r


def measure_compare():
    new = measure(os.path.join(SHOT_OUT_DIR, "blockout.mp4"))
    old = measure(os.path.join(ROOT, "outputs", "blockout", "1-2", "blockout.mp4"))
    out = {"mcp_pilot": new, "script_version": old}
    with open(os.path.join(PILOT_DIR, "motion_compare.json"), "w",
              encoding="utf-8") as f:
        json.dump(out, f, ensure_ascii=False, indent=1)
    print(json.dumps(out, ensure_ascii=False, indent=1))


# ============================ 人审卡片（R17-9-1 配套） ============================

def _load_op_keyframes(op_paths):
    """从 op_log 提取相机关键帧调用（动画路径素材）。"""
    kf = []
    for p in op_paths:
        if not os.path.exists(p):
            continue
        for line in open(p, encoding="utf-8"):
            try:
                r = json.loads(line)
            except ValueError:
                continue
            if r.get("method") == "keyframe_camera" and r.get("ok"):
                kf.append({"frame": r["params"].get("frame"),
                           "location": r["params"].get("location"),
                           "aim": r["params"].get("aim"),
                           "src": os.path.basename(p)})
    return kf


def _load_rounds(pilot_dir):
    """从 agent_log 提取逐轮 LLM 决策与 VL 判定（卡片素材）。"""
    log = os.path.join(pilot_dir, "agent_log.jsonl")
    rounds, vls = {}, []
    if not os.path.exists(log):
        return rounds, vls
    for line in open(log, encoding="utf-8"):
        try:
            r = json.loads(line)
        except ValueError:
            continue
        e = r.get("event")
        if e == "llm_round":
            rounds.setdefault(r["round"], {})["calls"] = r.get("tool_calls")
            rounds[r["round"]]["model"] = r.get("model")
        elif e == "vl_check":
            v = r.get("verdict") or {}
            vls.append({"round": r.get("round"), "pass": v.get("pass"),
                        "notes": v.get("notes"),
                        "issues": v.get("issues")})
        elif e == "guard_check":
            v = r.get("verdict") or {}
            vls.append({"round": "guard", "pass": not v.get("too_close"),
                        "notes": "末帧防怼脸护栏: %s" % v.get("reason", "")})
    return rounds, vls


def gen_review_card(v1_pilot, v2_pilot, v1_video, v2_video, out_path):
    """生成 v1 vs v2 人审卡片 Markdown（导演裁决用）。"""
    m1 = measure(v1_video)
    m2 = measure(v2_video)
    script_m = measure(os.path.join(ROOT, "outputs", "blockout", "1-2",
                                    "blockout.mp4"))
    kf1 = _load_op_keyframes([
        os.path.join(v1_pilot, "op_log.jsonl"),
        os.path.join(v1_pilot, "op_log_dev_archive.jsonl")])
    kf2 = _load_op_keyframes([os.path.join(v2_pilot, "op_log.jsonl"),
                              os.path.join(v2_pilot, "op_log_repair.jsonl")])
    r1, vl1 = _load_rounds(v1_pilot)
    r2, vl2 = _load_rounds(v2_pilot)

    def s1(v):
        cp = v.get("changed_pct") or {}
        return (cp.get("first_last"), cp.get("first_mid"), cp.get("mid_last"),
                v.get("avg_changed_pct"))

    def rounds_md(rounds):
        if not rounds:
            return "（无记录）"
        rows = []
        for rnd in sorted(rounds):
            info = rounds[rnd]
            rows.append("| %s | %s | %s |" % (
                rnd, info.get("model"),
                ", ".join(info.get("calls") or []) or "(无工具调用)"))
        return "\n".join(["| 轮 | 模型 | 工具调用 |", "|---|---|---|"] + rows)

    def vls_md(vls):
        if not vls:
            return "（本轮无 VL 判定记录）"
        rows = []
        for v in vls:
            rows.append("- **R%s pass=%s**：%s%s" % (
                v.get("round"), v.get("pass"),
                str(v.get("notes") or "")[:110],
                ("｜不符点：%s" % str(v.get("issues"))[:110]) if v.get("issues") else ""))
        return "\n".join(rows)

    def kf_md(kf):
        if not kf:
            return "（无 keyframe_camera 记录）"
        rows = []
        for k in kf:
            rows.append("- frame=%s loc=%s aim=%s" % (
                k.get("frame"), k.get("location"), k.get("aim")))
        return "\n".join(rows)

    card = """# 1-2 镜 MCP 试点 v1 vs v2 人审卡片（R17-9-1）

> 生成：%s ｜ 供导演裁决；数据源：mcp_pilot(v1) / mcp_pilot_v2(v2) 全程日志

## 一、动画路径（相机关键帧实测）

**v1（首轮试点）**
%s

**v2（VL 修复轮：+世界环境光 + 防怼脸软护栏）**
%s

## 二、动感量化对比（首/中/尾帧像素 diff，|diff|≥8 变化像素占比）

| 版本 | 首尾 first_last | 首中 first_mid | 中尾 mid_last | 三段均值 |
|---|---|---|---|---|
| 脚本版（基线，47.9%% 出处） | %s | %s | %s | %s |
| v1 MCP 试点 | %s | %s | %s | %s |
| **v2 VL 修复轮** | **%s** | **%s** | **%s** | **%s** |

## 三、VL 逐轮判定摘要（R17-9-1 起 VL 为参考记录，不阻塞出片）

**v1**（VL 语义：阻塞参考，4 轮全否决——dolly 末段怼进猫窝曲面）
%s

**v2**（含末帧防怼脸护栏判定）
%s

## 四、LLM 关键决策点

**v1 工具调用轨迹**
%s

**v2 工具调用轨迹**
%s

## 五、产物路径

- v1：`outputs/blockout/1-2_mcp/blockout.mp4`（72 帧）
- v2：`outputs/blockout/1-2_mcp_v2/blockout.mp4`（72 帧）
- 日志：`outputs/mcp_pilot{,_v2}/`（op_log / agent_log / messages_roundN.json / pilot_summary.json）
""" % (time.strftime("%Y-%m-%d %H:%M"),
       kf_md(kf1), kf_md(kf2),
       s1(script_m)[0], s1(script_m)[1], s1(script_m)[2], s1(script_m)[3],
       s1(m1)[0], s1(m1)[1], s1(m1)[2], s1(m1)[3],
       s1(m2)[0], s1(m2)[1], s1(m2)[2], s1(m2)[3],
       vls_md(vl1), vls_md(vl2),
       rounds_md(r1), rounds_md(r2))
    with open(out_path, "w", encoding="utf-8") as f:
        f.write(card)
    return out_path


def main():
    p = argparse.ArgumentParser("mcp_pilot_agent")
    sub = p.add_subparsers(dest="cmd", required=True)
    pr = sub.add_parser("run")
    pr.add_argument("--max-rounds", type=int, default=MAX_ROUNDS)
    pr.add_argument("--dry-vision", action="store_true",
                    help="跳过 VL 自检（链路联调用）")
    pr.add_argument("--pilot-dir", default=None,
                    help="覆盖试点日志目录（R17-9-3 用 mcp_pilot_v2）")
    pr.add_argument("--shot-out-dir", default=None,
                    help="覆盖成片输出目录（R17-9-3 用 1-2_mcp_v2）")
    pm = sub.add_parser("measure")
    pm.add_argument("video")
    sub.add_parser("measure-compare")
    pc = sub.add_parser("card")
    pc.add_argument("--v1-pilot", default=os.path.join(ROOT, "outputs", "mcp_pilot"))
    pc.add_argument("--v2-pilot", default=os.path.join(ROOT, "outputs", "mcp_pilot_v2"))
    pc.add_argument("--v1-video",
                    default=os.path.join(ROOT, "outputs", "blockout", "1-2_mcp",
                                         "blockout.mp4"))
    pc.add_argument("--v2-video",
                    default=os.path.join(ROOT, "outputs", "blockout", "1-2_mcp_v2",
                                         "blockout.mp4"))
    pc.add_argument("--out", default=os.path.join(ROOT, "outputs", "mcp_pilot_v2",
                                                  "review_card.md"))
    a = p.parse_args()
    if a.cmd == "run":
        _set_out_dirs(a.pilot_dir, a.shot_out_dir)
        sys.exit(run(a.max_rounds, a.dry_vision))
    elif a.cmd == "measure":
        print(json.dumps(measure(a.video), ensure_ascii=False, indent=1))
    elif a.cmd == "card":
        path = gen_review_card(a.v1_pilot, a.v2_pilot, a.v1_video, a.v2_video,
                               a.out)
        print("CARD_SAVED %s" % path)
    else:
        measure_compare()


if __name__ == "__main__":
    main()
