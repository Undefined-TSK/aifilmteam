import json
import sys
from pathlib import Path

sys.path.insert(0, r"D:\ai_film_projects\tools")
from k13_version_tree import lock_version

PROJ = r"D:\ai_film_projects\projects\雨夜寻猫"

for name in ["小白", "林小雨"]:
    meta_path = Path(PROJ) / "assets" / "characters" / "three_view" / f"{name}_meta.json"
    meta = json.loads(meta_path.read_text(encoding="utf-8"))
    for view, p in meta["prompts"].items():
        params = {
            "view": view,
            "engine": meta["engine"],
            "prompt": p["positive"],
            "negative": p["negative"],
            "seed": p.get("seed", meta.get("seed")),
            "steps": p.get("steps", meta.get("steps")),
            "cfg": p.get("cfg", meta.get("cfg")),
            "anchor_version_uuid": meta["anchor_version_uuid"],
            "identity_prompt": meta["identity_prompt"],
        }
        lock_version(PROJ, "character", name, meta["files"][view],
                     json.dumps(params, ensure_ascii=False))
