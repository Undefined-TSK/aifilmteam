# -*- coding: utf-8 -*-
"""EXR/PNG 帧 -> VACE 控制条件图（R17 自研件 2，全管线唯一不可替代件）

纯标准库实现（zlib/struct/binascii），不依赖 PIL/numpy/cv2。

输入（二选一）：
  A. Blender 白模渲染 EXR（含 Z 深度通道，ZIP/无压缩扫描线格式）
  B. RGB PNG 帧 + 深度源（EXR-Z 或 Blender compositor 输出的灰度深度 PNG）

输出（VACE 可用控制条件图序列）：
  - 深度图：8bit 灰度 PNG，近=白(255) 远=黑(0)，--invert 可翻转
  - 线稿：  8bit 灰度 PNG，白底黑线（Sobel 阈值）

附带 frames_to_mp4(frame_dir, fps, out)：ffmpeg 封装，Wan/VACE 对齐 720P
（1280x720，libx264，yuv420p）。

用法：
  python exr_to_control.py depth   --in-dir <exr或深度png目录> --out <dir> [--invert]
  python exr_to_control.py lineart --in-dir <rgb png/exr目录>  --out <dir> [--thresh 24]
  python exr_to_control.py mp4     --frames <帧目录> --fps 24 --out clip.mp4
"""
import argparse
import glob
import math
import os
import struct
import sys
import zlib

# 维度25：ffmpeg 解析统一走 config/paths.py（完整构建优先，TRAE 精简版缺 matroska/libx264）
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from config.paths import ffmpeg as _ffmpeg  # noqa: E402

# ---------------- EXR 解析（单层、扫描线、ZIP/无压缩） ----------------

_PX_SIZE = {0: 4, 1: 2, 2: 4}   # UINT / HALF / FLOAT 字节数

_HALF_LUT = None


def _half_to_float_lut():
    """65536 项 half->float 查表（懒构建）。"""
    global _HALF_LUT
    if _HALF_LUT is None:
        lut = []
        m_exp = 0x7C00
        m_sig = 0x03FF
        for h in range(65536):
            sign = (h >> 15) & 1
            exp = (h >> 10) & 0x1F
            sig = h & m_sig
            if exp == 0:
                if sig == 0:
                    f = 0.0
                else:
                    f = sig * 2.0 ** (-24) * (2.0 ** (exp - 15))  # 次正规
            elif exp == 0x1F:
                f = float("inf") if sig == 0 else float("nan")
            else:
                f = (1.0 + sig / float(m_sig)) * 2.0 ** (exp - 15)
            lut.append(-f if sign else f)
        _HALF_LUT = lut
    return _HALF_LUT


def _parse_attrs(d):
    i = 8
    attrs = {}
    while d[i] != 0:
        z = d.index(b"\0", i)
        name = d[i:z].decode("ascii")
        i = z + 1
        z = d.index(b"\0", i)
        typ = d[i:z].decode("ascii")
        i = z + 1
        size = struct.unpack("<I", d[i:i + 4])[0]
        i += 4
        attrs[name] = (typ, d[i:i + size])
        i += size
    return attrs, i + 1


def _parse_chlist(buf):
    chans = {}
    j = 0
    while j < len(buf) and buf[j] != 0:
        z = buf.index(b"\0", j)
        nm = buf[j:z].decode("ascii")
        j = z + 1
        pt, _pl, xs, ys = struct.unpack("<ib3xii", buf[j:j + 16])
        j += 16
        chans[nm] = (pt, xs, ys)
    return chans


