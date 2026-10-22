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
    print(f"=== {script} {' '.join(str(a)[:34] for a in args[:3])}")
    print(out[:400] if out else f"STDERR: {err[:400]}")
    print()
    return out


s_street = {
    "prompt": "rainy street at night, neon signs, wet pavement reflections, cinematic wide angle, empty street, atmospheric perspective, cold blue-purple tone, 35mm film, high quality",
    "seed": 623059198, "steps": 20, "cfg": 7.5, "width": 1344, "height": 768,
    "model": "sd_xl_base_1.0.safetensors",
    "note": "v1/v2为0字节空文件事故，v3重新生成恢复（原prompt=rainy street night, neon signs, wet pavement reflections, cinematic, wide angle）",
}
u1 = run("k13_version_tree.py", [
    "lock", PROJ, "scene", "雨夜街道",
    r"D:\ai_film_projects\projects\雨夜寻猫\assets\scenes\雨夜街道_v3.png",
    json.dumps(s_street, ensure_ascii=False),
])

s_home = {
    "prompt": "wide shot, young Chinese woman in beige trench coat with umbrella walking on rainy street at night, small white kitten walking beside her feet on wet pavement clearly visible, kitten following her, neon lights reflections on wet ground, cinematic, 35mm film, high quality",
    "seed": 1290763498, "steps": 20, "cfg": 7.5, "width": 1344, "height": 768,
    "model": "sd_xl_base_1.0.safetensors",
    "shot_info": {"shot_no": "4-1", "shot_type": "WS", "camera_move": "tracking", "duration_sec": 8},
    "note": "原分镜01_v1.png为0字节空文件（早期生成失败占位），v2重新生成恢复；v1(75%)缺猫，v2白猫清晰可见定稿",
}
u2 = run("k13_version_tree.py", [
    "lock", PROJ, "storyboard", "分镜01-归途",
    r"D:\ai_film_projects\projects\雨夜寻猫\assets\storyboards\分镜01-归途_v2.png",
    json.dumps(s_home, ensure_ascii=False),
])

uuid1 = uuid2 = None
for u, tag in [(u1, "street"), (u2, "home")]:
    try:
        uuid_ = json.loads(u).get("uuid")
        if tag == "street":
            uuid1 = uuid_
        else:
            uuid2 = uuid_
    except Exception:
        pass

street_lock = {
    "scene_name": "雨夜街道",
    "atmosphere_keywords": ["霓虹", "雨夜", "湿滑", "冷调"],
    "lighting_direction": "霓虹招牌多色光源+地面镜面反射",
    "color_palette": {"primary": "#1a1a2e", "secondary": "#0f3460", "accent": "#e94560"},
    "memory_point": "米色风衣在冷调霓虹中的唯一暖色锚点；湿路面霓虹镜面反射",
    "camera": "广角35mm低机位",
    "concept_art_path": "assets/scenes/雨夜街道_v3.png",
    "locked_version_uuid": uuid1 or "unknown",
    "locked_at": "2026-09-25T17:42:00",
    "note": "原concept_art（v1/v2）为0字节空文件事故，v3重生成后更新引用",
}
run("scene_lock_writer.py", [PROJ, "write", "雨夜街道", json.dumps(street_lock, ensure_ascii=False)])

print("uuid street:", uuid1)
print("uuid home:", uuid2)
