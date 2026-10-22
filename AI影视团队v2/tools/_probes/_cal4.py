"""一次性标定：哪种判据能把"已知2个真动效镜"与"已知16个静图+缓推镜"分开。用完删。
raw  = 直接帧差（v1 用它，误报 100% 真动）
dres = 稠密光流 − 全局仿射运动模型（robust 两次迭代）后幅值均值 → 画面内真实活动
dmove= 稠密光流幅值均值（含相机运动）
"""
import json
import subprocess
import sys
from pathlib import Path

import cv2
import numpy as np

try:
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
except Exception:
    pass

FF = (r"C:\Users\LZH\AppData\Local\Microsoft\WinGet\Packages"
      r"\Gyan.FFmpeg.Shared_Microsoft.Winget.Source_8wekyb3d8bbwe"
      r"\ffmpeg-8.1.2-full_build-shared\bin\ffmpeg.exe")
MEDIA = Path(sys.argv[1])
SHOTS = json.loads(Path(sys.argv[2]).read_text(encoding="utf-8"))
REAL = set((sys.argv[3] if len(sys.argv) > 3 else "3-3,4-1").split(","))
W, GAP, B = 480, 0.45, 12


def frame(t):
    raw = MEDIA.parent / f"k{int(t * 1000)}.raw"
    r = subprocess.run([FF, "-hide_banner", "-loglevel", "error", "-y", "-ss", f"{t:.3f}",
                        "-i", str(MEDIA), "-frames:v", "1", "-vf", f"scale={W}:-2",
                        "-pix_fmt", "gray", "-f", "rawvideo", str(raw)],
                       capture_output=True, text=True)
    if r.returncode != 0 or not raw.exists() or raw.stat().st_size == 0:
        raise RuntimeError(f"抽帧失败 @{t}: {r.stderr[-150:]}")
    h = raw.stat().st_size // W
    a = np.fromfile(raw, dtype=np.uint8).reshape(h, W)
    raw.unlink()
    return a


def global_affine_resid(u, v, A, mag):
    """对 u、v 各拟合一次全局仿射（xs,ys,1）；两次迭代剔除离群（>3MAD）后返回残余幅值图。"""
    keep = mag > 0.05
    ru = np.zeros_like(u)
    rv = np.zeros_like(v)
    if keep.sum() < 400:
        return None
    for _ in range(2):
        ku = np.linalg.lstsq(A[keep], u[keep], rcond=None)[0]
        kv = np.linalg.lstsq(A[keep], v[keep], rcond=None)[0]
        ru = u - (A @ ku).reshape(u.shape)
        rv = v - (A @ kv).reshape(v.shape)
        rmag = np.hypot(ru, rv)
        mad = np.median(rmag[keep]) + 1e-6
        keep = (rmag < mad * 3 + 0.05) & (mag > 0.05)
        if keep.sum() < 400:
            break
    return np.hypot(ru, rv)


def metrics(a0, a1):
    h, w = a0.shape
    raw = float(np.abs(a1.astype("int16") - a0.astype("int16")).mean())
    fl = cv2.calcOpticalFlowFarneback(a0, a1, None, 0.25, 3, 15, 3, 5, 1.2, 0)
    u, v = fl[..., 0].astype("float64"), fl[..., 1].astype("float64")
    mag = np.hypot(u, v)
    ys, xs = np.mgrid[0:h, 0:w]
    A = np.stack([xs.ravel(), ys.ravel(), np.ones(h * w)], 1).astype("float64")
    res = global_affine_resid(u.ravel(), v.ravel(), A, mag.ravel())
    dres = float(res.reshape(h, w)[B:h - B, B:w - B].mean()) if res is not None else raw
    core = (slice(B, h - B), slice(B, w - B))
    return {"raw": round(raw, 3), "dres": round(dres, 3),
            "dmove": round(float(mag[core].mean()), 3),
            "dp90": round(float(np.percentile(mag[core], 90)), 3)}


K = ["raw", "dres", "dmove", "dp90"]
rows = {}
print(f"{'镜':<6}{'真值':<5}" + "".join(f"{k:>9}" for k in K))
for name, t0 in sorted(SHOTS.items(), key=lambda kv: kv[1]):
    d = metrics(frame(t0 + 0.15), frame(t0 + 0.15 + GAP))
    rows[name] = d
    print(f"{name:<6}{'真动' if name in REAL else '静图':<5}" + "".join(f"{d[k]:>9.3f}" for k in K))

print("\n=== 可分性（真动下界 vs 静图上界）===")
for k in K:
    r = [rows[n][k] for n in rows if n in REAL]
    s = sorted(rows[n][k] for n in rows if n not in REAL)
    best = max(((sum(1 for n in REAL if rows[n][k] >= th)
                 + sum(1 for n in rows if n not in REAL and rows[n][k] < th), round(float(th), 2))
                for th in np.arange(0.02, 15.0, 0.02)))
    print(f"{k:<6} 静图上界={max(s):>7.3f}  真动下界={min(r):>7.3f}  "
          f"完全可分={'是' if min(r) > max(s) else '否'}  最优阈值={best[1]:.2f} 正确率={best[0]}/18")
(MEDIA.parent / "cal_verdict.json").write_text(json.dumps(rows, ensure_ascii=False, indent=1), encoding="utf-8")

