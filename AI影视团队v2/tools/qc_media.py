# -*- coding: utf-8 -*-
"""qc_media.py v7 — 交付技术门（只读；数值口径全部来自 pipeline/tech_delivery_spec.json）

职责（专业对口）：只判可客观测量项 + 溯源判定。不判审美、不做像素运动检测
（第五批标定否证：四种运动判据在 18 镜上最佳 16/18，且静图+缓推读数高于真动效镜），
不改片子、不定义标准。静图/真动一律由 tools/dit_ingest.py 的 kind 溯源判定。
用法：python tools/qc_media.py <媒体> <输出json> [--timeline 路径] [--profile web1080] [--shot 4-1]
"""
import argparse
import glob
import json
import os
import re
import subprocess
import sys
from pathlib import Path

try:
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
except Exception:
    pass

ROOT = Path(__file__).resolve().parents[1]
# 维度25：ffmpeg/ffprobe 改由 config/paths.py 中心化解析（原硬编码 C:\Users\LZH\...）
sys.path.insert(0, str(ROOT))
from config.paths import ffmpeg, ffprobe  # noqa: E402

FF, FP = ffmpeg(), ffprobe()
ERRN = [0]


def run(c, quiet=False):
    r = subprocess.run(c, capture_output=True, text=True, encoding="utf-8", errors="replace")
    if r.returncode and not quiet:
        ERRN[0] += 1
        os.makedirs(os.path.join(ROOT, "logs"), exist_ok=True)
        with open(os.path.join(ROOT, "logs", "qc_err_%d.txt" % ERRN[0]), "w", encoding="utf-8") as f:
            f.write(" ".join(map(str, c)) + "\n\n" + (r.stderr or ""))
    return r


def probe(p):
    return json.loads(run([FP, "-v", "error", "-show_format", "-show_streams", "-of", "json", p], True).stdout)


