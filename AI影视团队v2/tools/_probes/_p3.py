# -*- coding: utf-8 -*-
import glob, json, os, sys
sys.stdout.reconfigure(encoding="utf-8", errors="replace")
os.chdir(r"D:\ai_film_projects\projects\雨夜寻猫")
p = glob.glob(os.path.join("shots", "*.json"))
print("files:", p)
d = json.load(open(p[0], encoding="utf-8"))
print("ALL KEYS:", list(d.keys()))
for k, v in d.items():
    if isinstance(v, list):
        print(f"  LIST {k}: n={len(v)}", os.path.basename(__file__) and (json.dumps(v[0], ensure_ascii=False)[:520] if v and isinstance(v[0], dict) else v[:3]))
    elif isinstance(v, dict):
        print(f"  DICT {k}: keys={list(v)[:8]}")
    else:
        print(f"  {k} = {str(v)[:90]}")

