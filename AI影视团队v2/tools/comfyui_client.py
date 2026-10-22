#!/usr/bin/env python3
"""
ComfyUI API 客户端工具
将 SDXL 工作流提交给 ComfyUI 生成图片，下载到项目资产目录

用法：
  python comfyui_client.py status                                          # 检查 ComfyUI 状态
  python comfyui_client.py generate <project_path> <output_name>           # 生成图片
      [--prompt "..."] [--negative "..."] [--seed N]
      [--width N] [--height N] [--steps N] [--cfg F]

输出 JSON：{status, prompt_id, file_path, elapsed_sec, params}
"""

import argparse
import copy
import json
import os
import random
import sys
import time
import urllib.error
import urllib.request
import uuid
from datetime import datetime
from pathlib import Path

# vram_lock 全引擎接入（R0-T6）：ComfyUI GPU 生成全程持锁（submit→poll 期间独占显存配额）
try:
    sys.path.insert(0, str(Path(__file__).parent))
    from vram_lock import vram_lock as _vram_lock
except Exception:  # 锁模块不可用时降级为 no-op（不阻塞生成）
    import contextlib as _cl

    @_cl.contextmanager
    def _vram_lock(*a, **k):
        yield

# 维度33：端口不再写死，支持 COMFYUI_URL 环境变量覆盖（默认对齐 config/settings.yaml ports.comfyui）
COMFYUI_URL = os.environ.get("COMFYUI_URL", "http://127.0.0.1:8188")
WORKFLOW_TEMPLATE = Path(__file__).parent.parent / "comfyui" / "sdxl_txt2img_fixed.json"
T2V_TEMPLATE = Path(__file__).parent.parent / "comfyui" / "animatediff_t2v.json"
I2V_TEMPLATE = Path(__file__).parent.parent / "comfyui" / "animatediff_i2v.json"
TIMEOUT_POLL_SEC = 300   # 单次生成最长等待 5 分钟
TIMEOUT_POLL_VIDEO_SEC = 600
POLL_INTERVAL_SEC = 2

# 节点ID映射（与 sdxl_txt2img_fixed.json 对应）
NODE_SAMPLER = "3"
NODE_CHECKPOINT = "4"
NODE_LATENT = "5"
NODE_POS = "6"
NODE_NEG = "7"
NODE_SAVE = "9"


def http_get(url, timeout=10):
    with urllib.request.urlopen(url, timeout=timeout) as resp:
        return resp.read()


def check_status():
    """检查 ComfyUI 是否在线"""
    try:
        data = json.loads(http_get(f"{COMFYUI_URL}/system_stats"))
        device = data.get("devices", [{}])[0]
        return {
            "status": "online",
            "comfyui_version": data.get("system", {}).get("comfyui_version"),
            "gpu": device.get("name"),
            "vram_free_mb": round(device.get("vram_free", 0) / 1024 / 1024),
            "vram_total_mb": round(device.get("vram_total", 0) / 1024 / 1024),
        }
    except Exception as e:
        return {"status": "offline", "error": str(e)}


def load_template():
    if not WORKFLOW_TEMPLATE.exists():
        raise FileNotFoundError(f"工作流模板不存在: {WORKFLOW_TEMPLATE}")
    return json.loads(WORKFLOW_TEMPLATE.read_text(encoding="utf-8"))


def build_prompt(template, args):
    """用命令行参数覆盖模板默认值"""
    wf = copy.deepcopy(template)
    wf[NODE_POS]["inputs"]["text"] = args.prompt
    wf[NODE_NEG]["inputs"]["text"] = args.negative
    wf[NODE_LATENT]["inputs"]["width"] = args.width
    wf[NODE_LATENT]["inputs"]["height"] = args.height
    wf[NODE_SAMPLER]["inputs"]["steps"] = args.steps
    wf[NODE_SAMPLER]["inputs"]["cfg"] = args.cfg
    if args.seed is None:
        args.seed = random.randint(0, 2**32 - 1)
    wf[NODE_SAMPLER]["inputs"]["seed"] = args.seed
    return wf


def submit_workflow(wf):
    """提交工作流到 /prompt，返回 prompt_id"""
    client_id = uuid.uuid4().hex
    payload = json.dumps({"prompt": wf, "client_id": client_id}).encode("utf-8")
    req = urllib.request.Request(
        f"{COMFYUI_URL}/prompt",
        data=payload,
        headers={"Content-Type": "application/json"},
    )
    with urllib.request.urlopen(req, timeout=15) as resp:
        data = json.loads(resp.read())
    if "prompt_id" not in data:
        raise RuntimeError(f"提交失败: {data}")
    return data["prompt_id"], data.get("number")


