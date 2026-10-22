# -*- coding: utf-8 -*-
"""baimo_mcp_server —— 自研 stdio MCP server（R17-8a 交付物 2，纯标准库）

SPDX-License-Identifier: GPL-2.0-or-later

定位（调研文档 docs/03-规划与调研/自包含Blender控制层方案-2026-10-04.md 主线 D）：
  把"自家 Blender addon 工具"翻译成 MCP 协议，只对自家 agent 暴露。
  协议为开放标准（MIT，Linux Foundation/AAIF 托管）；本实现按
  spec 2025-06-18 手写 stdio transport（换行分隔 JSON，无 Content-Length 头），
  零第三方依赖（不引入官方 SDK，规避供应链与版本钉扎负担）。

协议面（tools server 最小集）：
  initialize / notifications/initialized / ping / tools/list / tools/call
  下行经 JSON-RPC 2.0 over TCP 转发到 Blender addon（默认 127.0.0.1:17800）。

用法：
  python baimo_mcp_server.py                # stdio，配合 MCP 客户端
  python baimo_mcp_server.py --selftest     # 不依赖 Blender 的协议自测
"""
import json
import os
import socket
import sys

# ---- 上游 Blender addon socket ----
BLENDER_HOST = os.environ.get("BAIMO_BLENDER_HOST", "127.0.0.1")
BLENDER_PORT = int(os.environ.get("BAIMO_BLENDER_PORT", "17800"))

PROTOCOL_VERSION = "2025-06-18"
SERVER_INFO = {"name": "baimo-mcp-server", "version": "0.1.0"}

# ---- 工具清单（与 addon server.py HANDLERS 一一对应；inputSchema 即
#      addon 端注释中的参数 schema，单位约定：rotation=度、color=RGB） ----