def read_exr(path, want=("Z", "R", "G", "B")):
    """读单层扫描线 EXR（ZIP/无压缩），返回 {通道名: [float,...]} + 尺寸。

    仅支持 compression=0(NONE)/3(ZIP, 16行一块)；tile/multipart 拒绝。
    """
    with open(path, "rb") as f:
        d = f.read()
    if d[:4] != b"\x76\x2f\x31\x01":
        raise ValueError("not EXR: %s" % path)
    ver = struct.unpack("<I", d[4:8])[0]
    flags = ver & 0xFC00
    if flags & (0x200 | 0x800 | 0x1000):
        raise ValueError("tile/multipart/multi-view EXR 不支持: %s" % path)
    attrs, i = _parse_attrs(d)
    chans = _parse_chlist(attrs["channels"][1])
    comp = attrs["compression"][1][0]
    if comp not in (0, 3):
        raise ValueError("仅支持 NONE/ZIP 压缩， got %d: %s" % (comp, path))
    x0, y0, x1, y1 = struct.unpack("<4i", attrs["dataWindow"][1])
    w, h = x1 - x0 + 1, y1 - y0 + 1
    bpp = sum(_PX_SIZE[c[0]] for c in chans.values())
    lines = 16 if comp == 3 else 1
    nchunk = (h + lines - 1) // lines
    offsets = struct.unpack("<%dQ" % nchunk, d[i:i + 8 * nchunk])

    order = sorted(chans)  # chlist 依名字节序排布
    out = {nm: [] for nm in order if nm in want}
    if not out:
        return None, (w, h), list(chans)

    lut = _half_to_float_lut() if any(
        chans[nm][0] == 1 for nm in out) else None
    for off in offsets:
        y, dsize = struct.unpack("<ii", d[off:off + 8])
        blob = d[off + 8:off + 8 + dsize]
        rows = min(lines, h - y)
        npx = rows * w
        if comp == 3:
            raw = bytearray(zlib.decompress(blob))
        else:
            raw = bytearray(blob)
        if len(raw) != npx * bpp:
            raise ValueError("EXR 块大小异常 %s @y=%d" % (path, y))
        if comp == 3:
            # 1) 逆交错：planar-by-byte -> interleaved（切片步长赋值）
            for c in range(bpp):
                raw[c::bpp] = raw[c * npx:(c + 1) * npx]
            # 2) 逆差分预测：d[i] -= d[i-bpp]
            prev = raw[0:bpp]
            for p in range(1, npx):
                base = p * bpp
                for c in range(bpp):
                    v = (raw[base + c] - prev[c]) & 0xFF
                    prev[c] = v
                    raw[base + c] = v
                prev = raw[base:base + bpp]
        # 3) 按通道提取
        cbase = 0
        for nm in order:
            pt = chans[nm][0]
            sz = _PX_SIZE[pt]
            if nm in out:
                vals = out[nm]
                if pt == 2:      # float32
                    vals.extend(struct.unpack_from("<%df" % npx, raw, cbase))
                elif pt == 0:    # uint32
                    vals.extend(struct.unpack_from("<%dI" % npx, raw, cbase))
                else:            # half -> LUT
                    lu = lut
                    vals.extend([lu[v] for v in struct.unpack_from(
                        "<%dH" % npx, raw, cbase)])
            cbase += sz * npx
    return out, (w, h), list(chans)


# ---------------- PNG 解码（8bit 非隔行：灰度/RGB/RGBA） ----------------

def read_png_rgb8(path):
    """解码 8bit 非隔行 PNG -> (w, h, [r,g,b,...])。"""
    with open(path, "rb") as f:
        d = f.read()
    if d[:8] != b"\x89PNG\r\n\x1a\n":
        raise ValueError("not PNG: %s" % path)
    i = 8
    ihdr = None
    idat = b""
    while i < len(d):
        ln = struct.unpack(">I", d[i:i + 4])[0]
        typ = d[i + 4:i + 8]
        body = d[i + 8:i + 8 + ln]
        if typ == b"IHDR":
            ihdr = struct.unpack(">IIBBBBB", body)
        elif typ == b"IDAT":
            idat += body
        elif typ == b"IEND":
            break
        i += 12 + ln
    w, h, depth, ct, comp, filt, inter = ihdr
    if depth != 8 or comp != 0 or filt != 0 or inter != 0:
        raise ValueError("仅支持 8bit 非隔行 PNG: %s" % path)
    nch = {0: 1, 2: 3, 4: 2, 6: 4}[ct]
    raw = zlib.decompress(idat)
    stride = w * nch
    px = bytearray(w * h * nch)
    prev = bytearray(stride)
    for y in range(h):
        ft = raw[y * (stride + 1)]
        row = bytearray(raw[y * (stride + 1) + 1:(y + 1) * (stride + 1)])
        if ft == 1:      # Sub
            for x in range(nch, stride):
                row[x] = (row[x] + row[x - nch]) & 0xFF
        elif ft == 2:    # Up
            for x in range(stride):
                row[x] = (row[x] + prev[x]) & 0xFF
        elif ft == 3:    # Average
            for x in range(stride):
                a = row[x - nch] if x >= nch else 0
                row[x] = (row[x] + ((a + prev[x]) >> 1)) & 0xFF
        elif ft == 4:    # Paeth
            for x in range(stride):
                a = row[x - nch] if x >= nch else 0
                b = prev[x]
                c = prev[x - nch] if x >= nch else 0
                pp = a + b - c
                pa, pb, pc = abs(pp - a), abs(pp - b), abs(pp - c)
                pr = a if (pa <= pb and pa <= pc) else (b if pb <= pc else c)
                row[x] = (row[x] + pr) & 0xFF
        px[y * stride:(y + 1) * stride] = row
        prev = row
    if nch == 1:
        g = px
        px = bytearray(w * h * 3)
        for k in range(w * h):
            px[3 * k:3 * k + 3] = bytes((g[k],) * 3)
    elif nch == 2 or nch == 4:
        p2 = bytearray(w * h * 3)
        for k in range(w * h):
            p2[3 * k:3 * k + 3] = px[k * nch:k * nch + 3]
        px = p2
    return w, h, px