def loud(meedia, windows=None, i=-14.0, tp=-1.5, lra=11):
    src = meedia
    tmp = None
    if windows:
        tmp = os.path.join(ROOT, "logs", "_qcwin.wav")
        inp, fc = [], []
        for k, (a, b) in enumerate(windows):
            inp += ["-i", meedia]
            fc.append("[%d:a]aresample=48000,atrim=%g:%g,asetpts=PTS-STARTPTS[w%d]" % (k, a, b, k))
        fc.append("".join("[w%d]" % k for k in range(len(windows))) +
                  "amix=inputs=%d:normalize=0:duration=longest[o]" % len(windows))
        r = run([FF, "-hide_banner", "-loglevel", "error", "-y"] + inp +
                ["-filter_complex", ";".join(fc), "-map", "[o]", "-ar", "48000", tmp])
        if r.returncode:
            raise RuntimeError("裁窗失败")
        src = tmp
    r = run([FF, "-hide_banner", "-nostats", "-i", src, "-af",
             "loudnorm=I=%s:TP=%s:LRA=%s:print_format=json" % (i, tp, lra), "-f", "null", "-"], True)
    if tmp and os.path.exists(tmp):
        os.remove(tmp)
    m = re.search(r"\{[^{}]*input_i[^{}]*\}", r.stderr or "", re.S)
    if not m:
        raise RuntimeError("响度解析失败")
    return {k: float(v) for k, v in json.loads(m.group(0)).items() if k.startswith(("input", "target_o"))}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("media")
    ap.add_argument("out")
    ap.add_argument("--timeline", default=os.path.join(ROOT, "projects", "雨夜寻猫", "timeline", "master_v2.json"))
    ap.add_argument("--profile", default="web1080")
    ap.add_argument("--shot", default=None)
    a = ap.parse_args()
    SP = json.load(open(ROOT / "pipeline" / "tech_delivery_spec.json", encoding="utf-8"))
    P = SP["profiles"][a.profile]
    VI, AU, PL, DLC, AIL = P["video"], P["audio"], P["program_loudness"], P.get("dialogue_check", {}), SP["ai_label"]
    tl = json.load(open(a.timeline, encoding="utf-8"))
    meta = tl.get("meta", {}) or {}
    stage = meta.get("delivery_stage", SP.get("default_stage", "preview"))
    lin = {}
    lp = os.path.join(ROOT, "projects", tl.get("project", "雨夜寻猫"), "ditmap", "lineage.jsonl")
    if os.path.exists(lp):
        for ln in open(lp, encoding="utf-8"):
            r = json.loads(ln)
            lin[str(r.get("shot_id"))] = r.get("kind")

    d = probe(a.media)
    fmt = d["format"]
    v = next((s for s in d["streams"] if s.get("codec_type") == "video"), {})
    au = next((s for s in d["streams"] if s.get("codec_type") == "audio"), {})
    fr = (v.get("avg_frame_rate") or "0/1").split("/")
    fps = round(float(fr[0]) / float(fr[1] or 1), 4) if float(fr[0] or 0) else 0.0
    kbps = round(int(v.get("bit_rate") or fmt.get("bit_rate") or 0) / 1000, 1)
    ww, wh = (int(x) for x in VI["res"].split("x"))
    fails, warns, info = [], [], {"delivery_stage": stage}

    if abs(fps - VI["fps"]) > VI.get("fps_tolerance", 0.01):
        fails.append("帧率 %s ≠ %s（±%s，禁 1001 时基引入节拍抖动）" % (fps, VI["fps"], VI.get("fps_tolerance")))
    if (v.get("width"), v.get("height")) != (ww, wh):
        fails.append("分辨率 %sx%s ≠ %s" % (v.get("width"), v.get("height"), VI["res"]))
    if kbps < VI["min_video_kbps"]:
        m = "视频码率 %skbps < %s（静图放大内容必然欠载；真动化后才可能达标）" % (kbps, VI["min_video_kbps"])
        (fails if stage == "final" else warns).append(m if stage == "final" else m + "｜preview 记警示")
    if str(au.get("sample_rate")) != str(AU["rate"]):
        fails.append("采样率 %s ≠ %s" % (au.get("sample_rate"), AU["rate"]))
    if int(au.get("channels") or 0) != int(AU["channels"]):
        fails.append("声道 %s ≠ %s" % (au.get("channels"), AU["channels"]))

    try:
        L = loud(a.media, i=PL["integrated_lufs"], tp=PL["true_peak_dbtp_max"], lra=PL.get("lra_max", 11))
        info["program_loudness"] = {k: round(x, 2) for k, x in L.items()}
        if abs(L["input_i"] - PL["integrated_lufs"]) > PL["tolerance"]:
            fails.append("程序响度 %.2f LUFS ≠ %s±%s" % (L["input_i"], PL["integrated_lufs"], PL["tolerance"]))
        if L["input_tp"] > PL["true_peak_dbtp_max"]:
            fails.append("真峰 %.2f dBTP > %s" % (L["input_tp"], PL["true_peak_dbtp_max"]))
        if L.get("input_lra", 0) > PL.get("lra_max", 99):
            warns.append("LRA %.1f > %s" % (L["input_lra"], PL["lra_max"]))
        wins = []
        for it in (tl["tracks"]["dialogue"].get("items") or []):
            for e in (it.get("events") or [it] if "start_s" in it else it.get("events") or []):
                s0 = float(e.get("start_s", 0))
                wins.append((s0, s0 + float(e.get("dur_s") or 2)))
        if wins and DLC.get("method") == "dialogue_window_relative":
            Dg = loud(a.media, windows=wins, i=PL["integrated_lufs"], tp=PL["true_peak_dbtp_max"])
            delta = round(Dg["input_i"] - L["input_i"], 2)
            lo, hi = DLC["band"]
            info["dialogue_window_relative"] = {"window_lufs": round(Dg["input_i"], 2), "delta_lu": delta,
                                                "band_lu": [lo, hi], "remedy": DLC.get("remedy")}
            if not (lo <= delta <= hi):
                fails.append("对白窗口相对程序响 %+.2f LU 超 [%s,%s]；修法只改 spec.bus_trim_db（%s），不改判据"
                             % (delta, lo, hi, json.dumps(SP.get("bus_trim_db", {}), ensure_ascii=False)))
    except Exception as ex:
        fails.append("响度测量失败：" + str(ex)[:150])

    r = run([FF, "-hide_banner", "-nostats", "-i", a.media, "-vf",
             "blackdetect=d=0.45:pix_th=0.10,freezedetect=n=-50dB:d=1.2", "-an", "-f", "null", "-"], True)
    black = re.findall(r"black_start:([\d.]+)", r.stderr or "")
    frozen = re.findall(r"freeze_start:([\d.]+)", r.stderr or "")
    info["defects"] = {"black_spans": black[:6], "frozen_over_1p2s": frozen[:8]}
    if black:
        fails.append("意外黑帧 %d 处" % len(black))
    if len(frozen) > 3:
        warns.append("完全静止>1.2s %d 处（静图镜属预期，须人工确认非坏帧）" % len(frozen))

    blob = json.dumps(d, ensure_ascii=False).lower()
    need = [k.lower() for k in AIL["implicit_metadata_keys"] if k != "aigc_generated_at"]
    have = [k for k in need if k in blob]
    info["aigc_implicit"] = {"required": need, "present": have}
    if len(have) < len(need):
        fails.append("AIGC 隐式元数据缺 %s（GB 45438-2025，容器 %s）" % (sorted(set(need) - set(have)), os.path.splitext(a.media)[1]))
    burned = meta.get("explicit_label_burned_in") or {}
    ovs = json.dumps(tl["tracks"].get("overlay", {}), ensure_ascii=False)
    if "ai_label" not in ovs and not burned.get("done"):
        fails.append("AI 显式标识无证据（overlay 未登记且无视频层烧录记录）")
    else:
        info["explicit_label"] = {"via": "overlay 登记"} if "ai_label" in ovs else {"via": "视频层烧录", "proof": burned}

    kinds = {}
    for k in lin.values():
        kinds[k] = kinds.get(k, 0) + 1
    info["provenance_kind_counts"] = kinds
    stills = sorted([s for s, k in lin.items() if k != "video"])
    if stills:
        msg = "血缘 kind≠video 共 %d 镜：%s" % (len(stills), ",".join(stills[:8]))
        (fails if stage == "final" else warns).append(msg if stage == "final" else msg + "｜final 阶段必硬判")
    if a.shot:
        kk = lin.get(str(a.shot))
        info["checked_shot_provenance"] = {"shot": a.shot, "kind": kk}
        if kk != "video":
            fails.append("被检镜 %s kind=%s 非视频源" % (a.shot, kk))
    if meta.get("auto_draft_needs_confirm"):
        warns.append("%d 项轨道值为脚本自动草稿未签字（g1 门前须签）" % len(meta["auto_draft_needs_confirm"]))

    res = {"file": os.path.basename(a.media), "profile": a.profile, "stage": stage,
           "spec_schema": SP["schema"], "spec_source": "pipeline/tech_delivery_spec.json",
           "measured": {"res": "%sx%s" % (v.get("width"), v.get("height")), "fps": fps, "kbps": kbps,
                        "audio_rate": au.get("sample_rate"), "audio_ch": au.get("channels"),
                        "duration_s": round(float(fmt.get("duration", 0) or 0), 3)},
           "info": info, "fail": fails, "warn": warns, "verdict": "PASS" if not fails else "FAIL"}
    json.dump(res, open(a.out, "w", encoding="utf-8"), ensure_ascii=False, indent=1)
    print("\n=== 技术门 %s | %s | 阶段 %s ===" % (res["verdict"], res["file"], stage))
    print("  实测 " + json.dumps(res["measured"], ensure_ascii=False))
    print("  响度 " + json.dumps(info.get("program_loudness", {}), ensure_ascii=False) +
          " ‖ 对白相对差 " + json.dumps(info.get("dialogue_window_relative", {}), ensure_ascii=False))
    for x in fails:
        print("  [FAIL] " + x)
    for x in warns:
        print("  [WARN] " + x)
    print("  口径 " + res["spec_source"])
    return 0 if res["verdict"] == "PASS" else 3


if __name__ == "__main__":
    sys.exit(main())

