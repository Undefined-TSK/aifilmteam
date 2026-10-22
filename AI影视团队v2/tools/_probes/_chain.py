import os,subprocess,sys
os.chdir(r"D:\ai_film_projects")
for a in [[r"pipeline\audio_mix.py"],[r"pipeline\audio_mix.py","--mux"],[r"tools\qc_media.py",r"projects\雨夜寻猫\output\tech_v5\雨夜寻猫_v5_tech.mkv",r"projects\雨夜寻猫\output\tech_v5\qc_final.json","--shot","4-1"]]:
    r=subprocess.run([sys.executable,"-X","utf8"]+a,capture_output=True,text=True,encoding="utf-8",errors="replace")
    print("\n#### "+" ".join(a)+" exit=%d"%r.returncode)
    print(((r.stdout or "")+(r.stderr or ""))[-1400:])