TOOLS = [
    {"name": "ping", "description": "健康检查：返回 Blender 版本与当前渲染引擎",
     "inputSchema": {"type": "object", "properties": {}}},
    {"name": "scene_state", "description":
        "场景全量 JSON：对象清单（名称/类型/位置/旋转(度)/缩放/材质）、相机（焦距/是否有aim靶）、"
        "灯光（类型/能量/颜色）、帧区间/fps/分辨率/引擎/活动相机。LLM 摆场景前先调它观察现状。",
     "inputSchema": {"type": "object", "properties": {}}},
    {"name": "create_primitive", "description":
        "新建占位几何体（自动赋灰阶白模材质）。kind: cube|sphere|cylinder|plane|cone",
     "inputSchema": {"type": "object",
                     "properties": {
                         "kind": {"type": "string", "enum": ["cube", "sphere",
                                                             "cylinder", "plane", "cone"]},
                         "size": {"type": "number", "description": "整体尺寸(米)，球/柱/锥为直径",
                                  "default": 1.0},
                         "location": {"type": "array", "items": {"type": "number"},
                                      "minItems": 3, "maxItems": 3},
                         "rotation": {"type": "array", "items": {"type": "number"},
                                      "minItems": 3, "maxItems": 3,
                                      "description": "欧拉 XYZ，单位度"},
                         "name": {"type": "string"},
                         "shade": {"type": "number", "description": "灰度0-1，默认0.8"}},
                     "required": ["kind"]}},
    {"name": "place_object", "description": "摆位/缩放既有对象（白模布局主要工具）",
     "inputSchema": {"type": "object",
                     "properties": {
                         "name": {"type": "string"},
                         "location": {"type": "array", "items": {"type": "number"},
                                      "minItems": 3, "maxItems": 3},
                         "rotation": {"type": "array", "items": {"type": "number"},
                                      "minItems": 3, "maxItems": 3,
                                      "description": "欧拉 XYZ，单位度"},
                         "scale": {"description": "数字或[x,y,z]"}},
                     "required": ["name"]}},
    {"name": "set_gray_material", "description": "给对象换白模灰阶材质（shade 0黑-1白）",
     "inputSchema": {"type": "object",
                     "properties": {"name": {"type": "string"},
                                    "shade": {"type": "number", "default": 0.8}},
                     "required": ["name"]}},
    {"name": "add_camera", "description":
        "加相机并设为活动相机。location+rotation(度) 或 location+aim(看向上哪个点)；"
        "给 aim 时自动挂 TRACK_TO 空靶（dolly/pan 运镜推荐），靶名 target_<name>。",
     "inputSchema": {"type": "object",
                     "properties": {
                         "name": {"type": "string", "default": "cam"},
                         "lens": {"type": "number", "description": "焦距mm，默认50"},
                         "location": {"type": "array", "items": {"type": "number"},
                                      "minItems": 3, "maxItems": 3},
                         "rotation": {"type": "array", "items": {"type": "number"},
                                      "minItems": 3, "maxItems": 3},
                         "aim": {"type": "array", "items": {"type": "number"},
                                 "minItems": 3, "maxItems": 3}},
                     "required": ["location"]}},
    {"name": "keyframe_camera", "description":
        "相机关键帧（dolly/truck 运镜用）。frame 两帧以上即成动画；给 aim 则同时给靶打关键帧。",
     "inputSchema": {"type": "object",
                     "properties": {
                         "name": {"type": "string"},
                         "frame": {"type": "integer"},
                         "location": {"type": "array", "items": {"type": "number"},
                                      "minItems": 3, "maxItems": 3},
                         "aim": {"type": "array", "items": {"type": "number"},
                                 "minItems": 3, "maxItems": 3}},
                     "required": ["name", "frame"]}},
    {"name": "add_light", "description":
        "加灯。kind: SUN(能量W/m2,建议1-5)|AREA|POINT|SPOT(能量W,建议100-2000)。"
        "color 传 RGB 0-1 或 0-255（自动识别）。暖光[1,0.85,0.7] 冷蓝[0.6,0.75,1]。"
        "AREA 专属：size/size_y（米）、shape(SQUARE|RECTANGLE|DISK|ELLIPSE)。"
        "窗光配方：AREA 大面光（size≥1.5）贴窗口朝室内，energy≥1000 冷蓝。",
     "inputSchema": {"type": "object",
                     "properties": {
                         "kind": {"type": "string", "enum": ["SUN", "AREA", "POINT", "SPOT"]},
                         "energy": {"type": "number"},
                         "location": {"type": "array", "items": {"type": "number"},
                                      "minItems": 3, "maxItems": 3},
                         "color": {"type": "array", "items": {"type": "number"}},
                         "rotation": {"type": "array", "items": {"type": "number"},
                                      "minItems": 3, "maxItems": 3},
                         "size": {"type": "number", "description": "AREA 面光边长(米)"},
                         "size_y": {"type": "number",
                                    "description": "RECTANGLE 时第二边长(米)"},
                         "shape": {"type": "string",
                                   "enum": ["SQUARE", "RECTANGLE", "DISK", "ELLIPSE"]},
                         "name": {"type": "string"}},
                     "required": ["kind"]}},
    {"name": "set_world", "description":
        "世界背景环境光（室内黑的根因对策）：strength 0.3-1.0 基础照明 + "
        "color（冷灰[0.5,0.55,0.65] 之类）。世界不存在时自动创建。"
        "add_world 为同义别名。",
     "inputSchema": {"type": "object",
                     "properties": {
                         "strength": {"type": "number", "default": 1.0},
                         "color": {"type": "array", "items": {"type": "number"},
                                   "description": "RGB 0-1 或 0-255"}}}},
    {"name": "set_frame_range", "description": "设帧区间与帧率",
     "inputSchema": {"type": "object",
                     "properties": {"start": {"type": "integer"},
                                    "end": {"type": "integer"},
                                    "fps": {"type": "integer", "default": 24}},
                     "required": ["start", "end"]}},
    {"name": "render_preview", "description":
        "EEVEE 低采样单帧 PNG（默认 640x360，frame 默认 1）——给视觉模型自检画面用。"
        "相对路径按项目根目录为根解析（见 addon server.py ROOT）。",
     "inputSchema": {"type": "object",
                     "properties": {
                         "camera": {"type": "string"},
                         "output_path": {"type": "string"},
                         "frame": {"type": "integer", "default": 1},
                         "res": {"type": "array", "items": {"type": "integer"},
                                 "default": [640, 360]},
                         "samples": {"type": "integer", "default": 16}},
                     "required": ["camera", "output_path"]}},
    {"name": "render_playblast", "description":
        "白模动画：EEVEE 逐帧渲染直出 MP4（H.264，内建 FFMPEG；失败回退 PNG 序列+系统 ffmpeg）。"
        "start/end 默认场景帧区间。",
     "inputSchema": {"type": "object",
                     "properties": {
                         "camera": {"type": "string"},
                         "output_dir": {"type": "string"},
                         "start": {"type": "integer"}, "end": {"type": "integer"},
                         "fps": {"type": "integer", "default": 24},
                         "res": {"type": "array", "items": {"type": "integer"},
                                 "default": [832, 480]},
                         "samples": {"type": "integer", "default": 32}},
                     "required": ["camera", "output_dir"]}},
    {"name": "save_blend", "description": "保存 .blend 场景文件（目录自动创建）",
     "inputSchema": {"type": "object",
                     "properties": {"path": {"type": "string"},
                                    "pack": {"type": "boolean", "default": False}},
                     "required": ["path"]}},
    {"name": "shutdown_server", "description": "停掉 Blender 端 socket 服务端（headless 收尾用）",
     "inputSchema": {"type": "object", "properties": {}}},
]


# ---------- 下游：Blender addon socket 客户端 ----------

