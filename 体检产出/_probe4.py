# -*- coding: utf-8 -*-
import json, os, collections
v2 = r"D:\aifilmteam\AI影视团队v2"
proj = os.path.join(v2, "projects", "雨夜寻猫")

sb = json.load(open(os.path.join(proj,"00_brief","storyboard","雨夜寻猫_分镜表_v1.json"), encoding="utf-8"))
print("top keys:", list(sb.keys()))
tot = 0
for sc in sb.get("scenes") or []:
    shots = sc.get("shots") or []
    ds = sum((s.get("duration_sec") or 0) for s in shots)
    tot += ds
    print(f"  scene={sc.get('scene_no') or sc.get('scene_id') or sc.get('title')} loc={sc.get('location')} shots={len(shots)} dur={ds}s  ids={[s.get('shot_no') for s in shots]}")
print("total dur:", tot, "frames@24:", tot*24)
print("scene keys:", sorted((sb.get('scenes') or [{}])[0].keys()))

print("\n=== K13 storyboard/scene versions ===")
v = json.load(open(os.path.join(proj,"locks","k13_locked","versions.json"), encoding="utf-8"))
for x in v["versions"]:
    if x["asset_type"] in ("storyboard","scene"):
        p = x.get("params") or {}
        print(f"  [{x['asset_type']}] {x['asset_name']} uuid={x['uuid']} seed={p.get('seed')} steps={p.get('steps')} cfg={p.get('cfg')}")
        print(f"      prompt: {str(p.get('prompt'))[:130]}")

print("\n=== character_lock 小白 ===")
print(json.dumps(json.load(open(os.path.join(proj,"locks","character_lock","小白.json"), encoding="utf-8")), ensure_ascii=False, indent=1))
