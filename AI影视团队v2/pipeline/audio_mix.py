# -*- coding: utf-8 -*-
"""audio_mix.py — 按 cue 表 + 交付标准重建 48k/24bit 分轨与母带（P-0e 音频层）

边界（专业对口）：
- 数值口径只读 pipeline/tech_delivery_spec.json（本脚本不发明标准）；
- 何时/何轨/多大声只读 pipeline/audio_cues_v1.json（本脚本不做创作决策）；
- ffmpeg 只执行既定自动化：延迟放置、增益、按空间混响发送、压缩、sidechain ducking、限幅、两遍响度归一；
- 缺的素材层**不用滤波伪造**，写进 blocked_items 交回音效层（上一版那样做是 ffmpeg 兼职当音效设计）。
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
    for pat in (r"C:\Users\LZH\AppData\Local\Microsoft\WinGet\Packages\Gyan.FFmpeg*\*\bin\ffmpeg.exe",
                r"C:\Program Files\ffmpeg*\bin\ffmpeg.exe"):
        g = glob.glob(pat)
        if g:
            return os.path.dirname(sorted(g)[-1])
    raise SystemExit("找不到 ffmpeg")


BIN = find_bin()
FF = os.path.join(BIN, "ffmpeg.exe")
ROOT = Path(__file__).resolve().parents[1]
PB = ROOT / "projects" / "雨夜寻猫"
WORK = PB / "output" / "tech_v5"
SPEC = json.load(open(ROOT / "pipeline" / "tech_delivery_spec.json", encoding="utf-8"))
CHS = int(SPEC["profiles"]["web1080"]["audio"]["channels"])
TRIM = SPEC.get("bus_trim_db", {})
PROF = SPEC["profiles"]["web1080"]
AU = PROF["audio"]; RATE = int(AU["rate"]); CHS = int(AU["channels"])
PBITS = "pcm_s%dle" % int(AU.get("bit_depth", 24))
DUR = 80.0
IRDIR = ROOT / "assets" / "ir"
SPACE = {"出租屋内": (18, 0.16, "room_indoor_018.wav"), "雨夜街道": (38, 0.22, "street_night_038.wav"),
         "雨夜巷口": (28, 0.20, "alley_wet_028.wav"), "归途": (46, 0.18, "street_night_038.wav")}
ERRN = [0]


def run(c, tag, quiet=False):
    r = subprocess.run(c, capture_output=True, text=True, encoding="utf-8", errors="replace")
    if r.returncode:
        ERRN[0] += 1
        os.makedirs(WORK, exist_ok=True)
        open(os.path.join(WORK, "audio_err_%d.txt" % ERRN[0]), "w", encoding="utf-8").write(
            " ".join(c) + "\n\n" + (r.stderr or ""))
        print(f"[{tag}] 失败 → audio_err_{ERRN[0]}.txt |", (r.stderr or "").strip().splitlines()[-1][:200] if r.stderr else "")
    return r


def db2lin(x):
    return round(10 ** (float(x) / 20), 4)


def delay(e):
    return "adelay=%d:all=1" % int(round(float(e["start_s"]) * 1000))


def build_group(name, events, resolve, chain, outfile, blk, approx):
    tr = round(10 ** (float(TRIM.get(name, 0)) / 20), 4)
    inp, fc, labs = [], [], []
    for i, e in enumerate(events):
        src = resolve(e)
        if not src or not os.path.exists(src):
            blk.append(f"{name}: 素材缺 {os.path.basename(str(src))}")
            continue
        inp += ["-i", src]
        lab = f"{name}{i}"
        fc.append("[%d:a]aresample=%d,aformat=sample_fmts=fltp:channel_layouts=stereo,%s[%s]" % (len(inp) // 2 - 1, RATE, chain(e, approx), lab))
        labs.append(lab)
    if not labs:
        blk.append(f"{name}: 整轨无可用素材")
        return None
    if len(labs) == 1:
        last = labs[0]
        fc.append("[%s]anull,%s[rawx]" % (last, "apad"))
    else:
        fc.append("".join("[%s]" % l for l in labs) +
                  "amix=inputs=" + str(len(labs)) + ":duration=longest:normalize=0,apad,volume=%s[rawx]" % tr)
    fc.append("[rawx]atrim=0:" + ("%g" % DUR) + ",asetpts=PTS-STARTPTS[OUT]")
    out = os.path.join(WORK, outfile)
    r = run([FF, "-hide_banner", "-loglevel", "error", "-y"] + inp +
            ["-filter_complex", ";".join(fc), "-map", "[OUT]", "-ar", str(RATE), "-c:a", PBITS, out], name)
    return out if r.returncode == 0 else None


def dlg_chain(e, approx):
    key = next((k for k in SPACE if k in (e.get("anchor_scene") or e.get("text") or "")), "雨夜街道")
    pd, dec, irf = SPACE[key]
    ir = os.path.join(IRDIR, irf)
    if os.path.exists(ir):
        verb = "afir=irfile='%s':normalize=scale=manual" % ir.replace("\\", "/")
    else:
        verb = "aecho=0.8:0.9:%d:%.2f" % (pd, dec)
        approx.append("dialogue %s 用 aecho 近似（缺 IR：%s）" % (e.get("line"), irf))
    return "highpass=f=95,%s,acompressor=threshold=0.09:ratio=3:attack=8:release=140,%s" % (verb, delay(e))


def mus_chain(e, approx):
    c = "volume=%s,%s" % (round(float(e.get("level_lin", 0.35)), 4), delay(e))
    fo = float(e.get("fade_out_s") or 0)
    if fo > 0:
        c += ",afade=t=out:st=%.2f:d=%.2f" % (max(0.0, float(e.get("end_s") or DUR) - fo), fo)
    return c


def main():
    os.makedirs(WORK, exist_ok=True)
    T = json.load(open(ROOT / "pipeline" / "audio_cues_v1.json", encoding="utf-8"))
    T = T.get("tracks") or T.get("stems") or {}
    blk, approx = [], []
    amb = build_group("AMB", T.get("ambience", {}).get("events", []),
                      lambda e: os.path.join(PB, e["src"]),
                      lambda e, ap: "volume=%s,%s" % (db2lin(-6), delay(e)),
                      "stem_ambience.wav", blk, approx)
    for e in T.get("ambience", {}).get("events", []):
        for miss in e.get("layers_missing") or []:
            blk.append("AMB 待补录层「%s」（场景 %s）→ 归音效层，不用 ffmpeg 伪造" % (miss, e.get("scene")))
    dlg = build_group("DLG", T.get("dialogue", {}).get("events", []),
                      lambda e: os.path.join(PB, "audio", "dialogue", e["line"] + ".mp3"), dlg_chain,
                      "stem_dialogue.wav", blk, approx)
    sfx = build_group("FX", T.get("sfx", {}).get("events", []),
                      lambda e: os.path.join(PB, e.get("src") or ("audio/sfx/%s.mp3" % e.get("name"))),
                      lambda e, ap: (("aloop=loop=%d:size=2e9," % e["loop"]) if e.get("loop") else "")
                      + "volume=%s,%s" % (round(float(e.get("gain_lin", 0.5)) * 1.6, 3), delay(e)),
                      "stem_sfx.wav", blk, approx)
    mus = build_group("MX", T.get("music", {}).get("events", []),
                      lambda e: os.path.join(PB, e["src"]), mus_chain, "stem_music.wav", blk, approx)
    pairs = [x for x in (("AMB", amb), ("DLG", dlg), ("FX", sfx), ("MX", mus)) if x[1]]
    if not pairs:
        print("无任何分轨"); return 2
    idx = {n: i for i, (n, _) in enumerate(pairs)}

    fc, inp = [], []
    for n, path in pairs:
        inp += ["-i", path]
    fc += ["[%d:a]anull[anull_%s]" % (i, n) for i, (n, _) in enumerate(pairs)]
    mixpads = []
    if "MX" in idx and "DLG" in idx:
        fc.append("[anull_DLG]asplit=2[dlgv][dlgsc]")           # 对白一路进混音、一路做侧链
        fc.append("[anull_MX][dlgsc]sidechaincompress=threshold=0.05:ratio=6:attack=25:release=280[mxde]")
        mixpads = ["mxde", "dlgv"]
        mxp = "mxde"
    else:
        mixpads = [f"anull_{n}" for n, _ in pairs]
        mxp = None
    for n, _ in pairs:
        if n in ("MX", "DLG") and mxp:
            continue
        if n == "MX" and mxp:
            continue
        if f"anull_{n}" not in mixpads:
            mixpads.append(f"anull_{n}")
    fc.append("".join("[%s]" % p for p in mixpads) +
              "amix=inputs=%d:duration=longest:normalize=0,alimiter=limit=0.9[mxp]" % len(mixpads))
    fc.append("[mxp]atrim=0:%g[out]" % DUR)
    up_note = "分轨经 aformat 上混/复制到 %d 声道" % CHS
    pre = os.path.join(WORK, "mix_pre.wav")
    r = run([FF, "-hide_banner", "-loglevel", "error", "-y"] + inp +
            ["-filter_complex", ";".join(fc), "-map", "[out]", "-ar", str(RATE), "-c:a", PBITS, pre], "mix")
    if r.returncode:
        return 2
    nt = PROF["program_loudness"]
    m = run([FF, "-hide_banner", "-nostats", "-i", pre, "-af",
             "loudnorm=I=%s:TP=%s:LRA=%s:print_format=json" % (nt["integrated_lufs"], nt["true_peak_dbtp_max"], nt["lra_max"]),
             "-f", "null", "-"], "measure", True)
    mm = re.search(r"\{[^{}]*\"input_i\"[^{}]*\}", (m.stdout or "") + (m.stderr or ""), re.S)
    if not mm:
        print("响度第一遍测量失败"); return 2
    meas = json.loads(mm.group(0))
    fin = os.path.join(WORK, "audio_48k_master.wav")
    ln = ("loudnorm=I=%s:TP=%s:LRA=%s:linear=true:measured_I=%s:measured_TP=%s:measured_LRA=%s:measured_thresh=%s:offset=%s"
          % (nt["integrated_lufs"], nt["true_peak_dbtp_max"], nt["lra_max"], meas["input_i"], meas["input_tp"],
             meas["input_lra"], meas["input_thresh"], meas["target_offset"]))
    r2 = run([FF, "-hide_banner", "-loglevel", "error", "-y", "-i", pre, "-af",
              ln + ",alimiter=limit=0.82:attack=5:release=80:level=disabled", "-ar", str(RATE),
              "-ac", str(CHS), "-c:a", PBITS, fin], "two_pass")
    rep = {"spec": SPEC["schema"], "profile": "web1080",
           "stems": {n: os.path.basename(p) for n, p in pairs},
           "pass1_measure": {k: round(float(v), 2) for k, v in meas.items() if k.startswith(("input", "target"))},
           "target": nt, "dialogue_check": PROF["dialogue_check"], "master": os.path.relpath(fin, ROOT) if r2.returncode == 0 else None,
           "blocked_items": blk, "approx_items": approx,
           "next": "对白门控 -27 与母带响度由 tools/qc_media.py 按同一 spec 复检"}
    json.dump(rep, open(os.path.join(WORK, "audio_report.json"), "w", encoding="utf-8"), ensure_ascii=False, indent=1)
    print(json.dumps({"stems": rep["stems"], "pass1": rep["pass1_measure"], "master": rep["master"]}, ensure_ascii=False, indent=1))
    print(f"blocked {len(blk)} / approx {len(approx)}")
    for x in blk[:5]:
        print("  [阻塞] " + x)
    return 0 if r2.returncode == 0 else 2


def mux():
    v = os.path.join(WORK, "video_24fps_1080.mp4")
    AUDIO = os.path.join(WORK, "audio_48k_master.wav")
    out = os.path.join(WORK, "雨夜寻猫_v5_tech.mkv")
    if not (os.path.exists(v) and os.path.exists(AUDIO)):
        print("缺视频或母带", os.path.exists(v), os.path.exists(AUDIO)); return 2
    ex = dict(SPEC["ai_label"]["implicit_values_example"])
    ex["aigc_generated_at"] = "2026-09-26"
    md = []
    for mk in SPEC["ai_label"]["implicit_metadata_keys"]:
        mv = str(ex.get(mk, "")).replace("<渲染日期>", "2026-09-26")
        md += ["-metadata", "%s=%s" % (mk, mv)]
    r = run([FF, "-hide_banner", "-loglevel", "error", "-y", "-i", v, "-i", AUDIO,
             "-map", "0:v", "-map", "1:a", "-c:v", "copy",
             "-c:a", "pcm_s24le", "-ar", str(RATE), "-ac", str(CHS)] + md + ["-shortest", out], "mux")
    print("交付版 →", os.path.relpath(out, ROOT), "OK" if r.returncode == 0 else "失败")
    return 0 if r.returncode == 0 else 2


if __name__ == "__main__":
    sys.exit(mux() if "--mux" in sys.argv else main())

