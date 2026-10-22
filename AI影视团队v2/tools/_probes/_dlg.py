import json
import os
import re
import subprocess
import sys

sys.path.insert(0, r"D:\ai_film_projects\pipeline")
import audio_mix as A

T = json.load(open(os.path.join(A.ROOT, "pipeline", "audio_cues_v1.json"), encoding="utf-8"))
T = T.get("tracks") or T.get("stems") or {}
ev = T.get("dialogue", {}).get("events", [])
blk, ap = [], []
print("对白句数=%d" % len(ev))
out = A.build_group("DLG", ev, lambda e: os.path.join(A.PB, "audio", "dialogue", e["line"] + ".mp3"),
                    A.dlg_chain, "stem_dialogue.wav", blk, ap)
print("build_group 返回:", out, "| blk:", blk[:3])
p = os.path.join(A.WORK, "stem_dialogue.wav")
if os.path.exists(p):
    m = subprocess.run([A.FF, "-hide_banner", "-nostats", "-i", p, "-af",
                        "loudnorm=I=-14:TP=-1.5:LRA=11:print_format=json", "-f", "null", "-"],
                       capture_output=True, text=True, encoding="utf-8", errors="replace")
    g = re.search(r"\{[^{}]*input_i[^{}]*\}", m.stderr or "", re.S)
    print("INPUT_I/INPUT_TP 原文:", (g.group(0).replace("\n", " ").replace("  ", " ") if g else (m.stderr or "")[-260:]))

