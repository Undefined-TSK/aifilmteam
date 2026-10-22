# -*- coding: utf-8 -*-
"""config/paths.py — AI影视团队v2 路径统一入口（R0 规划书 §A.10 规范落地）

规则（v2 规范）：
  - 全项目禁止字面量根路径（[A-Za-z]:\\ 字面量即违规）；
  - 现役脚本一律 from config.paths import ... 取路径；
  - 仅本文件允许出现根推导，其余文件用本模块结果。

2026-10-05 创建（债务3 清单与代码漂移）：旧接合点 D:\\ai_film_projects 已归档
（D:\\_ai_film_legacy_2026\\ai_film_projects），旧字面量路径全部断链；本文件
统一收敛到新根 D:\\aifilmteam\\AI影视团队v2。
"""
from pathlib import Path
import glob as _glob
import os as _os
import shutil as _shutil

ROOT = Path(__file__).resolve().parents[1]          # AI影视团队v2（新根）
PROJECTS = ROOT / "projects"
PROJ = PROJECTS / "雨夜寻猫"                         # 当前唯一在制项目
PIPELINE = ROOT / "pipeline"
TOOLS = ROOT / "tools"
SPECS = ROOT / "spec"
ASSETS = ROOT / "assets"
RUNTIME = ROOT / "runtime"
LOGS = ROOT / "logs"
TESTS = ROOT / "tests"
WEB = ROOT / "web"
MODELS = ROOT / "models"


def project(name="雨夜寻猫"):
    """按项目名取 projects/<name>，默认当前在制片。"""
    return PROJECTS / name


# ---------------------------------------------------------------- FFmpeg 解析
# 维度25：原 9 个工具各自硬编码 C:\Users\LZH\...\Gyan.FFmpeg...，换机即失效。
# 注意：TRAE 自带 ffmpeg 为精简版（缺 matroska muxer / libx264），因此
#       探测顺序必须「完整构建优先」，不可直接用 PATH 里的第一个。
_FFMPEG_BIN_ENV = "AI_FILM_FFMPEG_BIN"
_FFMPEG_GLOBS = (
    r"%LOCALAPPDATA%\Microsoft\WinGet\Packages\Gyan.FFmpeg*\*\bin",
    r"C:\Program Files\ffmpeg*\bin",
    r"C:\ffmpeg\bin",
    r"/usr/bin",
    r"/usr/local/bin",
)


def ffmpeg_bin() -> str:
    """返回 ffmpeg 可执行所在目录。顺序：env > Gyan 完整构建 > 常见安装位 > PATH。"""
    env = _os.environ.get(_FFMPEG_BIN_ENV, "")
    if env and Path(env).is_dir():
        return str(Path(env))
    for pat in _FFMPEG_GLOBS:
        hits = sorted(_glob.glob(_os.path.expandvars(pat)))
        if hits:
            return hits[-1]
    found = _shutil.which("ffmpeg") or _shutil.which("ffmpeg.exe")
    if found:
        return str(Path(found).parent)
    raise RuntimeError(
        "找不到 ffmpeg：请设环境变量 %s 或安装 ffmpeg 到 PATH" % _FFMPEG_BIN_ENV)


def _exe(name: str) -> str:
    suffix = ".exe" if _os.name == "nt" else ""
    return str(Path(ffmpeg_bin()) / (name + suffix))


def ffmpeg() -> str:
    return _exe("ffmpeg")


def ffprobe() -> str:
    return _exe("ffprobe")


if __name__ == "__main__":
    print("ROOT      =", ROOT)
    print("PROJ      =", PROJ)
    print("ffmpeg    =", ffmpeg())
    print("ffprobe   =", ffprobe())
