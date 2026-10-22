# -*- coding: utf-8 -*-
import json, os, sqlite3, collections, hashlib
sys_root = r"D:\aifilmteam\AI影视团队v2"
proj = os.path.join(sys_root, "projects", "雨夜寻猫")

print("=== K13 versions.json ===")
v = json.load(open(os.path.join(proj, "locks", "k13_locked", "versions.json"), encoding="utf-8"))
vs = v.get("versions", [])
print("versions:", len(vs), "assets:", len(v.get("assets", {})))
tc = collections.Counter(x.get("asset_type") for x in vs)
print("by type:", dict(tc))
prompts = [ (x.get("params") or {}).get("prompt") for x in vs ]
print("with prompt:", sum(1 for p in prompts if p))
seeds = [ (x.get("params") or {}).get("seed") for x in vs ]
print("with seed:", sum(1 for s in seeds if s is not None))
print("sample params keys:", sorted(((vs[0].get("params") or {}).keys()) if vs else []))
print("sample:", json.dumps(vs[0], ensure_ascii=False)[:600])

print("\n=== storyboard prompts ===")
sb = json.load(open(os.path.join(proj,"00_brief","storyboard","雨夜寻猫_分镜表_v1.json"), encoding="utf-8"))
scenes = sb.get("scenes") or []
allshots=[]
for sc in scenes:
    for s in sc.get("shots") or []:
        allshots.append(s)
print("scenes:", len(scenes), "shots:", len(allshots))
print("shot keys:", sorted(allshots[0].keys()) if allshots else [])
print("with prompt:", sum(1 for s in allshots if s.get("prompt")))
print("with ref:", sum(1 for s in allshots if s.get("reference_image")))
plens=[len(s.get("prompt") or "") for s in allshots]
print("prompt len min/max/avg:", min(plens), max(plens), round(sum(plens)/len(plens),1))

print("\n=== crew_bus.db ===")
db = os.path.join(sys_root, "runtime", "crew_bus.db")
if os.path.exists(db):
    c = sqlite3.connect(db); c.row_factory=sqlite3.Row
    print("tables:", [r[0] for r in c.execute("SELECT name FROM sqlite_master WHERE type='table'")])
    try:
        n = c.execute("SELECT COUNT(*) FROM events").fetchone()[0]
        print("events:", n)
        for r in c.execute("SELECT type, COUNT(*) c FROM events GROUP BY type ORDER BY c DESC"):
            print("  ", r["type"], r["c"])
        for r in c.execute("SELECT * FROM events ORDER BY seq LIMIT 5"):
            print("  first:", dict(r))
    except Exception as e:
        print("events err:", e)
    try:
        print("consumers:", [dict(r) for r in c.execute("SELECT * FROM consumers")])
    except Exception as e:
        print("consumers err:", e)
    c.close()
else:
    print("no crew_bus.db at", db)

print("\n=== jobs.db ===")
for p in [os.path.join(sys_root,"pipeline","jobs.db"), os.path.join(sys_root,"runtime","jobs.db")]:
    if os.path.exists(p):
        c=sqlite3.connect(p); c.row_factory=sqlite3.Row
        print("found:", p)
        print("tables:", [r[0] for r in c.execute("SELECT name FROM sqlite_master WHERE type='table'")])
        try:
            print("jobs count:", c.execute("SELECT COUNT(*) FROM jobs").fetchone()[0])
            for r in c.execute("SELECT * FROM jobs LIMIT 3"):
                print("  ", dict(r))
        except Exception as e: print("err", e)
        c.close()

print("\n=== jobs.py idem ===")
print(open(os.path.join(sys_root,"tools","jobs.py"), encoding="utf-8").read()[:0] or "")
