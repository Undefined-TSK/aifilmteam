#!/usr/bin/env python3
"""填充雨夜寻猫项目数据 — 预算+资产+交接+K13版本+场景锁定"""
import subprocess
import sys
import os
import json
from pathlib import Path

TOOLS_DIR = Path(__file__).parent
PROJECT_PATH = TOOLS_DIR.parent / "projects" / "雨夜寻猫"
PYTHON = sys.executable

sys.path.insert(0, str(TOOLS_DIR))
from handoff_manager import HandoffManager
from scene_lock_writer import write_scene


def cli(tool_name, args):
    """调用CLI工具，返回解析后的JSON"""
    script = str(TOOLS_DIR / f"{tool_name}.py")
    result = subprocess.run(
        [PYTHON, script] + args,
        capture_output=True, text=True, timeout=30, encoding="utf-8"
    )
    try:
        return json.loads(result.stdout)
    except json.JSONDecodeError:
        return {"error": result.stdout[:500]}


def seed_budget():
    print("=== 预算数据 ===")
    cli("budget_manager", ["set", str(PROJECT_PATH), "500"])
    spends = [
        ["30", "角色生成-雨夜少女", "雨夜少女"],
        ["25", "角色生成-流浪猫", "流浪猫"],
        ["40", "场景生成-雨夜街道", "雨夜街道"],
        ["45", "场景生成-梦境花园", "梦境花园"],
        ["60", "分镜生成-8镜头", "分镜01-08"],
    ]
    for s in spends:
        cli("budget_manager", ["spend", str(PROJECT_PATH)] + s)
    status = cli("budget_manager", ["status", str(PROJECT_PATH)])
    print(f"  总预算: {status.get('total_budget')} | 已支出: {status.get('spent')} | 剩余: {status.get('remaining')} | 使用率: {status.get('used_percent')}%")


def seed_assets():
    print("\n=== 资产数据 ===")
    assets = [
        ["character", "雨夜少女", "[]"],
        ["character", "流浪猫", "[]"],
        ["scene", "雨夜街道", '["雨夜少女"]'],
        ["scene", "梦境花园", '["雨夜少女","流浪猫"]'],
        ["storyboard", "分镜01-雨夜街道远景", '["雨夜街道"]'],
        ["storyboard", "分镜02-少女背影", '["雨夜街道","雨夜少女"]'],
        ["storyboard", "分镜03-猫特写", '["流浪猫"]'],
        ["storyboard", "分镜04-梦境花园全景", '["梦境花园"]'],
    ]
    for a in assets:
        cli("asset_manager", ["add", str(PROJECT_PATH)] + a)
    # Update statuses
    statuses = [
        ("雨夜少女", "locked"),
        ("流浪猫", "locked"),
        ("雨夜街道", "locked"),
        ("梦境花园", "review"),
        ("分镜01-雨夜街道远景", "generating"),
        ("分镜02-少女背影", "pending"),
        ("分镜03-猫特写", "pending"),
        ("分镜04-梦境花园全景", "pending"),
    ]
    for name, status in statuses:
        cli("asset_manager", ["update", str(PROJECT_PATH), name, "status", status])
    s = cli("asset_manager", ["status", str(PROJECT_PATH)])
    print(f"  总资产: {s.get('total')} | 进度: {s.get('progress_percent')}% | 已锁定: {s.get('locked_count')}")


