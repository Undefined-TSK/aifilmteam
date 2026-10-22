#!/usr/bin/env python3
"""
三视图客户端（角色设计师工具链）
从 K13 锚点定调图的原始 prompt 生成侧面/背面视图，补全角色三视图
- 正面视图 = 锁定定调图本身，不重复生成
- 策略 = 剥离姿势/构图锚词 + 视图短语前置 + 新seed：
  实测教训 v1（img2img denoise 0.6）：锚点构图主导，无法转体，输出仍是正面
  实测教训 v2（同seed+末尾追加视图短语）：同噪声基底锁死原构图，末尾短语权重不足
  身份一致性靠 prompt 承载（K13先例：林小雨 v2-v5 四个不同seed同prompt形象稳定）
- generate 只出图+扣费；自检通过后用 commit 写回 character_lock（对应工作流卡片"自检→锁定"判断点）

用法：
  python three_view_client.py generate <project_path> --character 小白 [--views side,back]
      [--seed N] [--strip "锚词1,锚词2"]
  python three_view_client.py commit <project_path> --character 小白

输出目录：assets/characters/three_view/{角色名}_{view}.png + {角色名}_meta.json
预算：10点/视图（与 character/storyboard 生图同价）
"""

import argparse
import json
import random
import subprocess
import sys
from datetime import datetime
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
from comfyui_client import (
    check_status,
    download_output,
    poll_history,
    submit_workflow,
)
from character_lock_writer import read_character, write_character

CHECKPOINT = "sd_xl_base_1.0.safetensors"
COST_PER_VIEW = 10
BUDGET_SCRIPT = Path(__file__).parent / "budget_manager.py"

VIEW_PHRASES = {
    "side": "side view, full body profile, standing pose, character reference",
    "back": "back view, seen from directly behind, back of head visible, full body, standing pose, character reference",
}
# 姿势/构图锚词：与"站立侧/背面参考图"冲突，默认从锚点prompt中剥离
STRIP_DEFAULT = ["cinematic portrait", "sitting in a cardboard box", "portrait"]
# 视图反向约束：压制模型回归正面的倾向
VIEW_NEGATIVE = {
    "side": "front view, facing camera",
    "back": "front view, facing camera, face visible, eyes visible, profile, side view",
}
DEFAULT_NEGATIVE = (
    "ugly, blurry, low quality, deformed, watermark, text, "
    "multiple characters, duplicate, inconsistent design, extra limbs"
)


def get_anchor_params(project, lock_data):
    """从 K13 版本树读取锚点定调图的原始生成参数（prompt/seed/steps/cfg）"""
    index_path = project / "k13_locked" / "versions.json"
    if not index_path.exists():
        return None
    index = json.loads(index_path.read_text(encoding="utf-8"))
    anchor_name = Path(lock_data["concept_art_path"]).name
    for v in index.get("versions", []):
        if v.get("asset_type") == "character" and v.get("file_name") == anchor_name:
            p = v.get("params", {})
            inner = p.get("params") or {}
            return {
                "prompt": p.get("prompt") or lock_data.get("prompt_injection", ""),
                "seed": p.get("seed"),
                "steps": inner.get("steps") or p.get("steps") or 25,
                "cfg": inner.get("cfg") or p.get("cfg") or 7.5,
                "uuid": v.get("uuid"),
            }
    return None


def build_workflow(positive, negative, seed, steps, cfg, prefix):
    """SDXL txt2img（API格式），与 sdxl_txt2img_fixed.json 模板同构"""
    return {
        "4": {"class_type": "CheckpointLoaderSimple", "inputs": {"ckpt_name": CHECKPOINT}},
        "5": {"class_type": "EmptyLatentImage", "inputs": {"width": 1024, "height": 1024, "batch_size": 1}},
        "6": {"class_type": "CLIPTextEncode", "inputs": {"text": positive, "clip": ["4", 1]}},
        "7": {"class_type": "CLIPTextEncode", "inputs": {"text": negative, "clip": ["4", 1]}},
        "3": {"class_type": "KSampler", "inputs": {
            "seed": seed, "steps": steps, "cfg": cfg,
            "sampler_name": "dpmpp_2m", "scheduler": "karras", "denoise": 1.0,
            "model": ["4", 0], "positive": ["6", 0], "negative": ["7", 0],
            "latent_image": ["5", 0],
        }},
        "8": {"class_type": "VAEDecode", "inputs": {"samples": ["3", 0], "vae": ["4", 2]}},
        "9": {"class_type": "SaveImage", "inputs": {"filename_prefix": prefix, "images": ["8", 0]}},
    }


