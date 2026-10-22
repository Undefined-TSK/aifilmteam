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
    print(out[:400] if out else f"STDERR: {err[:400]}")
    print()
    return out


s21 = {
    "prompt": "wide shot, young Chinese woman in beige trench coat with short dark hair, holding umbrella walking fast through empty rainy street, neon signs reflections on wet pavement, cold blue-purple tone, cinematic, low angle, 35mm film, high quality",
    "seed": 133461349, "steps": 20, "cfg": 7.5,
    "width": 1344, "height": 768,
    "model": "sd_xl_base_1.0.safetensors",
    "shot_info": {"shot_no": "2-1", "shot_type": "WS", "camera_move": "tracking", "duration_sec": 4},
}
u1 = run("k13_version_tree.py", [
    "lock", PROJ, "storyboard", "分镜2-1-街道寻找",
    r"D:\ai_film_projects\projects\雨夜寻猫\assets\storyboards\分镜2-1-街道寻找_v1.png",
    json.dumps(s21, ensure_ascii=False),
])
try:
    u1 = json.loads(u1).get("uuid")
except Exception:
    u1 = None

s33 = {
    "prompt": "extreme close-up of small white kitten in cardboard box, soaked wet fur clumping, damp matted white fur with water droplets, bright green eyes reflecting warm orange streetlight glow, warm light rim on fur edges, narrow rainy alley at night with bokeh background, cinematic, shallow depth of field, 35mm film, high quality",
    "seed": 1252240033, "steps": 20, "cfg": 7.5,
    "width": 1344, "height": 768,
    "model": "sd_xl_base_1.0.safetensors",
    "shot_info": {"shot_no": "3-3", "shot_type": "ECU", "camera_move": "static", "duration_sec": 3},
}
u2 = run("k13_version_tree.py", [
    "lock", PROJ, "storyboard", "分镜3-3-绿眼亮起",
    r"D:\ai_film_projects\projects\雨夜寻猫\assets\storyboards\分镜3-3-绿眼亮起_v2.png",
    json.dumps(s33, ensure_ascii=False),
])
try:
    u2 = json.loads(u2).get("uuid")
except Exception:
    u2 = None

deliverables = {
    "storyboard_table": ["storyboard/雨夜寻猫_分镜表_v1.json", "storyboard/雨夜寻猫_分镜表_v1.md"],
    "shots_total": "18镜（1场4+2场5+3场6+4场3），80秒",
    "reference_images": {
        "新生成并锁定": [f"分镜2-1-街道寻找_v1（uuid {u1}）", f"分镜3-3-绿眼亮起_v2（uuid {u2}）"],
        "沿用已锁": ["分镜01（2b21ef79）→4-1", "分镜02（1028cfdc）→3-1"],
        "待定": "1-2空猫窝特写（SD出猫偏差，文字描述为准，成片剪辑层控制）",
    },
    "lock_injection": "林小雨13镜/小白7镜/场景lock全覆盖，手动复制特征0处",
    "budget_spent": "50点（3张首生成+2张重生成，剩620）",
}
run("handoff_manager.py", [
    PROJ, "create", "storyboard_artist", "animator",
    "分镜表v1交付-18镜完整指令",
    "雨夜寻猫分镜v1完成：18镜五要素+完整prompt（lock注入），4张分镜图已锁K13",
    json.dumps(deliverables, ensure_ascii=False),
    "按分镜表逐镜生成动态画面（16:9），景别/运镜/时长按表执行",
])
print("UUID_2-1:", u1)
print("UUID_3-3:", u2)
