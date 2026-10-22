#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
ComfyUI 图像生成工具 — 对接本地 ComfyUI（默认 http://127.0.0.1:8188）

构造 SD1.5 文生图 workflow，轮询 /history 取图，保存至项目资产目录，
并联动预算管理（生成前检查 + 生成后扣减）。这是 CINEAST MVP 的"生成工具1个"。

用法：
  python comfyui_generator.py generate <project_path> <asset_type> <asset_name> <prompt>
        [--negative NEG] [--seed N] [--steps N] [--cfg F]
        [--width W] [--height H] [--cost C] [--model M] [--no-budget]

  asset_type: character | scene | storyboard | video
  asset_name: 资产名（如 雨夜少女、雨夜街道）
  prompt:     正向提示词
  --cost:     本次生成消耗的点数（默认 10，对应 SDXL 图像约 10 点/张）
  --no-budget: 跳过预算检查（仅本地调试用）

输出 JSON（stdout）：
  {status:"generated", asset_type, asset_name, image_path, web_path, seed, params, cost, budget}
  {status:"budget_blocked", message, remaining}
  {status:"error", message}
"""

import sys
import os
import io
import json
import uuid
import argparse
import urllib.request
import urllib.error
from datetime import datetime
from pathlib import Path

# vram_lock 全引擎接入（R0-T6）：ComfyUI GPU 生成期间独占显存锁（queue→wait_image）
sys.path.insert(0, str(Path(__file__).parent))
try:
    from vram_lock import vram_lock as _vram_lock
except Exception:  # 锁模块不可用时降级为 no-op
    import contextlib as _cl

    @_cl.contextmanager
    def _vram_lock(*a, **k):
        yield

# ============================================================
# 配置
# ============================================================

COMFYUI_URL = os.environ.get("COMFYUI_URL", "http://127.0.0.1:8188").rstrip("/")
# 不把 checkpoint 文件名写死：引擎统一为 D 盘 portable ComfyUI（8188），
# 模型集含 sd_xl_base(SDXL)/DreamShaper_8(SD1.5)/ace_step，写死必在一边失败。
# 留空 = 用 resolve_model() 按引擎实际能力自动挑（SDXL 优先）；
# 也可用环境变量 COMFYUI_MODEL 或 --model 显式指定。
COMFYUI_MODEL = os.environ.get("COMFYUI_MODEL", "").strip()
# 自动挑选时的偏好顺序
MODEL_PREFERENCE = (
    "sd_xl_base_1.0.safetensors",
    "sdxl",
    "sd_xl",
    "v1-5-pruned-emaonly-fp16.safetensors",
)
# 各模型族的采样参数；sdxl 一组取自项目内已实配的 comfyui/sdxl_txt2img_fixed.json
PRESETS = {
    "sdxl": {"steps": 30, "cfg": 7.5, "sampler_name": "dpmpp_2m",
             "scheduler": "karras", "width": 1024, "height": 1024},
    "sd15": {"steps": 25, "cfg": 7.0, "sampler_name": "euler",
             "scheduler": "normal", "width": 512, "height": 512},
}
DEFAULT_PRESET = os.environ.get("COMFYUI_PRESET", "sdxl")

# 资产类型 -> 目录名（与 projects/<项目>/assets/ 结构对应）
TYPE_DIR = {
    "character": "characters",
    "scene": "scenes",
    "storyboard": "storyboards",
    "video": "videos",
}

# 预算工具（同目录）
BUDGET_SCRIPT = Path(__file__).parent / "budget_manager.py"

HTTP_TIMEOUT = 120  # 单张生成最长等待（秒）


# ============================================================
# 通用 HTTP（仅用标准库，避免额外依赖）
# ============================================================

def _http_json(url, data=None, method="GET", timeout=HTTP_TIMEOUT):
    req = urllib.request.Request(url, data=data, method=method)
    if data is not None:
        req.add_header("Content-Type", "application/json")
    with urllib.request.urlopen(req, timeout=timeout) as resp:
        return json.loads(resp.read().decode("utf-8"))


def _http_bytes(url, timeout=HTTP_TIMEOUT):
    req = urllib.request.Request(url)
    with urllib.request.urlopen(req, timeout=timeout) as resp:
        return resp.read()


# ============================================================
# ComfyUI 交互
# ============================================================

def _engine_online(timeout=4):
    """探测引擎（COMFYUI_URL）是否已在监听。"""
    try:
        with urllib.request.urlopen(f"{COMFYUI_URL}/system_stats", timeout=timeout) as r:
            return True
    except Exception:
        return False


def _ensure_engine(wait_sec=180):
    """引擎不在线时，静默后台拉起归档区 portable ComfyUI 并等待在线。

    复用 comfyui_start.py 的路径推导与启动方式，不设开机自启——
    首次真正用到引擎时才拉起（用户要求「代码要用的时候自行静默启动」）。
    已在线则立即返回，不做任何事（幂等）。
    """
    if _engine_online():
        return True
    try:
        import subprocess
        import time
        from pathlib import Path

        start_path = Path(__file__).resolve().parent / "comfyui_start.py"
        if not start_path.exists():
            return False

        # 1) 启动前检查显存锁纪律（静默，失败不影响启动）
        try:
            sys.path.insert(0, str(Path(__file__).resolve().parent))
            from vram_lock import status
            holder = status().get("holder")
            if holder and not holder.get("released"):
                print(f"[generator] ⚠ 显存锁被占用 owner={holder.get('owner')} —— D23 分时纪律：错峰提交",
                      file=sys.stderr)
        except Exception:
            pass

        # 2) 后台静默拉起 portable（隐藏窗口、不阻塞），沿用与 comfyui_start.py 一致的调用方式
        py = sys.executable
        print(f"[generator] 引擎离线，静默拉起归档区 portable ComfyUI ...", file=sys.stderr)
        CREATE_NO_WINDOW = 0x08000000
        subprocess.Popen([py, str(start_path), "--wait"],
                         stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL,
                         creationflags=CREATE_NO_WINDOW)

        # 3) 等待在线（最多 wait_sec 秒），幂等返回
        deadline = time.time() + wait_sec
        while time.time() < deadline:
            if _engine_online():
                print(f"[generator] 引擎已在线: {COMFYUI_URL}", file=sys.stderr)
                return True
            time.sleep(3)
    except Exception as e:
        print(f"[generator] 自动拉起引擎失败: {e}", file=sys.stderr)
    return _engine_online()


def build_workflow(prompt, negative, seed, steps, cfg, width, height, model,
                   sampler_name="euler", scheduler="normal"):
    """构造文生图 workflow（SDXL / SD1.5 通用）

    sampler_name / scheduler 由模型 preset 给出：SDXL 用实测可用的
    dpmpp_2m + karras，SD1.5 沿用 euler + normal。
    """
    prefix = "cineast"
    return {
        "4": {
            "class_type": "CheckpointLoaderSimple",
            "inputs": {"ckpt_name": model},
        },
        "5": {
            "class_type": "EmptyLatentImage",
            "inputs": {"width": width, "height": height, "batch_size": 1},
        },
        "6": {
            "class_type": "CLIPTextEncode",
            "inputs": {"text": prompt, "clip": ["4", 1]},
        },
        "7": {
            "class_type": "CLIPTextEncode",
            "inputs": {"text": negative, "clip": ["4", 1]},
        },
        "3": {
            "class_type": "KSampler",
            "inputs": {
                "seed": seed,
                "steps": steps,
                "cfg": cfg,
                "sampler_name": sampler_name,
                "scheduler": scheduler,
                "denoise": 1.0,
                "model": ["4", 0],
                "positive": ["6", 0],
                "negative": ["7", 0],
                "latent_image": ["5", 0],
            },
        },
        "8": {
            "class_type": "VAEDecode",
            "inputs": {"samples": ["3", 0], "vae": ["4", 2]},
        },
        "9": {
            "class_type": "SaveImage",
            "inputs": {"images": ["8", 0], "filename_prefix": prefix},
        },
    }


def list_checkpoints():
    """返回引擎实际可用的 checkpoint 列表；引擎不可达时抛异常。"""
    if not _ensure_engine():
        raise RuntimeError(
            f"引擎 {COMFYUI_URL} 无法连接，且自动拉起失败；"
            "请手动运行：python tools/comfyui_start.py --wait"
        )
    info = _http_json(f"{COMFYUI_URL}/object_info/CheckpointLoaderSimple", timeout=15)
    node = info.get("CheckpointLoaderSimple") or {}
    required = (node.get("input") or {}).get("required") or {}
    field = required.get("ckpt_name") or []
    if field and isinstance(field[0], (list, tuple)):
        return list(field[0])
    return []


def _preset_for(model_name):
    return "sdxl" if "xl" in str(model_name).lower() else "sd15"


def resolve_model(requested=None):
    """解析出 (model, preset_name, available)。

    优先级：显式参数 > COMFYUI_MODEL 环境变量 > 引擎自检（MODEL_PREFERENCE 顺序）。
    请求了引擎上没有的模型时抛异常并列出可用值——不再让 ComfyUI 回一个
    含糊的 400，也不再静默退回到别的分辨率。
    """
    available = list_checkpoints()
    want = (requested or COMFYUI_MODEL or "").strip()
    if want:
        if available and want not in available:
            raise RuntimeError(
                f"引擎 {COMFYUI_URL} 上没有模型 {want}；可用模型: {available}"
            )
        return want, _preset_for(want), available
    for pref in MODEL_PREFERENCE:
        hits = [m for m in available if pref.lower() in m.lower()]
        if hits:
            return hits[0], _preset_for(hits[0]), available
    raise RuntimeError(
        f"引擎 {COMFYUI_URL} 上没有任何可用 checkpoint；"
        "请启动 D 盘 portable ComfyUI（python tools/comfyui_start.py --wait），多次失败可设 COMFYUI_URL 指定"
    )


def comfyui_queue(workflow):
    """提交 workflow 到 ComfyUI，返回 prompt_id"""
    payload = json.dumps({"prompt": workflow, "client_id": str(uuid.uuid4())}).encode("utf-8")
    result = _http_json(f"{COMFYUI_URL}/prompt", data=payload, method="POST", timeout=30)
    return result["prompt_id"]


def comfyui_wait_image(prompt_id):
    """轮询 /history 直到该 prompt 完成，返回输出图片的 {filename, subfolder, type}"""
    import time
    deadline = time.time() + HTTP_TIMEOUT
    while time.time() < deadline:
        try:
            hist = _http_json(f"{COMFYUI_URL}/history/{prompt_id}", timeout=10)
        except (urllib.error.HTTPError, urllib.error.URLError):
            hist = {}
        entry = hist.get(prompt_id)
        if entry and "outputs" in entry:
            outputs = entry["outputs"]
            # SaveImage 节点（"9"）的输出
            for node_out in outputs.values():
                imgs = node_out.get("images")
                if imgs:
                    return imgs[0]
        time.sleep(2)
    raise TimeoutError(f"ComfyUI 生成超时（>{HTTP_TIMEOUT}s），prompt_id={prompt_id}")


def comfyui_fetch_image(meta):
    """根据 /history 的 image meta 下载图片字节"""
    params = urllib.parse.urlencode({
        "filename": meta["filename"],
        "subfolder": meta.get("subfolder", ""),
        "type": meta.get("type", "output"),
    })
    return _http_bytes(f"{COMFYUI_URL}/view?{params}")


import urllib.parse  # noqa: E402  (放在文件中部仅为就近使用)


# ============================================================
# 预算联动
# ============================================================

def budget_check(project_path, amount):
    """返回 (can_spend, info_dict)"""
    import subprocess
    try:
        out = subprocess.run(
            [sys.executable, str(BUDGET_SCRIPT), "check", project_path, str(amount)],
            capture_output=True, text=True, timeout=30,
        ).stdout
        info = json.loads(out)
        return bool(info.get("can_spend", False)), info
    except Exception as e:
        return True, {"warning": f"预算检查失败，放行: {e}"}


def _read_budget_total(project_path):
    """直接读取预算总额（budget_check 的返回不含 total_budget）"""
    p = Path(project_path) / "budget.json"
    if not p.exists():
        return 0
    try:
        return float(json.loads(p.read_text(encoding="utf-8")).get("total_budget", 0))
    except Exception:
        return 0


def budget_spend(project_path, amount, desc, asset_name):
    import subprocess
    try:
        out = subprocess.run(
            [sys.executable, str(BUDGET_SCRIPT), "spend", project_path,
             str(amount), desc, asset_name],
            capture_output=True, text=True, timeout=30,
        ).stdout
        return json.loads(out)
    except Exception as e:
        return {"status": "error", "message": f"预算扣减失败: {e}"}


# ============================================================
# 主流程
# ============================================================

def next_version_path(assets_dir, asset_type, asset_name):
    """生成 assets/<type_dir>/<name>_vN.png 路径，N 取当前最大+1"""
    type_dir = TYPE_DIR.get(asset_type, asset_type + "s")
    target_dir = assets_dir / type_dir
    target_dir.mkdir(parents=True, exist_ok=True)
    existing = [p.name for p in target_dir.glob(f"{asset_name}_v*.png")]
    max_n = 0
    for name in existing:
        try:
            n = int(name[len(asset_name) + 2: name.rfind(".png")])
            max_n = max(max_n, n)
        except ValueError:
            continue
    n = max_n + 1
    return target_dir / f"{asset_name}_v{n}.png", n


def generate(project_path, asset_type, asset_name, prompt,
             negative="", seed=None, steps=None, cfg=None,
             width=None, height=None, cost=10, model=None,
             sampler_name=None, scheduler=None, skip_budget=False):
    project_path = Path(project_path)
    if asset_type not in TYPE_DIR:
        return {"status": "error", "message": f"未知 asset_type: {asset_type}"}
    if not project_path.exists():
        return {"status": "error", "message": f"项目不存在: {project_path}"}

    # 0) 引擎自检：按引擎真实能力决定模型与分辨率
    try:
        model, preset_name, available = resolve_model(model)
    except Exception as e:
        return {"status": "error", "engine": COMFYUI_URL,
                "message": f"ComfyUI 引擎检查失败: {e}"}
    preset = PRESETS.get(preset_name, PRESETS[DEFAULT_PRESET])
    # 显式传参优先，否则用该模型族的 preset（修掉“SDXL 被 512 默认值拖累”）
    steps = preset["steps"] if steps is None else steps
    cfg = preset["cfg"] if cfg is None else cfg
    width = preset["width"] if width is None else width
    height = preset["height"] if height is None else height
    sampler_name = sampler_name or preset["sampler_name"]
    scheduler = scheduler or preset["scheduler"]

    # 1) 预算检查
    budget_before = None
    total = 0
    if not skip_budget:
        can_spend, binfo = budget_check(str(project_path), cost)
        budget_before = binfo
        total = _read_budget_total(project_path)
        if total > 0 and not can_spend:
            return {
                "status": "budget_blocked",
                "message": f"预算不足，需 {cost}，剩余 {binfo.get('remaining')}",
                "remaining": binfo.get("remaining"),
            }

    # 2) 提交生成
    if seed is None:
        seed = (uuid.uuid4().int >> 8) % (2 ** 31)
    workflow = build_workflow(prompt, negative, seed, steps, cfg, width, height, model,
                             sampler_name=sampler_name, scheduler=scheduler)
    try:
        with _vram_lock("comfyui-gen", wait_sec=1800):  # R0-T6：生成期间独占显存锁
            prompt_id = comfyui_queue(workflow)
            meta = comfyui_wait_image(prompt_id)
            img_bytes = comfyui_fetch_image(meta)
    except Exception as e:
        return {"status": "error", "engine": COMFYUI_URL, "model": model,
                "message": f"ComfyUI 生成失败: {e}"}

    # 3) 落盘到项目资产目录
    assets_dir = project_path / "assets"
    save_path, version = next_version_path(assets_dir, asset_type, asset_name)
    save_path.write_bytes(img_bytes)
    web_path = f"/project-assets/{TYPE_DIR[asset_type]}/{save_path.name}"

    # 4) 预算扣减
    budget_after = None
    if not skip_budget and total and total > 0:
        budget_after = budget_spend(
            str(project_path), cost, f"生成 {asset_type}/{asset_name}", asset_name
        )

    return {
        "status": "generated",
        "asset_type": asset_type,
        "asset_name": asset_name,
        "version": version,
        "image_path": str(save_path),
        "web_path": web_path,
        "seed": seed,
        "params": {
            "prompt": prompt,
            "negative": negative,
            "seed": seed,
            "steps": steps,
            "cfg": cfg,
            "width": width,
            "height": height,
            "model": model,
            "preset": preset_name,
            "sampler_name": sampler_name,
            "scheduler": scheduler,
            "engine": COMFYUI_URL,
        },
        "cost": cost,
        "budget_before": budget_before,
        "budget_after": budget_after,
        "available_checkpoints": available,
        "saved_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
    }


def main():
    parser = argparse.ArgumentParser(description="ComfyUI 图像生成工具")
    sub = parser.add_subparsers(dest="cmd", required=True)

    p_gen = sub.add_parser("generate", help="生成一张图")
    p_gen.add_argument("project_path")
    p_gen.add_argument("asset_type")
    p_gen.add_argument("asset_name")
    p_gen.add_argument("prompt")
    p_gen.add_argument("--negative", default="")
    p_gen.add_argument("--seed", type=int, default=None)
    # 默认 None = 交给模型 preset 决定，避免固定的 512/25/7.0 压过 SDXL 配方
    p_gen.add_argument("--steps", type=int, default=None)
    p_gen.add_argument("--cfg", type=float, default=None)
    p_gen.add_argument("--width", type=int, default=None)
    p_gen.add_argument("--height", type=int, default=None)
    p_gen.add_argument("--cost", type=float, default=10)
    p_gen.add_argument("--model", default=None)
    p_gen.add_argument("--sampler", default=None)
    p_gen.add_argument("--scheduler", default=None)
    p_gen.add_argument("--no-budget", action="store_true")

    args = parser.parse_args()
    if args.cmd == "generate":
        result = generate(
            args.project_path, args.asset_type, args.asset_name, args.prompt,
            negative=args.negative, seed=args.seed, steps=args.steps, cfg=args.cfg,
            width=args.width, height=args.height, cost=args.cost,
            model=args.model, sampler_name=args.sampler, scheduler=args.scheduler,
            skip_budget=args.no_budget,
        )
        print(json.dumps(result, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
