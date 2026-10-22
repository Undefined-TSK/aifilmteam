import json

v = json.load(open(r"D:\ai_film_projects\projects\雨夜寻猫\k13_locked\versions.json", encoding="utf-8"))
seen = set()
for e in v["versions"]:
    key = f"{e['asset_type']}/{e['asset_name']}"
    if key in seen:
        continue
    seen.add(key)
    p = e.get("params", {})
    print("==", key, f"({e['file_name']}, {e['locked_at'][:10]})")
    print("   ", str(p.get("prompt", ""))[:200])
