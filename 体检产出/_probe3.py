# -*- coding: utf-8 -*-
import json, os, collections
root = r"D:\aifilmteam"
v2 = os.path.join(root, "AI影视团队v2")

print("=== master_v2.json tracks ===")
m = json.load(open(os.path.join(v2,"projects","雨夜寻猫","00_brief","timeline","master_v2.json"), encoding="utf-8"))
print("top keys:", list(m.keys()))
print("clock:", m.get("clock"))
for name, tr in (m.get("tracks") or {}).items():
    items = tr.get("items") or []
    signed = sum(1 for it in items if it.get("signoff"))
    print(f"  track={name} items={len(items)} signed={signed}")
cam = (m.get("tracks") or {}).get("camera", {}).get("items", [])
if cam:
    print("  camera item[0]:", json.dumps(cam[0], ensure_ascii=False)[:500])

print("\n=== outputs tree (cache candidates) ===")
for base in [os.path.join(root,"outputs")]:
    if os.path.isdir(base):
        for dp, dn, fn in os.walk(base):
            rel = os.path.relpath(dp, base)
            tot = sum(os.path.getsize(os.path.join(dp,f)) for f in fn if os.path.isfile(os.path.join(dp,f)))
            if fn:
                print(f"  {rel}: {len(fn)} files, {tot/1048576:.1f} MB")

print("\n=== handoff record ===")
h = json.load(open(os.path.join(v2,"projects","雨夜寻猫","00_brief","handoffs","handoff_record.json"), encoding="utf-8"))
print("type:", type(h).__name__, "keys:", list(h.keys())[:12] if isinstance(h,dict) else len(h))
if isinstance(h, dict) and "handoffs" in h:
    print("handoffs:", len(h["handoffs"]))
    for x in h["handoffs"][:3]:
        print("  ", json.dumps(x, ensure_ascii=False)[:300])
