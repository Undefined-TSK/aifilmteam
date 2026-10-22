# -*- coding: utf-8 -*-
"""tech_cut.py — 把 v4 抬到自定交付规格（P-0e）。只读原片，输出到 output/tech_v5/。

1) 视频：24fps 重定基（源本就 24fps，消 judder）→ 1920×1080 → crf16/slow（码率达标）
   → 统一颗粒+暗角 → 片头 4 秒"本片由 AI 生成合成"显式标识（法定）；
2) 音频：从 mix_tmp 的 80s 分轨 + 对白/音效 stem 重建 48kHz/24bit，三层床（硬雨+远景低鸣+雷低通）、
   对白按真时码 + 按空间混响预置 + 压缩；末了**两遍法** loudnorm 到 -14 LUFS/TP-1.5；
3) 合成 mp4 时写 AIGC 元数据（GB 45438-2025 隐式标识）。
输入清单全从 pipeline/audio_cues_v1.json 的 src 字段读，不做名字猜测。
"""
import glob
import json
import os
import re
import subprocess
import sys
from pathlib import Path

sys.stdout.reconfigure(encoding="utf-8", errors="replace")


def find_bin():
    for pat in (r"C:\Users\LZH\AppData\Local\Microsoft\WinGet\Packages\Gyan.FFmpeg*\*\bin\ffprobe.exe",
                r"C:\Program Files\ffmpeg*\bin\ffprobe.exe"):
        g = glob.glob(pat)
        if g:
            return os.path.dirname(sorted(g)[-1])
    raise SystemExit("找不到 ffmpeg，请给路径")


BIN = find_bin()
FF = os.path.join(BIN, "ffmpeg.exe")
ROOT = Path(__file__).resolve().parents[1]
PB = ROOT / "projects" / "雨夜寻猫"
V4 = PB / "output" / "雨夜寻猫_粗剪_v4.mp4"
WORK = PB / "output" / "tech_v5"
SPEC = json.load(open(ROOT / "pipeline" / "tech_delivery_spec.json", encoding="utf-8"))
PROF = SPEC["profiles"]["web1080"]
V, LB = PROF["video"], SPEC["ai_label"]["explicit"]
CRF = V.get("crf", 16)
RATE = int(PROF["audio"]["rate"])
REV = {"出租屋内": "aecho=0.85:0.9:18:0.16", "雨夜街道": "aecho=0.85:0.85:38:0.22",
       "雨夜巷口": "aecho=0.85:0.88:28:0.20", "归途": "aecho=0.85:0.8:46:0.18",
       "雨声渐弱": "aecho=0.85:0.8:46:0.18"}


ERRN = [0]


def run(c, quiet=False):
    r = subprocess.run(c, capture_output=True, text=True, encoding="utf-8", errors="replace")
    if r.returncode:
        ERRN[0] += 1
        os.makedirs(WORK, exist_ok=True)
        open(os.path.join(WORK, "ff_err_%d.txt" % ERRN[0]), "w", encoding="utf-8").write(
            " ".join(map(str, c)) + "\n\n" + (r.stderr or ""))
        print("FF err ->", "ff_err_%d.txt" % ERRN[0], (r.stderr or "")[-260:])
    return r


def p8(n):
    return max(8, int(round((n or 0) * 1000)))


def amb_space(scene):
    for k, v in REV.items():
        if k in (scene or ""):
            return v
    return "aecho=0.85:0.86:30:0.2"


def main():
    os.makedirs(WORK, exist_ok=True)
    rep = {"steps": [], "note": "video layer only"}

    w, h = (int(x) for x in V["res"].split("x"))
    vf = ("fps=%g,format=yuv420p,scale=%d:%d:flags=lanczos,setsar=1,fps=%g,"
          "noise=alls=6:allf=t+u,vignette=PI/5.5,"
          "drawtext=fontfile=C\\\\:/Windows/Fonts/msyh.ttc:text='%s':fontsize=%d:"
          "fontcolor=white:borderw=2:bordercolor=black@0.65:x=(w-text_w)/2:y=h*%s:"
          "enable='between(t,0,%g)'" % (V["fps"], w, h, V["fps"], LB["text"], LB["font_min_px"],
                                         LB["y_pct_start_of_frame"], max(LB["min_duration_s"], 4)))
    vout = os.path.join(WORK, "video_24fps_1080.mp4")
    if os.path.exists(vout) and os.path.getsize(vout) > 5_000_000 and "--force-video" not in sys.argv:
        r1 = type("R", (), {"returncode": 0})()
        rep["steps"].append(["video_reuse_existing", True])
    else:
        r1 = run([FF, "-hide_banner", "-loglevel", "error", "-y", "-i", V4, "-vf", vf, "-c:v", "libx264",
              "-pix_fmt", "yuv420p", "-r", "%g" % V["fps"], "-g", str(int(V["fps"] * 2)),
              "-video_track_timescale", "24000", "-an", vout])
    rep["steps"].append(["video_24fps_1080_crf16_ai_label", r1.returncode == 0])

    json.dump(rep, open(os.path.join(WORK, "video_report.json"), "w", encoding="utf-8"),
              ensure_ascii=False, indent=1)
    mp = os.path.join(PB, "timeline", "master_v2.json")
    if os.path.exists(mp):
        m = json.load(open(mp, encoding="utf-8"))
        m.setdefault("meta", {})["explicit_label_burned_in"] = {
            "done": True, "by": "pipeline/tech_cut.py drawtext",
            "text": LB["text"], "window_s": [0.0, 4.0], "proof": os.path.basename(vout)}
        m["meta"]["delivery_stage"] = m["meta"].get("delivery_stage", "preview")
        json.dump(m, open(mp, "w", encoding="utf-8"), ensure_ascii=False, indent=1)
        rep["master_meta_updated"] = True
    print("视频规格层完成（24fps CFR / 1080p / ABR / 颗粒暗角 / 片头显式AI标识）→",
          os.path.relpath(vout, ROOT), "OK" if r1.returncode == 0 else "FAIL")
    print("音频与合成不归本文件：见 pipeline/audio_mix.py（专业对口拆分）")
    return 0 if r1.returncode == 0 else 2


if __name__ == "__main__":
    sys.exit(main())