def strip_anchor_prompt(prompt, extra=None):
    """剥离锚点prompt中与参考图转体冲突的姿势/构图锚词"""
    words = STRIP_DEFAULT + [w.strip() for w in (extra or "").split(",") if w.strip()]
    for w in words:
        prompt = prompt.replace(w, "")
    return ", ".join(p.strip() for p in prompt.split(",") if p.strip())


def generate(project_path, args):
    start = datetime.now()
    project = Path(project_path)

    status = check_status()
    if status["status"] != "online":
        return {"error": f"ComfyUI 离线: {status.get('error', 'unknown')}"}

    lock = read_character(str(project), args.character)
    if lock.get("status") != "ok":
        return {"error": f"character_lock 未找到 {args.character}"}
    lock_data = lock["content"]

    anchor = project / lock_data["concept_art_path"]
    if not anchor.exists():
        return {"error": f"定调图不存在: {anchor}"}

    anchor_params = get_anchor_params(project, lock_data)
    if not anchor_params or anchor_params["prompt"] is None:
        return {"error": f"K13 版本树中未找到 {anchor.name} 的原始生成参数"}

    views = [v.strip() for v in args.views.split(",") if v.strip()]
    for v in views:
        if v not in VIEW_PHRASES:
            return {"error": f"未知视图 {v}，可选: {list(VIEW_PHRASES)}"}

    # 新seed（身份靠prompt承载，避免同seed锁死原构图）；同一轮各视图共用
    seed = args.seed if args.seed is not None else random.randint(0, 2**32 - 1)
    identity_prompt = strip_anchor_prompt(anchor_params["prompt"], args.strip)

    out_dir = project / "assets" / "characters" / "three_view"
    out_dir.mkdir(parents=True, exist_ok=True)

    results = {}
    prompts = {}
    for view in views:
        positive = f"{VIEW_PHRASES[view]}, {identity_prompt}"
        if args.reinforce:
            positive = f"{VIEW_PHRASES[view]}, {args.reinforce}, {identity_prompt}"
        negative = f"{DEFAULT_NEGATIVE}, {VIEW_NEGATIVE[view]}"
        if args.negative_extra:
            negative = f"{negative}, {args.negative_extra}"
        prompts[view] = {"positive": positive, "negative": negative,
                         "seed": seed, "steps": anchor_params["steps"],
                         "cfg": anchor_params["cfg"]}
        prefix = f"three_view/{args.character}_{view}"
        wf = build_workflow(positive, negative, seed,
                            anchor_params["steps"], anchor_params["cfg"], prefix)
        prompt_id, number = submit_workflow(wf)
        entry = poll_history(prompt_id)
        if entry.get("status", {}).get("status_str") == "error":
            msgs = [m for m in entry.get("status", {}).get("messages", []) if m[0] == "execution_error"]
            return {"error": f"{view} 视图生成失败", "detail": msgs[:1], "done_views": results}
        file_path, _ = download_output(entry, out_dir, f"{args.character}_{view}")
        results[view] = file_path
        subprocess.run(
            [sys.executable, str(BUDGET_SCRIPT), "spend", str(project),
             str(COST_PER_VIEW), f"生成 character/{args.character}_{view}",
             f"{args.character}_{view}"],
            check=True, capture_output=True,
        )

    # 合并式meta：支持分轮补视图（如先side后back），历史视图记录不丢
    meta_path = out_dir / f"{args.character}_meta.json"
    prev = {}
    if meta_path.exists():
        prev = json.loads(meta_path.read_text(encoding="utf-8"))
    meta = {
        **prev,
        "character": args.character,
        "engine": "sdxl_txt2img_prompt_identity",
        "checkpoint": CHECKPOINT,
        "anchor": str(anchor),
        "anchor_version_uuid": anchor_params["uuid"],
        "anchor_prompt": anchor_params["prompt"],
        "identity_prompt": identity_prompt,
        "seed": seed,
        "steps": anchor_params["steps"],
        "cfg": anchor_params["cfg"],
        "views_generated": sorted(
            set(prev.get("views_generated", []) + views),
            key=lambda v: ["front", "side", "back"].index(v)),
        "prompts": {**prev.get("prompts", {}), **prompts},
        "files": {**prev.get("files", {}), **results},
        "generated_at": start.strftime("%Y-%m-%d %H:%M:%S"),
        "cost": prev.get("cost", 0) + COST_PER_VIEW * len(views),
    }
    meta_path.write_text(json.dumps(meta, ensure_ascii=False, indent=2), encoding="utf-8")

    return {
        "status": "done",
        "character": args.character,
        "seed": seed,
        "files": results,
        "meta": str(meta_path),
        "cost": COST_PER_VIEW * len(views),
        "elapsed_sec": round((datetime.now() - start).total_seconds(), 1),
    }


