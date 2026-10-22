# -*- coding: utf-8 -*-
"""comfyui_start.py — 归档区 ComfyUI 启动包装（R0-T6 最小侵入接入）

当前唯一 ComfyUI 安装位于冻结归档区
`_legacy_projects/v2-intermediate/comfyui/ComfyUI_windows_portable/`，
纪律要求不改其内部文件 → 本包装脚本只负责以正确参数启动它，不触碰任何归档内容。

职责：
  1. 定位 run_nvidia_gpu.bat（GPU 模式）并以其原生方式启动（工作目录=portable 根）；
  2. 启动前打印 vram_lock 状态（若锁被占，提示错峰——D23 分时纪律的 submit 前检查）；
  3. 可选 --lowvram / --novram 透传（ComfyUI 原生启动参数，经 set COMFYUI_ARGS 不支持时
     改用命令行透传方式：本包装直接调 python_embeded\\python.exe main.py 传参）。

用法：
  python tools/comfyui_start.py                # 常规 GPU 启动（run_nvidia_gpu.bat）
  python tools/comfyui_start.py --lowvram      # 低显存模式（12GB 卡跑 5B 模型建议）
  python tools/comfyui_start.py --wait         # 启动后阻塞轮询 /system_stats 到在线
"""
import argparse
import json
import os
import subprocess
import sys
import time
import urllib.request
from pathlib import Path

V2_ROOT = Path(__file__).resolve().parent.parent
# 归档区与 v2 根同级（AI影视团队v2/ ↔ _legacy_projects/），经 __file__ 相对推导，
# 与 vram_lock.py / jobs.py 的 ROOT 相对化修复对齐（R0-T6-P2）
PORTABLE = (V2_ROOT.parent / "_legacy_projects" / "v2-intermediate" /
            "comfyui" / "ComfyUI_windows_portable")
COMFYUI_URL = os.environ.get("COMFYUI_URL", "http://127.0.0.1:8188")
ONLINE_TIMEOUT_SEC = 300


def vram_lock_hint():
    """打印当前显存锁状态（仅提示，不强制——锁纪律由各提交端强制）。"""
    try:
        sys.path.insert(0, str(Path(__file__).parent))
        from vram_lock import status
        holder = status().get("holder")
        if holder and not holder.get("released"):
            print(f"[vram_lock] ⚠ 当前锁被占用：owner={holder.get('owner')} "
                  f"pid={holder.get('pid')}——D23 分时纪律：错峰提交")
        else:
            print("[vram_lock] 显存锁空闲")
    except Exception as e:
        print(f"[vram_lock] 状态读取失败（不影响启动）: {e}")


def main():
    ap = argparse.ArgumentParser("comfyui_start")
    ap.add_argument("--lowvram", action="store_true", help="透传 --lowvram")
    ap.add_argument("--novram", action="store_true", help="透传 --novram")
    ap.add_argument("--cpu", action="store_true", help="用 run_cpu.bat")
    ap.add_argument("--wait", action="store_true", help="启动后等待 /system_stats 在线")
    a = ap.parse_args()

    vram_lock_hint()
    if not PORTABLE.exists():
        raise SystemExit(f"ComfyUI 归档区不存在: {PORTABLE}")

    extra = []
    if a.lowvram:
        extra.append("--lowvram")
    if a.novram:
        extra.append("--novram")

    if extra or a.cpu:
        # 参数透传模式：直接调内嵌 python main.py（等效 run_nvidia_gpu.bat 的最小改法）
        py = PORTABLE / "python_embeded" / "python.exe"
        main_py = PORTABLE / "ComfyUI" / "main.py"
        cmd = [str(py), "-s", str(main_py)] + extra
        if a.cpu:
            cmd.append("--cpu")
        print(f"[comfyui_start] 启动: {cmd}\n  cwd={PORTABLE}")
        subprocess.Popen(cmd, cwd=str(PORTABLE))
    else:
        bat = PORTABLE / "run_nvidia_gpu.bat"
        print(f"[comfyui_start] 启动: {bat}\n  cwd={PORTABLE}")
        # start 语义：bat 自带 pause 行为，用独立窗口跑，本脚本立即返回
        subprocess.Popen(["cmd", "/c", "start", "", str(bat)], cwd=str(PORTABLE))

    if a.wait:
        deadline = time.time() + ONLINE_TIMEOUT_SEC
        while time.time() < deadline:
            try:
                with urllib.request.urlopen(f"{COMFYUI_URL}/system_stats", timeout=5) as r:
                    info = json.loads(r.read())
                    dev = (info.get("devices") or [{}])[0]
                    print(f"[comfyui_start] 在线: gpu={dev.get('name')} "
                          f"vram_total={round((dev.get('vram_total') or 0)/2**20)}MiB")
                    return 0
            except Exception:
                time.sleep(3)
        raise SystemExit(f"等待 {ONLINE_TIMEOUT_SEC}s 仍未在线")
    return 0


if __name__ == "__main__":
    sys.exit(main())