# ---------------- PNG 编码（8bit 灰度） ----------------

def write_png_gray(path, w, h, gray):
    """gray: bytes/bytearray 长 w*h。"""
    def chunk(t, body):
        return (struct.pack(">I", len(body)) + t + body +
                struct.pack(">I", zlib.crc32(t + body) & 0xFFFFFFFF))
    stride = w
    raw = b"".join(b"\x00" + bytes(gray[y * stride:(y + 1) * stride])
                   for y in range(h))
    png = (b"\x89PNG\r\n\x1a\n"
           + chunk(b"IHDR", struct.pack(">IIBBBBB", w, h, 8, 0, 0, 0, 0))
           + chunk(b"IDAT", zlib.compress(raw, 6))
           + chunk(b"IEND", b""))
    with open(path, "wb") as f:
        f.write(png)


# ---------------- 派生：深度图 / 线稿 ----------------

def exr_z_depth(exr_path, out_png, near=None, far=None, invert=False):
    """EXR(Z) -> 深度灰度 PNG。默认近=白(255) 远=黑(0)。"""
    ch, (w, h), names = read_exr(exr_path, want=("Z",))
    if ch is None or "Z" not in ch:
        raise ValueError("EXR 无 Z 通道（含通道: %s）: %s" % (names, exr_path))
    z = ch["Z"]
    lo = near if near is not None else min(v for v in z if math.isfinite(v))
    hi = far if far is not None else max(v for v in z if math.isfinite(v))
    rng = (hi - lo) or 1.0
    g = bytearray(w * h)
    for k, v in enumerate(z):
        # 默认近=白(255)：t 越近（z 越小）越白
        if math.isfinite(v):
            t = max(0.0, min(1.0, (v - lo) / rng))
            g[k] = int((1.0 - t) * 255 + 0.5)
        else:
            g[k] = 0  # 无穷远 -> 黑
        if invert:
            g[k] = 255 - g[k]
    write_png_gray(out_png, w, h, g)
    return w, h, lo, hi


def normalize_depth_png(in_png, out_png, invert=False):
    """深度 PNG（Blender compositor 灰度输出）-> VACE 深度图（归一化拉伸）。"""
    w, h, px = read_png_rgb8(in_png)
    g = px[0::3]
    lo, hi = min(g), max(g)
    rng = (hi - lo) or 1
    out = bytearray(w * h)
    for k, v in enumerate(g):
        t = (v - lo) / rng
        if invert:
            t = 1.0 - t
        out[k] = int(t * 255 + 0.5)
    write_png_gray(out_png, w, h, out)
    return w, h, lo, hi


def lineart_from_rgb(w, h, px, out_png, thresh=24):
    """RGB 像素缓冲 -> Sobel 线稿 PNG（白底黑线）。"""
    gray = bytearray(w * h)
    for k in range(w * h):
        r, g_, b = px[3 * k], px[3 * k + 1], px[3 * k + 2]
        gray[k] = (299 * r + 587 * g_ + 114 * b) // 1000
    out = bytearray(b"\xff" * (w * h))
    for y in range(1, h - 1):
        r0, r1, r2 = (y - 1) * w, y * w, (y + 1) * w
        for x in range(1, w - 1):
            gx = (-gray[r0 + x - 1] - 2 * gray[r1 + x - 1] - gray[r2 + x - 1]
                  + gray[r0 + x + 1] + 2 * gray[r1 + x + 1] + gray[r2 + x + 1])
            gy = (-gray[r0 + x - 1] - 2 * gray[r0 + x] - gray[r0 + x + 1]
                  + gray[r2 + x - 1] + 2 * gray[r2 + x] + gray[r2 + x + 1])
            if gx * gx + gy * gy > thresh * thresh * 4:
                out[r1 + x] = 0
    write_png_gray(out_png, w, h, out)


