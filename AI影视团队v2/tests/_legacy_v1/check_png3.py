from pathlib import Path

for p in [
    r"D:\ai_film_projects\projects\雨夜寻猫\assets\scenes\雨夜街道_v1.png",
    r"D:\ai_film_projects\projects\雨夜寻猫\assets\storyboards\分镜01_v1.png",
    r"D:\ai_film_projects\projects\雨夜寻猫\assets\scenes\雨夜街道_v2.png",
]:
    f = Path(p)
    data = f.read_bytes()[:24]
    png = data[:8] == b"\x89PNG\r\n\x1a\n"
    print(f"{f.name}: size={f.stat().st_size} magic={data[:12].hex()} isPNG={png}")
