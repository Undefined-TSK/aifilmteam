#!/usr/bin/env python3
"""D1 P0 模型下载队列：ACE 完成后串行下载 Qwen3-VL-4B 与 MuseTalk 1.5 全套权重（经 hf-mirror）

2026-10-05（债务3）：旧接合点 D:\\ai_film_projects 已归档断链；目标目录收敛到
v2 根内 models/（Qwen3-VL、MuseTalk 为可选下游模型，未下载时相关工具自动报未就绪）。
"""
import os
import time
from pathlib import Path

os.environ["HF_ENDPOINT"] = "https://hf-mirror.com"
os.environ["HF_HUB_DISABLE_XET"] = "1"

from huggingface_hub import snapshot_download

ROOT = Path(__file__).resolve().parents[1]
ACE = ROOT / "models" / "ace_step_1.5_turbo_aio.safetensors"
QWEN_DIR = ROOT / "models" / "Qwen3-VL-4B-Instruct"
MT_DIR = ROOT / "models" / "musetalk"


def wait_ace():
    print("waiting for ACE ...", flush=True)
    while os.path.exists(str(ACE) + ".aria2"):
        time.sleep(20)
    print("ACE done", flush=True)


def qwen_complete():
    # 必须校验两个大权重分片实际存在，config.json 在而权重缺一半是既有踩坑场景
    d = os.path.join(QWEN_DIR, "model-0000%d-of-00002.safetensors")
    return all(os.path.exists(d % i) for i in (1, 2))


def dl_qwen():
    if qwen_complete():
        print("qwen already present", flush=True)
        return
    snapshot_download("Qwen/Qwen3-VL-4B-Instruct", local_dir=QWEN_DIR, max_workers=8)
    print("QWEN DONE", flush=True)


def dl_musetalk():
    marker = os.path.join(MT_DIR, "musetalkV15", "unet.pth")
    if os.path.exists(marker):
        print("musetalk weights already present", flush=True)
        return
    snapshot_download("TMElyralab/MuseTalk", local_dir=os.path.join(MT_DIR, "_raw"), max_workers=4)
    print("musetalk core DONE", flush=True)
    snapshot_download("stabilityai/sd-vae-ft-mse", local_dir=os.path.join(MT_DIR, "_raw_vae"),
                      allow_patterns=["config.json", "diffusion_pytorch_model.bin"])
    snapshot_download("openai/whisper-tiny", local_dir=os.path.join(MT_DIR, "_raw_whisper"),
                      allow_patterns=["config.json", "pytorch_model.bin", "preprocessor_config.json"])
    snapshot_download("yzd-v/DWPose", local_dir=os.path.join(MT_DIR, "_raw_dwpose"),
                      allow_patterns=["dw-ll_ucoco_384.pth"])
    snapshot_download("ByteDance/LatentSync", local_dir=os.path.join(MT_DIR, "_raw_syncnet"),
                      allow_patterns=["latentsync_syncnet.pt"])
    snapshot_download("ManyOtherFunctions/face-parse-bisent", local_dir=os.path.join(MT_DIR, "_raw_faceparse"),
                      allow_patterns=["79999_iter.pth", "resnet18-5c106cde.pth"])
    print("MUSETALK COMPONENTS DONE", flush=True)


if __name__ == "__main__":
    wait_ace()
    dl_qwen()
    dl_musetalk()
    print("ALL DOWNLOADS DONE", flush=True)
