import json
from pathlib import Path

LOCK_DIR = Path(r"D:\ai_film_projects\projects\雨夜寻猫\character_lock")

for name in ["小白", "林小雨"]:
    p = LOCK_DIR / f"{name}.json"
    data = json.loads(p.read_text(encoding="utf-8"))
    notes = data.get("notes", "")
    marker = "；三视图补全"
    if marker in notes:
        data["notes"] = notes.split(marker)[0]
        p.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")
        print(f"{name}: notes 截断回原始 -> {data['notes'][:40]}...")
    else:
        print(f"{name}: 无需处理")
