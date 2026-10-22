from pathlib import Path

p = Path(r"D:\ai_film_projects\projects\雨夜寻猫\assets\scenes\出租屋内_v2.png")
data = p.read_bytes()[:32]
print("size:", p.stat().st_size)
print("magic:", data[:16].hex())
print("is PNG:", data[:8] == b"\x89PNG\r\n\x1a\n")

import subprocess
r = subprocess.run(
    ["ffprobe", "-v", "error", "-show_entries", "stream=codec_name,width,height",
     "-of", "default=noprint_wrappers=1", str(p)],
    capture_output=True, text=True, encoding="utf-8", errors="replace",
)
print("ffprobe rc:", r.returncode)
print(r.stdout or r.stderr[-300:])