def seed_handoffs():
    print("\n=== 交接记录 ===")
    hm = HandoffManager(str(PROJECT_PATH))

    h1 = hm.create_handoff(
        from_agent="编剧", to_agent="角色设计师",
        task_name="剧本定稿-雨夜寻猫",
        work_background="编剧完成剧本初稿，主角为雨夜少女和流浪猫，故事发生在雨夜街道和梦境花园",
        deliverables=["剧本文档director_intent.md", "角色列表：雨夜少女、流浪猫", "场景列表：雨夜街道、梦境花园"],
        downstream_task="角色设计与锁定",
        completion_criteria=["角色色板已定义", "角色prompt已构建", "角色已通过审核"],
        stop_conditions=["预算不足", "角色色板无法统一"]
    )
    hm.accept_handoff(h1["handoff_id"], "角色设计师")
    hm.complete_handoff(h1["handoff_id"], "角色设计师", ["角色色板.json", "雨夜少女_prompt.txt", "流浪猫_prompt.txt"])
    print(f"  交接1: 编剧->角色设计师 [已完成] ID={h1['handoff_id'][:8]}")

    h2 = hm.create_handoff(
        from_agent="角色设计师", to_agent="场景设计师",
        task_name="角色设计完成-雨夜少女+流浪猫",
        work_background="雨夜少女和流浪猫的角色设计已锁定，色板和prompt已交付",
        deliverables=["雨夜少女色板和prompt", "流浪猫色板和prompt", "角色设计审核通过记录"],
        downstream_task="场景设计（雨夜街道、梦境花园）",
        completion_criteria=["场景氛围图已生成", "光影方案已确认", "场景已锁定K13"],
        stop_conditions=["预算不足", "场景与角色色板冲突"]
    )
    hm.accept_handoff(h2["handoff_id"], "场景设计师")
    print(f"  交接2: 角色设计师->场景设计师 [进行中] ID={h2['handoff_id'][:8]}")

    h3 = hm.create_handoff(
        from_agent="场景设计师", to_agent="分镜师",
        task_name="场景锁定-雨夜街道",
        work_background="雨夜街道场景已锁定K13版本，scene_lock已写入，包含光影、色调、构图参数",
        deliverables=["雨夜街道_scene_lock.json", "ComfyUI workflow参数", "参考图3张"],
        downstream_task="分镜生成（8镜头）",
        completion_criteria=["分镜01已生成", "分镜02-08待生成", "分镜与场景一致性检查通过"],
        stop_conditions=["预算不足", "分镜质量不达标"]
    )
    hm.accept_handoff(h3["handoff_id"], "分镜师")
    print(f"  交接3: 场景设计师->分镜师 [进行中] ID={h3['handoff_id'][:8]}")

    h4 = hm.create_handoff(
        from_agent="分镜师", to_agent="制片人",
        task_name="分镜01生成中",
        work_background="分镜01（雨夜街道远景）正在ComfyUI生成中，预计30分钟完成",
        deliverables=["分镜01预览图（生成中）"],
        downstream_task="分镜01审核与锁定",
        completion_criteria=["分镜01质量达标", "分镜01已锁定K13"],
        stop_conditions=["预算不足", "生成超时"]
    )
    print(f"  交接4: 分镜师->制片人 [待检查] ID={h4['handoff_id'][:8]}")

    h5 = hm.create_handoff(
        from_agent="角色设计师", to_agent="制片人",
        task_name="角色设计被退回-流浪猫",
        work_background="流浪猫的角色设计色板与雨夜少女色调冲突，需要重新调整",
        deliverables=["流浪猫初版色板（被退回）"],
        downstream_task="流浪猫色板重新设计",
        completion_criteria=["色板冲突已解决", "新版色板已通过审核"],
        stop_conditions=["预算不足"]
    )
    hm.reject_handoff(h5["handoff_id"], "制片人", "色板与雨夜少女色调冲突，需调整对比度")
    print(f"  交接5: 角色设计师->制片人 [已退回] ID={h5['handoff_id'][:8]}")

    stats = hm.get_stats()
    print(f"  统计: 总{stats['total']} | 完成{stats['completed']} | 退回{stats['rejected']} | 进行中{stats['in_progress']}")