def lineart_from_file(path, out_png, thresh=24):
    if path.lower().endswith(".exr"):
        ch, (w, h), names = read_exr(path, want=("R", "G", "B"))
        if ch is None:
            raise ValueError("EXR 无 RGB: %s" % path)
        n = w * h
        px = bytearray(n * 3)
        # float 线性值 -> sRGB 近似（sqrt），再量化
        lut = [int(255.0 * math.sqrt(i / 255.0) + 0.5) for i in range(256)]
        for c, nm in enumerate("RGB"):
            src = ch[nm]
            for k in range(n):
                v = src[k]
                # NaN（Blender 背景 alpha=0 像素）与负值按 0 处理
                q = 0 if (v != v or v <= 0) else (
                    255 if v >= 1 else int(v * 255))
                px[3 * k + c] = lut[q]
    else:
        w, h, px = read_png_rgb8(path)
    lineart_from_rgb(w, h, px, out_png, thresh)
    return w, h


# ---------------- ffmpeg 封装 ----------------

def find_ffmpeg():
    """委托 config/paths.ffmpeg()（完整构建优先 + AI_FILM_FFMPEG_BIN 覆盖）。"""
    try:
        return _ffmpeg()
    except Exception:
        return None


def frames_to_mp4(frame_dir, fps, out, width=1280, height=720):
    """帧序列 -> mp4（Wan/VACE 对齐 720P）。返回 (out, size, frames)。"""
    ff = find_ffmpeg()
    if not ff:
        raise RuntimeError("未找到 ffmpeg，无法封装 mp4")
    pngs = sorted(glob.glob(os.path.join(frame_dir, "*.png")))
    if not pngs:
        raise RuntimeError("帧目录为空: %s" % frame_dir)
    first = None
    pat = None
    import re
    m = re.search(r"^(.*?)(\d+)\.png$", os.path.basename(pngs[0]), re.I)
    if m:
        prefix, num = m.group(1), m.group(2)
        suffix = os.path.splitext(os.path.basename(pngs[0]))[1]
        # 所有帧共享同一非数字前缀 → 标准 image2 序列
        if all(os.path.basename(f).startswith(prefix) and
               re.search(r"^\d+\.png$", os.path.basename(f)[len(prefix)], re.I)
               for f in pngs):
            first = int(num)
            pat = os.path.join(frame_dir,
                               "%s%%0%dd%s" % (prefix, len(num), suffix)
                               ).replace("\\", "/")
    os.makedirs(os.path.dirname(os.path.abspath(out)) or ".", exist_ok=True)
    if first is not None:
        cmd = [ff, "-y", "-framerate", str(fps), "-start_number", str(first),
               "-i", pat,
               "-vf", "scale=%d:%d:flags=lanczos" % (width, height),
               "-c:v", "libx264", "-crf", "16", "-pix_fmt", "yuv420p",
               "-movflags", "+faststart", os.path.abspath(out)]
    else:
        # 帧名非标准序列（如 Unsaveddepth0001_depth.png）→ concat demuxer
        lst = os.path.join(frame_dir, "_concat.txt")
        dur = 1.0 / fps
        with open(lst, "w", encoding="utf-8") as f:
            for p in pngs:
                f.write("file '%s'\nduration %.6f\n" % (
                    os.path.abspath(p).replace("\\", "/"), dur))
            f.write("file '%s'\n" % os.path.abspath(pngs[-1]).replace("\\", "/"))
        cmd = [ff, "-y", "-f", "concat", "-safe", "0", "-i", lst,
               "-vf", "scale=%d:%d:flags=lanczos" % (width, height),
               "-c:v", "libx264", "-crf", "16", "-pix_fmt", "yuv420p",
               "-movflags", "+faststart", os.path.abspath(out)]
    r = subprocess_run(cmd)
    if r.returncode != 0:
        raise RuntimeError("ffmpeg 失败: %s" % r.stderr[-800:])
    return out, os.path.getsize(out), len(pngs)


