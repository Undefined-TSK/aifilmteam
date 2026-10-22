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
    print(f"=== {script} {' '.join(str(a)[:36] for a in args[:3])}")
    print(out[:500] if out else f"STDERR: {err[:500]}")
    print()
    return out


# 1. K13锁定出租屋内v2（k13参数顺序：[命令, 项目路径, ...]）
params = {
    "prompt": "small apartment interior at night, wide open window with rainy night outside, white curtain blowing inward in the wind, empty round pet bed on wooden floor, no animals, warm yellow desk lamp glow on desk, cold blue light coming from window, books on desk, strong warm-cold color contrast, cinematic, 35mm film, volumetric light, high quality",
    "seed": 321270685,
    "steps": 20,
    "cfg": 7.5,
    "width": 1344,
    "height": 768,
    "model": "sd_xl_base_1.0.safetensors",
}
out = run("k13_version_tree.py", [
    "lock", PROJ, "scene", "出租屋内",
    r"D:\ai_film_projects\projects\雨夜寻猫\assets\scenes\出租屋内_v2.png",
    json.dumps(params, ensure_ascii=False),
])
uuid = None
try:
    uuid = json.loads(out).get("uuid")
except Exception:
    pass

# 2. scene_lock写入：出租屋内
apartment = {
    "scene_name": "出租屋内",
    "atmosphere_keywords": ["冷暖对比", "寂静", "丢失感"],
    "lighting_direction": "暖黄台灯主光 vs 窗外冷蓝光",
    "color_palette": {
        "primary": "#e8b04b",
        "secondary": "#3a5a8c",
        "accent": "#8b7355",
    },
    "memory_point": "开着的窗+飘动窗帘（丢失线索）；空猫窝特写为分镜层关键镜头，概念图不承载",
    "concept_art_path": "assets/scenes/出租屋内_v2.png",
    "locked_version_uuid": uuid or "unknown",
    "locked_at": "2026-09-25T17:02:00",
}
run("scene_lock_writer.py", [PROJ, "write", "出租屋内", json.dumps(apartment, ensure_ascii=False)])

# 3. scene_lock写入：雨夜巷口（基于已锁分镜02，无新生成）
alley = {
    "scene_name": "雨夜巷口",
    "atmosphere_keywords": ["湿冷", "微光", "希望"],
    "lighting_direction": "路灯暖光主光源（冷环境中的唯一暖光源，全片情绪转折点）",
    "color_palette": {
        "primary": "#16213e",
        "secondary": "#e8a87c",
        "accent": "#2b8a5a",
    },
    "memory_point": "绿眼睛在路灯暖光下亮起来（重逢瞬间）",
    "concept_art_path": "k13_locked/storyboard/分镜02-巷口寻猫/1028cfdc/分镜02-巷口寻猫_v1.png",
    "locked_version_uuid": "1028cfdc",
    "locked_at": "2026-09-25T17:02:00",
}
run("scene_lock_writer.py", [PROJ, "write", "雨夜巷口", json.dumps(alley, ensure_ascii=False)])

# 4. handoff complete
deliverables = {
    "scene_lock": ["scene_lock/出租屋内.json", "scene_lock/雨夜巷口.json"],
    "k13_locked": f"出租屋内_v2（uuid: {uuid}）",
    "concept_art": [
        "assets/scenes/出租屋内_v2.png（新生成：开窗/无猫/冷暖对比达标，猫窝特写留分镜层）",
        "雨夜巷口沿用分镜02（uuid 1028cfdc）零成本锁定",
    ],
    "budget_spent": "20点（出租屋v1叙事缺项重生成+v2定稿）",
    "consistency": "巷口色板沿用街道#16213e+路灯暖#e8a87c（与小白lock accent一致）+绿眼#2b8a5a（小白lock secondary）",
}
run("handoff_manager.py", [
    PROJ, "complete", "场景设计-20260925-E49F", "场景设计师",
    json.dumps(deliverables, ensure_ascii=False),
])
