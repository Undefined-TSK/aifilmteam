#!/usr/bin/env python3
"""
ACE-Step v1.5 本地 BGM 生成客户端（ComfyUI 0.37.2 原生节点 API 化）
作曲岗工具：tag 驱动纯音乐/歌曲生成，中文歌词支持，替代程序合成 BGM

用法：
  python acestep_client.py status
  python acestep_client.py generate <project_path> <output_name>
      --tags "ambient, piano, slow tempo" [--lyrics "[inst]"] [--duration 30]
      [--bpm 72] [--timesig 4] [--language zh] [--keyscale "C minor"]
      [--seed N] [--steps 8] [--cfg 1.5] [--no-audio-codes] [--subdir audio/bgm]

引擎参数说明：
  - turbo AIO 模型：steps=8 cfg=1.5 为推荐档（蒸馏版少步快出）
  - generate_audio_codes=True 走 LLM 音频码增强（质量↑速度↓），纯音乐可关
  - lyrics="[inst]" 表示纯音乐；有歌词时写实际歌词文本
  - 输出 44.1kHz 立体声（flac），经 ComfyUI audio/ 前缀落盘后下载到项目目录
"""
import argparse
import json
import random
import sys
import time
from datetime import datetime
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
# vram_lock 全引擎接入（R0-T6）：ACE-Step 本地推理经 ComfyUI 执行，生成期间独占显存锁
try:
    from vram_lock import vram_lock as _vram_lock
except Exception:  # 锁模块不可用时降级为 no-op
    import contextlib as _cl

    @_cl.contextmanager
    def _vram_lock(*a, **k):
        yield
from comfyui_client import (
    check_status,
    download_output,
    poll_history,
    submit_workflow,
)

CHECKPOINT = "ace_step_1.5_turbo_aio.safetensors"
TIMEOUT_SEC = 600


def check_models():
    models = Path(__file__).parent.parent / "comfyui" / "ComfyUI_windows_portable" / "ComfyUI" / "models"
    p = models / "checkpoints" / CHECKPOINT
    if not p.exists() or p.stat().st_size < 8_000_000_000:
        return [f"checkpoints/{CHECKPOINT}"]
    return []


def build_workflow(a):
    positive = {
        "class_type": "TextEncodeAceStepAudio1.5",
        "inputs": {
            "clip": ["10", 1],
            "tags": a.tags,
            "lyrics": a.lyrics,
            "seed": a.seed,
            "bpm": a.bpm,
            "duration": a.duration,
            "timesignature": str(a.timesig),
            "language": a.language,
            "keyscale": a.keyscale,
            "generate_audio_codes": not a.no_audio_codes,
            "cfg_scale": 2.0,
            "temperature": 0.85,
            "top_p": 0.9,
            "top_k": 0,
            "min_p": 0.0,
        },
    }
    negative = dict(positive)
    negative["inputs"] = {**positive["inputs"], "tags": "", "lyrics": ""}
    return {
        "10": {"class_type": "CheckpointLoaderSimple", "inputs": {"ckpt_name": CHECKPOINT}},
        "6": positive,
        "7": negative,
        "5": {"class_type": "EmptyAceStep1.5LatentAudio", "inputs": {"seconds": a.duration, "batch_size": 1}},
        "3": {"class_type": "KSampler", "inputs": {
            "seed": a.seed, "steps": a.steps, "cfg": a.cfg,
            "sampler_name": "euler", "scheduler": "normal", "denoise": 1.0,
            "model": ["10", 0], "positive": ["6", 0], "negative": ["7", 0],
            "latent_image": ["5", 0],
        }},
        "8": {"class_type": "VAEDecodeAudio", "inputs": {"samples": ["3", 0], "vae": ["10", 2]}},
        "9": {"class_type": "SaveAudio", "inputs": {"audio": ["8", 0], "filename_prefix": "audio/acestep"}},
    }


def generate_music(project_path, output_name, a):
    start = time.time()
    status = check_status()
    if status["status"] != "online":
        return {"error": f"ComfyUI 离线: {status.get('error', 'unknown')}"}
    missing = check_models()
    if missing:
        return {"error": "模型未就位（下载中或不完整）", "missing": missing}
    if a.seed is None:
        a.seed = random.randint(0, 2**32 - 1)

    wf = build_workflow(a)
    with _vram_lock("acestep", wait_sec=1800):  # R0-T6：生成期间独占显存锁
        prompt_id, number = submit_workflow(wf)
        entry = poll_history(prompt_id, timeout_sec=TIMEOUT_SEC)
    if entry.get("status", {}).get("status_str") == "error":
        msgs = [m for m in entry.get("status", {}).get("messages", []) if m[0] == "execution_error"]
        return {"error": "音频生成失败", "detail": msgs[:1]}

    out_dir = Path(project_path) / a.subdir
    file_path, comfy_filename = download_output(entry, out_dir, output_name)
    return {
        "status": "done",
        "prompt_id": prompt_id,
        "queue_number": number,
        "file_path": file_path,
        "comfyui_filename": comfy_filename,
        "elapsed_sec": round(time.time() - start, 1),
        "params": {
            "engine": "ace_step_1.5_turbo",
            "tags": a.tags,
            "lyrics": a.lyrics,
            "seed": a.seed,
            "bpm": a.bpm,
            "duration": a.duration,
            "timesignature": str(a.timesig),
            "language": a.language,
            "keyscale": a.keyscale,
            "audio_codes": not a.no_audio_codes,
            "steps": a.steps,
            "cfg": a.cfg,
        },
        "generated_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
    }


def main():
    parser = argparse.ArgumentParser(description="ACE-Step v1.5 本地 BGM 生成客户端")
    sub = parser.add_subparsers(dest="cmd", required=True)
    sub.add_parser("status")
    g = sub.add_parser("generate")
    g.add_argument("project_path")
    g.add_argument("output_name")
    g.add_argument("--tags", default="ambient, piano, slow tempo, rainy night mood, emotional, minimalist")
    g.add_argument("--lyrics", default="[inst]")
    g.add_argument("--duration", type=float, default=30)
    g.add_argument("--bpm", type=int, default=72)
    g.add_argument("--timesig", type=int, default=4)
    g.add_argument("--language", default="zh")
    g.add_argument("--keyscale", default="C minor")
    g.add_argument("--seed", type=int, default=None)
    g.add_argument("--steps", type=int, default=8)
    g.add_argument("--cfg", type=float, default=1.5)
    g.add_argument("--no-audio-codes", action="store_true")
    g.add_argument("--subdir", default="audio/bgm")
    args = parser.parse_args()

    if args.cmd == "status":
        out = check_status()
        out["missing_models"] = check_models()
        print(json.dumps(out, ensure_ascii=False))
    else:
        print(json.dumps(generate_music(args.project_path, args.output_name, args), ensure_ascii=False))


if __name__ == "__main__":
    main()
