import subprocess

FF = r"C:\Users\LZH\AppData\Local\Microsoft\WinGet\Packages\Gyan.FFmpeg.Shared_Microsoft.Winget.Source_8wekyb3d8bbwe\ffmpeg-8.1.2-full_build-shared\bin\ffmpeg.exe"
FP = r"C:\Users\LZH\AppData\Local\Microsoft\WinGet\Packages\Gyan.FFmpeg.Shared_Microsoft.Winget.Source_8wekyb3d8bbwe\ffmpeg-8.1.2-full_build-shared\bin\ffprobe.exe"

src = r"D:\ai_film_projects\projects\雨夜寻猫\assets\scenes\出租屋内_v2.png"
r = subprocess.run([FP, "-v", "error", "-show_entries", "stream=codec_name,width,height",
                   "-of", "csv=p=0", src], capture_output=True, text=True, encoding="utf-8", errors="replace")
print("probe:", r.stdout.strip() or r.stderr[-200:])

dst = r"D:\ai_film_projects\projects\雨夜寻猫\output\rough_clips\test.mp4"
vf = (
    "scale=2560:1440:force_original_aspect_ratio=increase,crop=2560:1440,"
    "zoompan=z='min(1.0+0.0006*on,1.05)':x='iw/2-(iw/zoom)/2':y='ih/2-(ih/zoom)/2'"
    ":d=90:s=1280x720:fps=30"
)
r = subprocess.run([FF, "-y", "-i", src, "-vf", vf, "-frames:v", "90",
                   "-c:v", "libx264", "-crf", "23", "-pix_fmt", "yuv420p", "-an", dst],
                  capture_output=True, text=True, encoding="utf-8", errors="replace")
print("encode rc:", r.returncode)
r2 = subprocess.run([FP, "-v", "error", "-show_entries", "format=duration",
                     "-of", "default=noprint_wrappers=1:nokey=1", dst],
                    capture_output=True, text=True)
print("test.mp4 duration:", r2.stdout.strip())