def commit(project_path, args):
    """自检通过后：把三视图路径写回 character_lock JSON"""
    project = Path(project_path)
    meta_path = project / "assets" / "characters" / "three_view" / f"{args.character}_meta.json"
    if not meta_path.exists():
        return {"error": f"未找到生成记录，请先 generate: {meta_path}"}
    meta = json.loads(meta_path.read_text(encoding="utf-8"))

    lock = read_character(str(project), args.character)
    if lock.get("status") != "ok":
        return {"error": f"character_lock 未找到 {args.character}"}
    data = lock["content"]

    views = sorted(set(data.get("views", []) + ["front"] + list(meta["views_generated"])),
                   key=lambda v: ["front", "side", "back"].index(v))
    data["views"] = views
    data["three_view_paths"] = {
        "front": data["concept_art_path"],
        **{v: f"assets/characters/three_view/{args.character}_{v}.png"
           for v in meta["views_generated"]},
    }
    data["three_view_meta"] = {
        "engine": meta["engine"], "seed": meta["seed"],
        "anchor_version_uuid": meta["anchor_version_uuid"],
        "generated_at": meta["generated_at"],
    }
    note = (f"三视图补全({meta['generated_at']})：side/back由SDXL txt2img生成"
            f"（视图短语前置+剥离姿势锚词，seed {meta['seed']}，身份由prompt_injection承载），front=锁定定调图")
    data["notes"] = f"{data.get('notes', '')}；{note}" if data.get("notes") else note

    result = write_character(str(project), args.character, json.dumps(data, ensure_ascii=False))
    return {"status": "locked_with_three_views", "character": args.character,
            "views": views, "lock_result": result}


def main():
    parser = argparse.ArgumentParser(description="三视图客户端（prompt身份承载策略）")
    sub = parser.add_subparsers(dest="cmd", required=True)

    g = sub.add_parser("generate")
    g.add_argument("project_path")
    g.add_argument("--character", required=True)
    g.add_argument("--views", default="side,back")
    g.add_argument("--seed", type=int, default=None,
                   help="默认随机新seed（同seed会锁死原构图），同轮各视图共用")
    g.add_argument("--strip", default="",
                   help="额外剥离的锚词，逗号分隔（默认已含 cinematic portrait/sitting in a cardboard box/portrait）")
    g.add_argument("--reinforce", default="",
                   help="强化短语，注入视图短语之后（前置高权重位），用于压制特征漂移（如发型）")
    g.add_argument("--negative-extra", default="",
                   help="本轮附加负面词，逗号分隔（如 updo, bun, long hair）")

    c = sub.add_parser("commit")
    c.add_argument("project_path")
    c.add_argument("--character", required=True)

    args = parser.parse_args()
    if args.cmd == "generate":
        print(json.dumps(generate(args.project_path, args), ensure_ascii=False, indent=2))
    else:
        print(json.dumps(commit(args.project_path, args), ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
