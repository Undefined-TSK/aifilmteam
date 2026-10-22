import subprocess
from pathlib import Path

FFBIN = Path(r"C:\Users\LZH\AppData\Local\Microsoft\WinGet\Packages\Gyan.FFmpeg.Shared_Microsoft.Winget.Source_8wekyb3d8bbwe\ffmpeg-8.1.2-full_build-shared\bin")
FF = str(FFBIN / "ffmpeg.exe")
FP = str(FFBIN / "ffprobe.exe")

PROJ = Path(r"D:\ai_film_projects\projects\雨夜寻猫")
ASSETS = PROJ / "assets"
WORK = PROJ / "output" / "rough_clips"
OUT = PROJ / "output" / "雨夜寻猫_粗剪_v1.mp4"
WORK.mkdir(parents=True, exist_ok=True)

FPS = 30
W, H = 1280, 720
CX = "iw/2-(iw/zoom)/2"
CY = "ih/2-(ih/zoom)/2"

# (镜号, 素材, 时长s, zoompan表达式, x表达式, 附加滤镜)
SHOTS = [
    ("1-1", "scenes/出租屋内_v2.png",    3, "min(1.0+0.0006*on,1.05)", CX, ""),
    ("1-2", "scenes/出租屋内_v2.png",    3, "min(1.0+0.0023*on,1.20)", CX, ""),
    ("1-3", "characters/林小雨_v5.png",  4, "1.08", "(iw-iw/zoom)*on/120", ""),
    ("1-4", "scenes/出租屋内_v2.png",    5, "max(1.15-0.0017*on,1.0)", CX, ""),
    ("2-1", "storyboards/分镜2-1-街道寻找_v1.png", 4, "1.08", "(iw-iw/zoom)*(1-on/120)", ""),
    ("2-2", "characters/林小雨_v5.png",  5, "min(1.0+0.0009*on,1.10)", CX, ""),
    ("2-3", "scenes/雨夜街道_v3.png",   4, "min(1.0+0.0013*on,1.15)", CX, ""),
    ("2-4", "scenes/雨夜街道_v3.png",   4, "min(1.0+0.0006*on,1.05)", CX, ""),
    ("2-5", "scenes/雨夜街道_v3.png",   3, "max(1.15-0.0017*on,1.0)", CX, ""),
    ("3-1", "storyboards/分镜02-巷口寻猫_v1.png", 4, "min(1.0+0.0006*on,1.05)", CX, ""),
    ("3-2", "characters/林小雨_v5.png",  3, "1.08", "(iw-iw/zoom)*(1-on/90)", ""),
    ("3-3", "storyboards/分镜3-3-绿眼亮起_v2.png", 3, "min(1.0+0.0028*on,1.25)", CX, ""),
    ("3-4", "storyboards/分镜02-巷口寻猫_v1.png", 5, "min(1.0+0.0006*on,1.07)", CX, ""),
    ("3-5", "characters/小白_v2.png",    5, "min(1.0+0.0005*on,1.06)", CX, ""),
    ("3-6", "storyboards/分镜02-巷口寻猫_v1.png", 5, "max(1.12-0.0013*on,1.0)", CX, ""),
    ("4-1", "storyboards/分镜01-归途_v2.png", 8, "1.10", "(iw-iw/zoom)*on/240", ""),
    ("4-2", "characters/林小雨_v5.png",  5, "min(1.0+0.0004*on,1.04)", CX, ""),
    ("4-3", "storyboards/分镜01-归途_v2.png", 7, "max(1.18-0.0026*on,1.0)", CX, "fade=t=out:st=5:d=2"),
]


def build(shot):
    no, rel, dur, z, x, extra = shot
    frames = dur * FPS
    src = ASSETS / rel
    dst = WORK / f"{no}.mp4"
    vf = (
        f"scale=2560:1440:force_original_aspect_ratio=increase,crop=2560:1440,"
        f"zoompan=z='{z}':x='{x}':y='{CY}':d={frames}:s={W}x{H}:fps={FPS}"
    )
    if extra:
        vf += f",{extra}"
    cmd = [
        FF, "-y", "-i", str(src),
        "-vf", vf, "-frames:v", str(frames), "-r", str(FPS),
        "-c:v", "libx264", "-crf", "23", "-pix_fmt", "yuv420p",
        "-an", str(dst),
    ]
    r = subprocess.run(cmd, capture_output=True, text=True)
    status = "OK" if r.returncode == 0 else f"FAIL {r.stderr[-300:]}"
    print(f"{no}: {dur}s {rel} -> {status}")
    return r.returncode == 0


fails = [s[0] for s in SHOTS if not build(s)]
if fails:
    print("FAILED SHOTS:", fails)
    raise SystemExit(1)

concat = WORK / "concat.txt"
concat.write_text("".join(f"file '{WORK}/{s[0]}.mp4'\n" for s in SHOTS), encoding="utf-8")
r = subprocess.run(
    [FF, "-y", "-f", "concat", "-safe", "0", "-i", str(concat),
     "-c", "copy", str(OUT)],
    capture_output=True, text=True,
)
print("CONCAT:", "OK" if r.returncode == 0 else r.stderr[-300:])

probe = subprocess.run(
    [FP, "-v", "error", "-show_entries", "format=duration",
     "-of", "default=noprint_wrappers=1:nokey=1", str(OUT)],
    capture_output=True, text=True,
)
print(f"TOTAL DURATION: {probe.stdout.strip()}s (target 80s)")
print(f"OUTPUT: {OUT}")
