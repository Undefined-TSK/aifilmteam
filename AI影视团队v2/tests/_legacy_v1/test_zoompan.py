import subprocess

src = r"D:\ai_film_projects\projects\雨夜寻猫\assets\scenes\出租屋内_v2.png"
dst = r"D:\ai_film_projects\projects\雨夜寻猫\output\rough_clips\test.mp4"
vf = (
    "scale=2560:1440:force_original_aspect_ratio=increase,crop=2560:1440,"
    "zoompan=z='min(1.0+0.0006*on,1.05)':x='iw/2-(iw/zoom)/2':y='ih/2-(ih/zoom)/2'"
    ":d=90:s=1280x720:fps=30"
)
cmd = [
    "ffmpeg", "-y", "-i", src, "-vf", vf, "-frames:v", "90",
    "-c:v", "libx264", "-crf", "23", "-pix_fmt", "yuv420p", "-an", dst,
]
r = subprocess.run(cmd, capture_output=True, text=True, encoding="utf-8", errors="replace")
print("returncode:", r.returncode)
print((r.stderr or "")[-500:])
