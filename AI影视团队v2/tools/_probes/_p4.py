# -*- coding: utf-8 -*-
import json, os, sys
sys.stdout.reconfigure(encoding="utf-8", errors="replace")
p = r"D:\ai_film_projects\projects\雨夜寻猫\shots\雨夜寻猫_镜头清单_v1.json"
d = json.load(open(p, encoding="utf-8"))
print("TYPE", type(d).__name__, "KEYS", list(d)[:14])
for k, v in d.items():
    if isinstance(v, list) and v:
        print("LIST", k, "n=", len(v))
        print("  E0", json.dumps(v[0], ensure_ascii=False)[:520])
    elif isinstance(v, dict) and k not in ("stats", "generation_params"):
        print("DICT", k, list(v)[:6], json.dumps(list(v.values())[:1], ensure_ascii=False)[:300])

