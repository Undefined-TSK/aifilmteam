import json

v = json.load(open(r"D:\ai_film_projects\projects\雨夜寻猫\k13_locked\versions.json", encoding="utf-8"))
for e in v["versions"]:
    if e["asset_name"] in ("分镜01-雨夜街道远景", "雨夜街道"):
        p = e.get("params", {}) or {}
        print("==", e["asset_name"], e["asset_type"], e["uuid"], e.get("file_name", ""))
        print("   prompt:", str(p.get("prompt", ""))[:250])
        print("   seed:", p.get("seed"), "steps:", p.get("steps"), "size:", p.get("width"), "x", p.get("height"))
        print()
