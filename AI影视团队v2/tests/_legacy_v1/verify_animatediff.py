#!/usr/bin/env python3
"""AnimateDiff 部署回归测试：t2v冒烟 + i2v首帧锚定全链路

前置：ComfyUI(8188)已启动且加载 AnimateDiff-Evolved + VideoHelperSuite 节点
用法：python tests/verify_animatediff.py
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent / "tools"))

import comfyui_client as cc

PROJ = r"D:\ai_film_projects\projects\雨夜寻猫"
ANCHOR = PROJ + r"\k13_locked\storyboard\分镜3-3-绿眼亮起\cd16d91b\分镜3-3-绿眼亮起_v2.png"


class Args:
    pass


def main():
    results = {}

    status = cc.check_status()
    assert status["status"] == "online", f"ComfyUI离线: {status}"
    print(f"[1/4] ComfyUI online: {status.get('gpu')}")

    a = Args()
    a.prompt = "rainy neon city street at night, cinematic"
    a.negative = ""
    a.seed = 42
    a.width, a.height = 512, 512
    a.frames, a.fps = 16, 8
    a.mode, a.denoise, a.anchor = "t2v", 1.0, None
    a.output_name = "regress_ad_t2v"
    r = cc.generate_video(PROJ, "regress_ad_t2v", a)
    assert r.get("status") == "done", f"t2v失败: {r}"
    p = Path(r["file_path"])
    assert p.exists() and p.stat().st_size > 10_000, f"t2v产物异常: {p}"
    print(f"[2/4] t2v OK: {p.name} ({r['elapsed_sec']}s)")

    a2 = Args()
    a2.prompt = "small white kitten in cardboard box, green eyes slowly opening, rain falling, warm streetlight glow"
    a2.negative = ""
    a2.seed = 42
    a2.width, a2.height = 704, 384
    a2.frames, a2.fps = 16, 8
    a2.mode, a2.denoise, a2.anchor = "i2v", 0.65, ANCHOR
    r2 = cc.generate_video(PROJ, "regress_ad_i2v", a2)
    assert r2.get("status") == "done", f"i2v失败: {r2}"
    p2 = Path(r2["file_path"])
    assert p2.exists() and p2.stat().st_size > 10_000, f"i2v产物异常: {p2}"
    print(f"[3/4] i2v OK: {p2.name} ({r2['elapsed_sec']}s)")

    print("[4/4] ALL PASS")
    print(f"t2v: {r['file_path']}")
    print(f"i2v: {r2['file_path']}")


if __name__ == "__main__":
    main()
