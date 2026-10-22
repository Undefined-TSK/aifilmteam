import subprocess
import json
import sys

TOOL = r"D:\ai_film_projects\tools\character_lock_writer.py"
PROJ = r"D:\ai_film_projects\projects\雨夜寻猫"

params = {
    "feature_keywords": ["米色风衣", "黑色长发", "圆框眼镜", "帆布包"],
    "color_palette": {"primary": "#d4c5a9", "secondary": "#2b2b2b", "accent": "#8b7355"},
    "prompt_injection": "young woman, beige trench coat, long black hair, round glasses, canvas bag",
    "views": ["front", "side", "back"],
    "concept_art_path": "assets/characters/林小雨_v5.png",
}


def run(*args):
    r = subprocess.run([sys.executable, TOOL, PROJ, *args],
                       capture_output=True, text=True, encoding="utf-8")
    return json.loads(r.stdout)


# write
w = run("write", "林小雨", json.dumps(params, ensure_ascii=False))
assert w["status"] == "locked", w
print("write OK ->", w["path"])

# read
r = run("read", "林小雨")
assert r["status"] == "ok" and r["content"]["prompt_injection"].startswith("young woman")
print("read OK ->", r["content"]["feature_keywords"])

# list
l = run("list")
assert l["total"] == 1 and l["characters"][0]["character_name"] == "林小雨"
print("list OK ->", l["total"], "个角色")

# remove（清掉测试数据，留空目录）
d = run("remove", "林小雨")
assert d["status"] == "removed"
print("remove OK")
print("PASS: character_lock_writer 全部通过")