def subprocess_run(cmd):
    import subprocess
    return subprocess.run(cmd, capture_output=True, text=True)


# ---------------- CLI ----------------

def _collect(in_dir, exts):
    fs = sorted(f for f in glob.glob(os.path.join(in_dir, "*"))
                if f.lower().endswith(exts))
    if not fs:
        raise RuntimeError("输入目录无 %s 帧: %s" % (exts, in_dir))
    return fs


def cmd_depth(a):
    os.makedirs(a.out, exist_ok=True)
    # EXR-Z 优先；否则把目录里的灰度 PNG 视作深度源归一化
    in_dir = a.in_dir
    exrs = sorted(f for f in glob.glob(os.path.join(in_dir, "*"))
                  if f.lower().endswith(".exr"))
    n = 0
    for f in exrs:
        w, h, lo, hi = exr_z_depth(f, os.path.join(
            a.out, os.path.splitext(os.path.basename(f))[0] + "_depth.png"),
            near=a.near, far=a.far, invert=a.invert)
        n += 1
        if a.sample and n <= a.sample:
            print("  depth %s: %dx%d z=[%.3f..%.3f]" % (
                os.path.basename(f), w, h, lo, hi))
    if n:
        print("DEPTH_DONE %d 帧 -> %s" % (n, a.out))
        return 0
    pngs = _collect(a.in_dir, (".png",))
    for f in pngs:
        w, h, lo, hi = normalize_depth_png(f, os.path.join(
            a.out, os.path.splitext(os.path.basename(f))[0] + "_depth.png"),
            invert=a.invert)
        n += 1
        if a.sample and n <= a.sample:
            print("  depth(png) %s: %dx%d lum=[%d..%d]" % (
                os.path.basename(f), w, h, lo, hi))
    print("DEPTH_DONE %d 帧(png 深度源) -> %s" % (n, a.out))
    return 0


def cmd_lineart(a):
    os.makedirs(a.out, exist_ok=True)
    fs = _collect(a.in_dir, (".png", ".exr"))
    for n, f in enumerate(fs, 1):
        w, h = lineart_from_file(f, os.path.join(
            a.out, os.path.splitext(os.path.basename(f))[0] + "_line.png"),
            thresh=a.thresh)
        if a.sample and n <= a.sample:
            print("  line %s: %dx%d" % (os.path.basename(f), w, h))
    print("LINEART_DONE %d 帧 -> %s" % (len(fs), a.out))
    return 0


def cmd_mp4(a):
    out, size, n = frames_to_mp4(a.frames, a.fps, a.out, a.width, a.height)
    print("MP4_DONE %s %d bytes %d frames %dx%d" % (
        out, size, n, a.width, a.height))
    return 0


def main():
    p = argparse.ArgumentParser("exr_to_control")
    sub = p.add_subparsers(dest="cmd", required=True)
    pd = sub.add_parser("depth", help="EXR-Z/深度PNG -> VACE 深度图")
    pd.add_argument("--in-dir", required=True)
    pd.add_argument("--out", required=True)
    pd.add_argument("--near", type=float, default=None)
    pd.add_argument("--far", type=float, default=None)
    pd.add_argument("--invert", action="store_true")
    pd.add_argument("--sample", type=int, default=3)
    pd.set_defaults(fn=cmd_depth)
    pl = sub.add_parser("lineart", help="RGB PNG/EXR -> 线稿")
    pl.add_argument("--in-dir", required=True)
    pl.add_argument("--out", required=True)
    pl.add_argument("--thresh", type=int, default=24)
    pl.add_argument("--sample", type=int, default=3)
    pl.set_defaults(fn=cmd_lineart)
    pm = sub.add_parser("mp4", help="帧序列 -> 720P mp4")
    pm.add_argument("--frames", required=True)
    pm.add_argument("--fps", type=int, default=24)
    pm.add_argument("--out", required=True)
    pm.add_argument("--width", type=int, default=1280)
    pm.add_argument("--height", type=int, default=720)
    pm.set_defaults(fn=cmd_mp4)
    a = p.parse_args()
    sys.exit(a.fn(a))


if __name__ == "__main__":
    main()
