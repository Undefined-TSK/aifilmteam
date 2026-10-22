import subprocess
import json
import sys

PY = sys.executable
TOOLS = r"D:\ai_film_projects\tools"
PROJ = r"D:\ai_film_projects\projects\雨夜寻猫"


def run(script, args):
    r = subprocess.run(
        [PY, f"{TOOLS}\\{script}"] + args,
        capture_output=True, text=True, encoding="utf-8",
    )
    out = (r.stdout or "").strip()
    err = (r.stderr or "").strip()
    print(f"=== {script} {args[0]} {args[2] if len(args) > 2 else ''}")
    print(out[:600] if out else f"STDERR: {err[:600]}")
    return out


# 1. K13锁定小白v2
params = {
    "prompt": "small white kitten with green eyes, soaked wet fur, fur clumping, water droplets on fur, sitting in a cardboard box, rainy night alleyway, warm streetlight glow, cinematic portrait, 35mm film, detailed wet fur texture, high quality",
    "seed": 1937030601,
    "steps": 20,
    "cfg": 7.5,
    "width": 1024,
    "height": 1024,
    "model": "sd_xl_base_1.0.safetensors",
}
out = run("k13_version_tree.py", [
    "lock", PROJ, "character", "小白",
    r"D:\ai_film_projects\projects\雨夜寻猫\assets\characters\小白_v2.png",
    json.dumps(params, ensure_ascii=False),
])
uuid = None
try:
    uuid = json.loads(out).get("uuid")
except Exception:
    pass

# 2. 林小雨character_lock（基于K13 v5）
lin = {
    "character_name": "林小雨",
    "feature_keywords": ["米色风衣", "深色短发", "年轻中国女性"],
    "color_palette": {"primary": "#d4c5a9", "secondary": "#2b2b2b", "accent": "#8b7355"},
    "prompt_injection": "young Chinese woman, beige trench coat, short dark hair",
    "views": ["front"],
    "expression_set": ["neutral", "anxious", "relieved", "tender"],
    "concept_art_path": "assets/characters/林小雨_v5.png",
    "locked_version_uuid": "4ef11a54",
    "locked_at": "2026-09-25T16:55:00",
    "notes": "定调图复检通过（K13 v2-v5同prompt连续锁定，形象稳定）；三视图/表情集待img2img工作流，views暂仅front",
}
run("character_lock_writer.py", ["write", PROJ, "林小雨", json.dumps(lin, ensure_ascii=False)])

# 3. 小白character_lock（基于刚锁定的v2）
cat = {
    "character_name": "小白",
    "feature_keywords": ["白色小猫", "绿眼睛", "湿毛", "幼猫体型"],
    "color_palette": {"primary": "#f5f5f0", "secondary": "#2b8a5a", "accent": "#e8a87c"},
    "prompt_injection": "small white kitten with green eyes, soaked wet fur",
    "views": ["front"],
    "expression_set": ["scared", "curious", "relieved"],
    "concept_art_path": "assets/characters/小白_v2.png",
    "locked_version_uuid": uuid or "unknown",
    "locked_at": "2026-09-25T16:55:00",
    "notes": "流浪猫v1特征继承（wet fur/green eyes）+分镜02（small white kitten）；v2定调=湿毛/绿眼/白猫全达标，纸箱属分镜层道具（分镜02已锁）不属角色本体",
}
run("character_lock_writer.py", ["write", PROJ, "小白", json.dumps(cat, ensure_ascii=False)])

# 4. handoff complete
deliverables = {
    "character_lock": ["character_lock/林小雨.json", "character_lock/小白.json"],
    "k13_locked": "小白_v2（uuid: {}）".format(uuid),
    "concept_art": ["assets/characters/小白_v2.png（新生成定调）", "assets/characters/林小雨_v5.png（复检沿用）"],
    "budget_spent": "20点（小白v1重生成+v2定稿）",
}
run("handoff_manager.py", [
    "complete", PROJ, "角色设计-20260925-54FE", "角色设计师",
    json.dumps(deliverables, ensure_ascii=False),
])