def seed_k13():
    print("\n=== K13版本锁定 ===")
    A = str(PROJECT_PATH / "assets")
    # Create placeholder files
    for f in ["characters/雨夜少女_v1.png", "characters/流浪猫_v1.png",
              "scenes/雨夜街道_v1.png", "scenes/雨夜街道_v2.png",
              "storyboards/分镜01_v1.png"]:
        p = Path(A) / f
        p.parent.mkdir(parents=True, exist_ok=True)
        if not p.exists():
            p.write_bytes(b"\x89PNG\r\n\x1a\n")

    versions = [
        ["character", "雨夜少女", f"{A}/characters/雨夜少女_v1.png",
         json.dumps({"prompt": "cyberpunk girl, rain night, neon lights, 18yo, black hair, red jacket", "seed": 42, "steps": 30, "cfg": 7.5})],
        ["character", "流浪猫", f"{A}/characters/流浪猫_v1.png",
         json.dumps({"prompt": "stray cat, wet fur, green eyes, alleyway, rainy night", "seed": 108, "steps": 25, "cfg": 7.0})],
        ["scene", "雨夜街道", f"{A}/scenes/雨夜街道_v1.png",
         json.dumps({"prompt": "rainy street night, neon signs, wet pavement reflections, cinematic", "seed": 256, "steps": 35, "cfg": 8.0})],
        ["scene", "雨夜街道", f"{A}/scenes/雨夜街道_v2.png",
         json.dumps({"prompt": "rainy street night, neon signs, wet pavement reflections, cinematic, wide angle", "seed": 257, "steps": 40, "cfg": 8.5})],
        ["storyboard", "分镜01-雨夜街道远景", f"{A}/storyboards/分镜01_v1.png",
         json.dumps({"prompt": "wide shot, rainy street, girl walking, cat following, neon lights", "seed": 512, "steps": 30, "cfg": 7.5})],
    ]
    for v in versions:
        result = cli("k13_version_tree", ["lock", str(PROJECT_PATH)] + v)
        uid = result.get("uuid", "?")[:8]
        print(f"  {v[1]} V1: {uid}")

    lst = cli("k13_version_tree", ["list", str(PROJECT_PATH)])
    print(f"  总版本数: {lst.get('total', '?')}")


def seed_scene_locks():
    print("\n=== 场景锁定 ===")
    s1 = write_scene(str(PROJECT_PATH), "雨夜街道", json.dumps({
        "mood": "孤寂、神秘",
        "lighting": "霓虹灯+雨幕反射，冷色调",
        "color_palette": ["#1a1a2e", "#16213e", "#0f3460", "#e94560", "#533483"],
        "composition": "三分法，街道延伸至画面深处",
        "camera": "广角35mm，低机位",
        "weather": "中雨，地面水渍反光",
        "time": "深夜23:00",
        "props": ["霓虹招牌", "垃圾桶", "路灯", "水渍"],
        "comfyui_workflow": "scene_rain_v2.json",
        "reference_count": 3
    }, ensure_ascii=False))
    print(f"  雨夜街道: {s1.get('status')}")

    s2 = write_scene(str(PROJECT_PATH), "梦境花园", json.dumps({
        "mood": "奇幻、温暖",
        "lighting": "月光+萤火虫光点，暖冷对比",
        "color_palette": ["#2d1b4e", "#1a0f2e", "#e8b949", "#5bb8b5", "#c97b63"],
        "composition": "中心对称，花园小径引导视线",
        "camera": "50mm标准镜头，平视",
        "weather": "无风，轻微雾气",
        "time": "梦境时间",
        "props": ["发光花朵", "石质小径", "古树", "萤火虫"],
        "comfyui_workflow": "scene_dream_v1.json",
        "reference_count": 2
    }, ensure_ascii=False))
    print(f"  梦境花园: {s2.get('status')}")


if __name__ == "__main__":
    seed_budget()
    seed_assets()
    seed_handoffs()
    seed_k13()
    seed_scene_locks()
    print("\n=== 数据填充完成 ===")
