import subprocess
from pathlib import Path

targets = [
    r"D:\ai_film_projects\projects\雨夜寻猫\assets\test_comfyui_01.png",
    r"D:\ai_film_projects\projects\雨夜寻猫\assets\storyboards\分镜01_v1.png",
    r"D:\ai_film_projects\projects\雨夜寻猫\assets\scenes\雨夜街道_v1.png",
]
syspng = list(Path(r"C:\Windows\WebScreen").glob("*.png"))[:2] if Path(r"C:\Windows\WebScreen").exists() else []
syspng = syspng or list(Path(r"C:\Windows\Web\Wallpaper\Windows").glob("*.jpg"))[:2]
targets += [str(p) for p in syspng]

for t in targets:
    r = subprocess.run(
        ["ffprobe", "-v", "error", "-show_entries", "stream=codec_name,width",
         "-of", "csv=p=0", t],
        capture_output=True, text=True, encoding="utf-8", errors="replace",
    )
    name = Path(t).name
    print(f"{'OK ' if r.returncode == 0 else 'ERR'} {name}: {(r.stdout or r.stderr[-80:]).strip()}")
