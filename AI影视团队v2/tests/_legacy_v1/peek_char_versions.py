import json

v = json.load(open(r"D:\ai_film_projects\projects\雨夜寻猫\k13_locked\versions.json", encoding="utf-8"))
for e in v["versions"]:
    if "林小雨" in e.get("asset_name", "") or "流浪猫" in e.get("asset_name", ""):
        print(json.dumps({
            "uuid": e.get("uuid"),
            "asset_type": e.get("asset_type"),
            "asset_name": e.get("asset_name"),
            "file_path": e.get("file_path"),
            "locked_at": e.get("locked_at"),
            "prompt": (e.get("params", {}) or {}).get("prompt", ""),
        }, ensure_ascii=False, indent=2))
        print("---")
