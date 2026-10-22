
import glob, json, subprocess, os
B=glob.glob(r"C:\Users\LZH\AppData\Local\Microsoft\WinGet\Packages\Gyan.FFmpeg*\*\bin")[0]
p=os.path.join(B,"ffprobe.exe")
m=r"D:\ai_film_projects\projects\雨夜寻猫\output\tech_v5\雨夜寻猫_v5_tech.mkv"
r=subprocess.run([p,"-v","error","-show_format","-show_streams","-of","json",m],capture_output=True,text=True,encoding="utf-8",errors="replace")
d=json.loads(r.stdout)
print("FORMAT TAGS:", json.dumps(d["format"].get("tags",{}),ensure_ascii=False))
for s in d["streams"]:
    print(s["codec_type"], s.get("bit_rate"), round(int(s.get("bit_rate",0))/1000,1) if s.get("bit_rate") else None, json.dumps(s.get("tags",{}),ensure_ascii=False)[:200])

