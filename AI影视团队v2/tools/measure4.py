import glob, hashlib, json, os, re, subprocess, sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
# 维度25：ffmpeg 改由 config/paths.py 中心化解析（原硬编码 C:\Users\LZH\...）
sys.path.insert(0, str(ROOT))
from config.paths import ffmpeg  # noqa: E402

FF = ffmpeg()
W = ROOT / "projects" / "雨夜寻猫" / "output" / "tech_v5"
for f in ("stem_ambience.wav", "stem_dialogue.wav", "stem_sfx.wav", "stem_music.wav"):
    p = os.path.join(W, f)
    ln = subprocess.run([FF, "-hide_banner", "-nostats", "-i", p, "-af",
                         "loudnorm=I=-14:TP=-1.5:LRA=11:print_format=json", "-f", "null", "-"],
                        capture_output=True, text=True, encoding="utf-8", errors="replace")
    vd = subprocess.run([FF, "-hide_banner", "-i", p, "-af", "volumedetect", "-f", "null", "-"],
                        capture_output=True, text=True, encoding="utf-8", errors="replace")
    blob = (ln.stderr or "") + (vd.stderr or "")
    g = re.search(r'"input_i"\s*:\s*"(-?[\d.]+)"', blob)
    t = re.search(r'"input_tp"\s*:\s*"(-?[\d.]+)"', blob)
    r = re.search(r"mean_volume:\s*(-?[\d.]+) dB", blob)
    x = re.search(r"max_volume:\s*(-?[\d.]+) dB", blob)
    print("%s | bytes=%s | loudnorm input_i=%s input_tp=%s | volumedetect mean=%s max=%s"
          % (f, os.path.getsize(p) if os.path.exists(p) else "MISSING",
             g.group(1) if g else "NA", t.group(1) if t else "NA",
             r.group(1) if r else "NA", x.group(1) if x else "NA"))
q = ROOT / "pipeline" / "audio_mix.py"
h = hashlib.sha256(open(q, "rb").read()).hexdigest()
print("audio_mix.py sha256[:16] = %s | bytes=%d" % (h[:16], os.path.getsize(q)))

