#!/usr/bin/env python3
"""dl_vace — 补齐 Wan2.1-VACE-1.3B 官方仓库权重（经 hf-mirror，断点续传）

2026-10-05（债务4）：本地 models/wan_vace_1.3b 两个大文件是下载中断残片
  - diffusion_pytorch_model.safetensors   本地 776MB / 完整 7,146,067,848
  - models_t5_umt5-xxl-enc-bf16.pth       本地 98.6MB / 完整 11,361,920,418
  - Wan2.1_VAE.pth / config.json / tokenizer 已完整，跳过
完成校验 = 两个大文件字节数与上表完全一致，否则报缺失清单。
"""
import os
import sys
from pathlib import Path

os.environ["HF_ENDPOINT"] = "https://hf-mirror.com"
os.environ["HF_HUB_DISABLE_XET"] = "1"

from huggingface_hub import snapshot_download

ROOT = Path(__file__).resolve().parents[1]
VACE_DIR = ROOT / "models" / "wan_vace_1.3b"

EXPECTED = {
    "diffusion_pytorch_model.safetensors": 7_146_067_848,
    "models_t5_umt5-xxl-enc-bf16.pth": 11_361_920_418,
    "Wan2.1_VAE.pth": 507_609_880,
}


def _missing():
    out = []
    for name, want in EXPECTED.items():
        p = VACE_DIR / name
        if not p.exists() or p.stat().st_size != want:
            out.append(f"{name}: {p.stat().st_size if p.exists() else 0}/{want}")
    return out


def main():
    miss = _missing()
    if not miss:
        print("VACE weights already complete", flush=True)
        return
    print("missing before download:", "; ".join(miss), flush=True)
    # hf-mirror 大文件偶发断流（实测 11.3GB 文件 3.2GB 处 IncompleteRead）；
    # 局部文件落在 .cache/huggingface/download/*.incomplete，重跑即字节级续传。
    for attempt in range(1, 6):
        try:
            snapshot_download(
                "Wan-AI/Wan2.1-VACE-1.3B",
                local_dir=VACE_DIR,
                allow_patterns=[
                    "*.json", "*.pth", "*.safetensors", "*.model", "LICENSE.txt",
                    "README.md", "google/*",
                ],
                max_workers=4,
            )
            break
        except Exception as exc:
            left = _missing()
            print(f"attempt {attempt} failed: {type(exc).__name__} {str(exc)[:160]}", flush=True)
            print("still missing:", "; ".join(left), flush=True)
            if attempt == 5:
                sys.exit(1)
            time.sleep(10)
    miss = _missing()
    if miss:
        print("STILL MISSING:", "; ".join(miss), flush=True)
        sys.exit(2)
    print("VACE weights complete: 16.4GB verified", flush=True)


if __name__ == "__main__":
    main()