def blender_rpc(method, params=None, timeout=1800.0):
    """一次一连接的 JSON-RPC 调用（简单可靠；渲染类调用串行无并发竞争）。"""
    s = socket.create_connection((BLENDER_HOST, BLENDER_PORT), timeout=10)
    s.settimeout(timeout)
    try:
        req = json.dumps({"jsonrpc": "2.0", "id": 1, "method": method,
                          "params": params or {}}).encode("utf-8")
        s.sendall(req + b"\n")
        buf = b""
        while b"\n" not in buf:
            chunk = s.recv(65536)
            if not chunk:
                raise ConnectionError("Blender socket 连接被关闭")
            buf += chunk
        line, _ = buf.split(b"\n", 1)
        resp = json.loads(line.decode("utf-8"))
    finally:
        try:
            s.close()
        except OSError:
            pass
    if "error" in resp:
        raise RuntimeError("Blender[%s]: %s" % (method, resp["error"].get("message")))
    return resp.get("result")


# ---------- MCP 协议层 ----------

def handle_message(msg):
    """处理一条 MCP 客户端请求，返回响应 dict 或 None（notification 不回包）。"""
    method = msg.get("method", "")
    rid = msg.get("id")

    if method == "initialize":
        return {"jsonrpc": "2.0", "id": rid,
                "result": {"protocolVersion": PROTOCOL_VERSION,
                           "capabilities": {"tools": {}},
                           "serverInfo": SERVER_INFO}}
    if method == "notifications/initialized":
        return None
    if method == "ping":
        return {"jsonrpc": "2.0", "id": rid, "result": {}}
    if method == "tools/list":
        return {"jsonrpc": "2.0", "id": rid, "result": {"tools": TOOLS}}
    if method == "tools/call":
        params = msg.get("params") or {}
        name = params.get("name", "")
        args = params.get("arguments") or {}
        if not any(t["name"] == name for t in TOOLS):
            return {"jsonrpc": "2.0", "id": rid,
                    "result": {"content": [{"type": "text",
                                            "text": "未知工具: %s" % name}],
                               "isError": True}}
        try:
            result = blender_rpc(name, args)
            text = json.dumps(result, ensure_ascii=False)
            return {"jsonrpc": "2.0", "id": rid,
                    "result": {"content": [{"type": "text", "text": text}],
                               "isError": False}}
        except Exception as exc:   # 上游错误按 MCP 约定装进 result.isError
            return {"jsonrpc": "2.0", "id": rid,
                    "result": {"content": [{"type": "text",
                                            "text": "%s: %s"
                                                    % (type(exc).__name__, exc)}],
                               "isError": True}}
    # 未知方法
    if rid is None:
        return None
    return {"jsonrpc": "2.0", "id": rid,
            "error": {"code": -32601, "message": "未知 method: %s" % method}}


def serve_stdio(stdin=None, stdout=None):
    """stdio 主循环：换行分隔 JSON。MCP 规范要求消息内不得含裸换行。"""
    stdin = stdin or sys.stdin
    stdout = stdout or sys.stdout
    for line in stdin:
        line = line.strip()
        if not line:
            continue
        try:
            msg = json.loads(line)
        except ValueError as exc:
            resp = {"jsonrpc": "2.0", "id": None,
                    "error": {"code": -32700, "message": "解析错误: %s" % exc}}
        else:
            resp = handle_message(msg)
        if resp is None:
            continue
        stdout.write(json.dumps(resp, ensure_ascii=False) + "\n")
        stdout.flush()


def selftest():
    """协议自测：不经 socket，验证握手/tools/list/tools/call 的错误分支。"""
    import io
    out = io.StringIO()
    reqs = [
        {"jsonrpc": "2.0", "id": 1, "method": "initialize",
         "params": {"protocolVersion": PROTOCOL_VERSION}},
        {"jsonrpc": "2.0", "method": "notifications/initialized"},
        {"jsonrpc": "2.0", "id": 2, "method": "tools/list"},
        {"jsonrpc": "2.0", "id": 3, "method": "tools/call",
         "params": {"name": "no_such_tool", "arguments": {}}},
    ]
    serve_stdio(io.StringIO("\n".join(json.dumps(r) for r in reqs) + "\n"), out)
    lines = [json.loads(x) for x in out.getvalue().splitlines()]
    tools_n = None
    for r in lines:
        if r.get("id") == 2:
            tools_n = len(r["result"]["tools"])
        if r.get("id") == 3:
            assert r["result"]["isError"] is True, "未知工具应 isError"
    assert lines[0]["result"]["serverInfo"]["name"] == SERVER_INFO["name"]
    print("MCP_SELFTEST PASS tools=%d" % tools_n)


if __name__ == "__main__":
    if "--selftest" in sys.argv:
        selftest()
    else:
        serve_stdio()
