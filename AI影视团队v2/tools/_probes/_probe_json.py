# -*- coding: utf-8 -*-
import glob, json, sys, os
sys.stdout.reconfigure(encoding="utf-8", errors="replace")
os.chdir(r"D:\ai_film_projects\projects\雨夜寻猫")
p = glob.glob("shots/*镜头清单*.json")
print("shotlist files:", p)
d = json.load(open(p[0], encoding="utf-8"))
print("TOP", type(d).__name__, (list(d.keys())[:10] if isinstance(d, dict) else len(d)))
node = d[list(d.keys())[0]] if isinstance(d, dict) else d[0]
print("NODE", type(node).__name__, json.dumps(node, ensure_ascii=False)[:600])
if isinstance(node, list) and node:
    print("ELEM0", json.dumps(node[0], ensure_ascii=False)[:600])
v = json.load(open("k13_locked/versions.json", encoding="utf-8"))
print("VER", type(v).__name__, (list(v.keys())[:8] if isinstance(v, dict) else len(v)))
n2 = v[list(v.keys())[0]] if isinstance(v, dict) else v[0]
print("VER NODE", type(n2).__name__, json.dumps(n2, ensure_ascii=False)[:600])

