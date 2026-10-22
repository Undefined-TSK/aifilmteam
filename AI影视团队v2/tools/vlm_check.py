#!/usr/bin/env python3
"""
场记岗 VLM 自动质检工具（Qwen3-VL-4B 本地推理）
对生成镜头帧做一致性/五官/穿帮检查，输出结构化 JSON 供"达标注记+不达标定向重生成"。

运行环境（显存约10GB，需 CUDA）：
  本机任一含 torch+transformers 的 python 均可（旧 comfyui 嵌入 python 已随归档迁移）
模型目录：<v2>/models/Qwen3-VL-4B-Instruct（首次由 hf-mirror 下载，见 tools/d1_model_queue.py）

用法：
  python vlm_check.py <image> [image2 ...] --preset consistency --anchor <锚点图>
  python vlm_check.py <image> --preset anatomy
  python vlm_check.py <image> --prompt "自由检查指令"
预设：
  consistency  与锚点图比对角色/场景一致性（需 --anchor）
  anatomy      单图五官/手部/肢体崩坏检查
  motion       单图运动伪影/重影/物体消失检查
"""
import argparse
import json
import os
import sys
from pathlib import Path

# vram_lock 全引擎接入（R0-T6）：Qwen3-VL-4B 本地 CUDA 推理（约10GB）期间独占显存锁
sys.path.insert(0, str(Path(__file__).parent))
try:
    from vram_lock import vram_lock as _vram_lock
except Exception:  # 锁模块不可用时降级为 no-op
    import contextlib as _cl

    @_cl.contextmanager
    def _vram_lock(*a, **k):
        yield

os.environ.setdefault("HF_ENDPOINT", "https://hf-mirror.com")
os.environ.setdefault("HF_HUB_DISABLE_XET", "1")

MODEL_DIR = Path(__file__).resolve().parents[1] / "models" / "Qwen3-VL-4B-Instruct"

PRESETS = {
    "anatomy": (
        "你是电影剧组场记，检查这张AI生成画面是否存在崩坏。只输出JSON："
        '{"verdict":"pass|fail","issues":[{"type":"face|hands|limbs|clothes|props|background","desc":"问题描述","severity":"high|mid|low"}]}。'
        "重点：五官是否畸形/多指断指/肢体融合/衣物物理错误/背景穿帮。没有问题就 verdict=pass、issues=[]。"
    ),
    "motion": (
        "你是电影剧组场记，检查这张视频帧是否存在运动伪影。只输出JSON："
        '{"verdict":"pass|fail","issues":[{"type":"ghosting|flicker|warp|vanishing","desc":"问题描述","severity":"high|mid|low"}]}。'
        "重点：拖影/闪烁/物体扭曲变形/主体突然消失或变形。没有问题就 verdict=pass、issues=[]。"
    ),
}
PRESETS["consistency"] = (
    "你是电影剧组场记，第一张图是锚点参考图（角色与场景的锁定标准），后面是生成结果帧。"
    "比对生成帧与锚点的一致性。只输出JSON："
    '{"verdict":"pass|fail","issues":[{"type":"character|scene|props|lighting","desc":"不一致处","severity":"high|mid|low"}]}。'
    "重点：角色五官/发型/服装是否与锚点同一人；场景布局/色调是否同一场景；关键道具是否一致。轻微镜头角度差异不算问题。"
)


def build_model():
    from transformers import AutoProcessor, Qwen3VLForConditionalGeneration

    try:
        model = Qwen3VLForConditionalGeneration.from_pretrained(
            MODEL_DIR, dtype="auto", device_map="cuda:0", attn_implementation="sdpa"
        )
    except TypeError:
        model = Qwen3VLForConditionalGeneration.from_pretrained(
            MODEL_DIR, torch_dtype="auto", device_map="cuda:0"
        )
    model.eval()
    processor = AutoProcessor.from_pretrained(MODEL_DIR)
    return model, processor


def ask(model, processor, image_paths, prompt):
    # qwen_vl_utils 的 file:// 分支对 Windows 盘符路径会留下前导斜杠，改传裸路径走 Image.open 分支
    content = [{"type": "image", "image": str(p)} for p in image_paths]
    content.append({"type": "text", "text": prompt})
    messages = [{"role": "user", "content": content}]
    from qwen_vl_utils import process_vision_info

    text = processor.apply_chat_template(messages, tokenize=False, add_generation_prompt=True)
    images, videos = process_vision_info(messages)
    inputs = processor(text=[text], images=images, videos=videos, padding=True, return_tensors="pt").to(model.device)
    out = model.generate(**inputs, max_new_tokens=768, do_sample=False)
    trimmed = [o[len(i):] for i, o in zip(inputs.input_ids, out)]
    return processor.batch_decode(trimmed, skip_special_tokens=True, clean_up_tokenization_spaces=False)[0]


def parse_json(text):
    text = text.strip()
    start = text.find("{")
    end = text.rfind("}")
    if start == -1 or end == -1:
        return {"verdict": "parse_error", "raw": text}
    try:
        return json.loads(text[start : end + 1])
    except json.JSONDecodeError:
        return {"verdict": "parse_error", "raw": text}


def main():
    parser = argparse.ArgumentParser(description="Qwen3-VL 场记质检")
    parser.add_argument("images", nargs="+", help="待检图片（首张可为锚点图，配合 --preset consistency）")
    parser.add_argument("--preset", default="anatomy", choices=list(PRESETS))
    parser.add_argument("--anchor", default=None, help="锚点图（consistency 预设用，置于最前）")
    parser.add_argument("--prompt", default=None, help="自定义检查指令（覆盖预设）")
    parser.add_argument("--out", default=None, help="结果JSON落盘路径")
    args = parser.parse_args()

    images = [p for p in args.images if Path(p).exists()]
    if not images:
        raise SystemExit("无有效图片")
    if args.preset == "consistency":
        if not args.anchor:
            raise SystemExit("consistency 预设需要 --anchor 锚点图")
        images = [args.anchor] + images
    prompt = args.prompt or PRESETS[args.preset]

    if not Path(MODEL_DIR).exists() or not any(Path(MODEL_DIR).glob("*.safetensors")):
        raise SystemExit(f"模型未就位: {MODEL_DIR}（先执行下载脚本）")

    with _vram_lock("qwen3-vl", wait_sec=1800):  # R0-T6：模型加载+推理期间独占显存锁
        model, processor = build_model()
        raw = ask(model, processor, images, prompt)
    result = parse_json(raw)
    result = {**result, "preset": args.preset, "images": images, "raw": raw}

    text = json.dumps(result, ensure_ascii=False, indent=2)
    if args.out:
        Path(args.out).parent.mkdir(parents=True, exist_ok=True)
        Path(args.out).write_text(text, encoding="utf-8")
    print(text)


if __name__ == "__main__":
    main()
