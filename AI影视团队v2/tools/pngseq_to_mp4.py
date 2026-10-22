"""
R4-L1 白模 PNG 序列 -> mp4（VACE 输入）
- 读：PIL（归档 python 的 cv2 缺 PNG 解码后端，故用 PIL 读）
- 写：cv2.VideoWriter(mp4v, 24fps)；PIL 读为 RGB，直接写入使 decord/imageio 读出 RGB 一致
"""
import os, glob, sys
from pathlib import Path

import numpy as np
from PIL import Image
import cv2

# 维度25：路径改由 config/paths.py 中心化推导（原为字面量 D:/AI影视团队v2/...，已随新根迁移断链）
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from config.paths import ROOT  # noqa: E402

_SHOTS = ROOT / "blender" / "shots" / "r4_l1"
RGB_DIR = str(_SHOTS / "rgb")
OUT = str(_SHOTS / "blockout.mp4")
FPS = 24

def main():
    fs = sorted(glob.glob(os.path.join(RGB_DIR, "*.png")))
    if not fs:
        print("NO_FRAMES"); sys.exit(1)
    img = np.array(Image.open(fs[0]))
    h, w = img.shape[:2]
    vw = cv2.VideoWriter(OUT, cv2.VideoWriter_fourcc(*"mp4v"), FPS, (w, h))
    for f in fs:
        vw.write(np.array(Image.open(f)))  # RGB 写入，decord 读出 RGB 一致
    vw.release()
    print("MP4_DONE", os.path.getsize(OUT), "bytes", len(fs), "frames", (w, h))

if __name__ == "__main__":
    main()