def poll_history(prompt_id, timeout_sec=TIMEOUT_POLL_SEC):
    """轮询 /history/{prompt_id} 直到完成，返回历史记录"""
    deadline = time.time() + timeout_sec
    while time.time() < deadline:
        try:
            data = json.loads(http_get(f"{COMFYUI_URL}/history/{prompt_id}"))
        except urllib.error.HTTPError:
            time.sleep(POLL_INTERVAL_SEC)
            continue
        if prompt_id in data:
            entry = data[prompt_id]
            status = entry.get("status", {})
            if status.get("completed") or status.get("status_str") == "error":
                return entry
        time.sleep(POLL_INTERVAL_SEC)
    raise TimeoutError(f"生成超时（{timeout_sec}s）: {prompt_id}")


def download_output(entry, out_dir, output_name):
    """从历史记录提取输出文件并下载（兼容图片 images、视频 gifs、音频 audio 三种输出）"""
    outputs = entry.get("outputs", {})
    for node_output in outputs.values():
        files = list(node_output.get("images", [])) + list(node_output.get("gifs", [])) + list(node_output.get("audio", []))
        for img in files:
            if img.get("type") != "output":
                continue
            filename = img["filename"]
            subfolder = img.get("subfolder", "")
            url = (
                f"{COMFYUI_URL}/view"
                f"?filename={urllib.request.quote(filename)}"
                f"&subfolder={urllib.request.quote(subfolder)}"
                f"&type=output"
            )
            content = http_get(url, timeout=120)
            out_dir.mkdir(parents=True, exist_ok=True)
            stem = output_name.replace(" ", "_")
            suffix = Path(filename).suffix or ".png"
            out_path = out_dir / f"{stem}{suffix}"
            out_path.write_bytes(content)
            return str(out_path), filename
    raise RuntimeError("历史记录中没有输出文件")


def generate(project_path, output_name, args):
    """完整生成流程：提交 → 轮询 → 下载"""
    start = time.time()

    status = check_status()
    if status["status"] != "online":
        return {"error": f"ComfyUI 离线: {status.get('error', 'unknown')}"}

    template = load_template()
    wf = build_prompt(template, args)
    with _vram_lock("comfyui-sdxl", wait_sec=1800):  # R0-T6：生成期间独占显存锁
        prompt_id, number = submit_workflow(wf)
        entry = poll_history(prompt_id)
    if entry.get("status", {}).get("status_str") == "error":
        msgs = [m for m in entry.get("status", {}).get("messages", []) if m[0] == "execution_error"]
        return {"error": "生成失败", "detail": msgs[:1]}

    out_dir = Path(project_path) / "assets"
    file_path, comfy_filename = download_output(entry, out_dir, output_name)

    return {
        "status": "done",
        "prompt_id": prompt_id,
        "queue_number": number,
        "file_path": file_path,
        "comfyui_filename": comfy_filename,
        "elapsed_sec": round(time.time() - start, 1),
        "params": {
            "prompt": args.prompt,
            "negative": args.negative,
            "seed": args.seed,
            "width": args.width,
            "height": args.height,
            "steps": args.steps,
            "cfg": args.cfg,
        },
        "generated_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
    }


def upload_image(image_path):
    """上传锚点图到 ComfyUI input 目录，返回远端文件名"""
    path = Path(image_path)
    if not path.exists():
        raise FileNotFoundError(f"锚点图不存在: {path}")
    boundary = f"----cineast{uuid.uuid4().hex}"
    body = []
    body.append(f"--{boundary}\r\n".encode())
    body.append(
        f'Content-Disposition: form-data; name="image"; filename="{path.name}"\r\n\r\n'.encode()
    )
    body.append(path.read_bytes())
    body.append(f"\r\n--{boundary}--\r\n".encode())
    payload = b"".join(body)
    req = urllib.request.Request(
        f"{COMFYUI_URL}/upload/image",
        data=payload,
        headers={"Content-Type": f"multipart/form-data; boundary={boundary}"},
    )
    with urllib.request.urlopen(req, timeout=60) as resp:
        data = json.loads(resp.read())
    remote_name = data.get("name")
    if not remote_name:
        raise RuntimeError(f"上传失败: {data}")
    if data.get("subfolder"):
        remote_name = f"{data['subfolder']}/{remote_name}"
    return remote_name


def build_video_prompt(template, args, output_name, anchor_remote=None):
    """用命令行参数覆盖视频工作流模板默认值"""
    wf = copy.deepcopy(template)
    wf["6"]["inputs"]["text"] = args.prompt
    wf["7"]["inputs"]["text"] = args.negative
    wf["11"]["inputs"]["frame_rate"] = args.fps
    wf["11"]["inputs"]["filename_prefix"] = output_name.replace(" ", "_")
    if args.seed is None:
        args.seed = random.randint(0, 2**32 - 1)
    # t2v 模板采样器为节点3，i2v 模板采样器为节点9
    sampler = wf["9"] if "9" in wf else wf["3"]
    sampler["inputs"]["seed"] = args.seed
    if anchor_remote is not None:
        wf["1"]["inputs"]["image"] = anchor_remote
        wf["2"]["inputs"]["width"] = args.width
        wf["2"]["inputs"]["height"] = args.height
        sampler["inputs"]["denoise"] = args.denoise
        wf["8"]["inputs"]["amount"] = args.frames
    else:
        wf["5"]["inputs"]["width"] = args.width
        wf["5"]["inputs"]["height"] = args.height
        wf["5"]["inputs"]["batch_size"] = args.frames
    return wf


def generate_video(project_path, output_name, args):
    """视频生成流程：上传锚点（i2v）→ 提交 → 轮询 → 下载mp4"""
    start = time.time()

    status = check_status()
    if status["status"] != "online":
        return {"error": f"ComfyUI 离线: {status.get('error', 'unknown')}"}

    if args.mode == "i2v":
        template = json.loads(I2V_TEMPLATE.read_text(encoding="utf-8"))
        anchor_remote = upload_image(args.anchor)
    else:
        template = json.loads(T2V_TEMPLATE.read_text(encoding="utf-8"))
        anchor_remote = None

    wf = build_video_prompt(template, args, output_name, anchor_remote)
    prompt_id, number = submit_workflow(wf)

    entry = poll_history(prompt_id, timeout_sec=TIMEOUT_POLL_VIDEO_SEC)
    if entry.get("status", {}).get("status_str") == "error":
        msgs = [m for m in entry.get("status", {}).get("messages", []) if m[0] == "execution_error"]
        return {"error": "视频生成失败", "detail": msgs[:1]}

    out_dir = Path(project_path) / "shots"
    file_path, comfy_filename = download_output(entry, out_dir, output_name)

    return {
        "status": "done",
        "prompt_id": prompt_id,
        "queue_number": number,
        "file_path": file_path,
        "comfyui_filename": comfy_filename,
        "elapsed_sec": round(time.time() - start, 1),
        "params": {
            "mode": args.mode,
            "prompt": args.prompt,
            "anchor": args.anchor,
            "seed": args.seed,
            "width": args.width,
            "height": args.height,
            "frames": args.frames,
            "fps": args.fps,
            "denoise": args.denoise if args.mode == "i2v" else 1.0,
            "steps": 4,
            "cfg": 1.0,
        },
        "generated_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
    }


def main():
    parser = argparse.ArgumentParser(description="ComfyUI API 客户端")
    sub = parser.add_subparsers(dest="cmd", required=True)

    sub.add_parser("status")

    g = sub.add_parser("generate")
    g.add_argument("project_path")
    g.add_argument("output_name")
    g.add_argument("--prompt", default="cinematic photograph, dramatic lighting, intricate detail")
    g.add_argument("--negative", default="ugly, blurry, low quality, deformed, watermark")
    g.add_argument("--seed", type=int, default=None)
    g.add_argument("--width", type=int, default=1024)
    g.add_argument("--height", type=int, default=1024)
    g.add_argument("--steps", type=int, default=30)
    g.add_argument("--cfg", type=float, default=7.5)

    v = sub.add_parser("video")
    v.add_argument("project_path")
    v.add_argument("output_name")
    v.add_argument("--mode", choices=["t2v", "i2v"], default="i2v")
    v.add_argument("--prompt", default="subtle motion, cinematic")
    v.add_argument("--negative", default="")
    v.add_argument("--anchor", default=None, help="i2v锚点图路径")
    v.add_argument("--seed", type=int, default=None)
    v.add_argument("--width", type=int, default=704)
    v.add_argument("--height", type=int, default=384)
    v.add_argument("--frames", type=int, default=16)
    v.add_argument("--fps", type=int, default=8)
    v.add_argument("--denoise", type=float, default=0.65)

    args = parser.parse_args()
    if args.cmd == "status":
        print(json.dumps(check_status(), ensure_ascii=False))
    elif args.cmd == "generate":
        print(json.dumps(generate(args.project_path, args.output_name, args), ensure_ascii=False))
    elif args.cmd == "video":
        if args.mode == "i2v" and not args.anchor:
            parser.error("i2v 模式必须提供 --anchor 锚点图路径")
        print(json.dumps(generate_video(args.project_path, args.output_name, args), ensure_ascii=False))


if __name__ == "__main__":
    main()
