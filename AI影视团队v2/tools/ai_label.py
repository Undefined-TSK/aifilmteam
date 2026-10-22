"""AI 双标识工具（GB 45438-2025 落地）：显式 overlay + 隐式 matroska 元数据

规格唯一来源：spec/delivery_spec.json → ai_label 段（本脚本不自行发明数值）。
- 显式：片头 3 秒「本片由 AI 生成合成」overlay（title_safe 区）
- 隐式：写 matroska 5 键（comment/aigc_label/aigc_service/aigc_provider_id/aigc_generated_at）
        MP4 会丢自定义键 → 交付版容器用 .mkv（R3 定稿 + 旧项目 ffprobe 实测）
"""
import argparse
import json
import subprocess
import sys
from datetime import datetime
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]
# 维度25：ffmpeg 改由 config/paths.py 中心化解析（原硬编码 C:\Users\LZH\...）
sys.path.insert(0, str(PROJECT_ROOT))
from config.paths import ffmpeg as _ffmpeg  # noqa: E402
SPEC = json.load(open(PROJECT_ROOT / "spec" / "delivery_spec.json", encoding="utf-8"))
AI = SPEC["ai_label"]

# Windows 常见中文字体（drawtext 需要字体文件路径；找不到则报错提示）
FONT_CANDIDATES = [
    r"C:\Windows\Fonts\msyh.ttc",   # 微软雅黑
    r"C:\Windows\Fonts\msyhbd.ttc",
    r"C:\Windows\Fonts\simhei.ttf",  # 黑体
]

def find_ffmpeg():
    """完整构建优先（config/paths.ffmpeg 已内建 Gyan 完整版优先 + 环境变量覆盖）。"""
    return _ffmpeg()

def explicit_args(ff, w, h):
    """片头 min_duration_s 的显式 overlay（drawtext，title_safe 顶部）"""
    font = next((p for p in FONT_CANDIDATES if Path(p).exists()), None)
    if not font:
        sys.exit("未找到中文字体（msyh/simhei），请安装或补充 FONT_CANDIDATES")
    e = AI["explicit"]
    y = int(h * e["y_pct_start_of_frame"]) if h else None
    # filtergraph 转义（ffmpeg 8.x 实测）：正斜杠路径 + 冒号转义 + 单引号包裹
    font_esc = "'" + font.replace("\\", "/").replace(":", "\\:") + "'"
    text = e["text"]
    fs = max(e["font_min_px"], int(h * 0.05))
    return [ff, "-y", "-hide_banner", "-loglevel", "error", "-i", "%INPUT%",
            "-vf", f"drawtext=fontfile={font_esc}:text='{text}':x=(w-text_w)/2:y={y}"
                   f":fontsize={fs}:fontcolor=white:"
                   f"box=1:boxcolor=black@0.5:boxborderw=12:enable='lt(t,{e['min_duration_s']})'"]

def main():
    p = argparse.ArgumentParser(description="GB 45438-2025 AI 双标识（显式 overlay + 隐式 mkv 元数据）")
    p.add_argument("input", help="输入视频（MP4/MOV/…）")
    p.add_argument("output", help="输出 .mkv（交付版容器，MP4 会丢隐式键）")
    p.add_argument("--provider", default="cineast_pipeline_v1",
                   help="aigc_provider_id（引擎链标识，如 kling3_omni+wan2.2_local）")
    p.add_argument("--probe", action="store_true", help="仅校验输入并输出规格，不执行")
    args = p.parse_args()

    ff = find_ffmpeg()
    if not ff:
        sys.exit("未找到 ffmpeg（Gyan 构建，见 build_mix.py 的 FF 路径）")

    # 取分辨率（overlay y 坐标需要 h）
    probed = subprocess.run([ff, "-hide_banner", "-i", args.input],
                            capture_output=True, text=True, errors="replace")
    import re
    m = re.search(r"(\d{2,5})x(\d{2,5})", probed.stderr or "")
    w, h = (int(m.group(1)), int(m.group(2))) if m else (1280, 720)

    if args.probe:
        print(f"输入: {args.input} ({w}x{h})")
        print("显式:", AI["explicit"]["text"], f"≥{AI['explicit']['min_duration_s']}s",
              f"y={int(h*AI['explicit']['y_pct_start_of_frame'])}px font≥{AI['explicit']['font_min_px']}px")
        print("隐式键:", ", ".join(AI["implicit_metadata_keys"]))
        return

    out = Path(args.output)
    if out.suffix.lower() != ".mkv":
        print(f"⚠️ 输出 {out.name} 非 .mkv：MP4 会静默丢弃 aigc_* 自定义键（R3 定稿 + 旧项目实测）")
    out.parent.mkdir(parents=True, exist_ok=True)

    meta = {
        "comment": "AIGC",
        "aigc_label": AI["explicit"]["text"],
        "aigc_service": "cineast_pipeline_v1",
        "aigc_provider_id": args.provider,
        "aigc_generated_at": datetime.now().strftime("%Y-%m-%d"),
    }
    cmd = explicit_args(ff, w, h) + ["-map", "0:v:0", "-map", "0:a:0?"]
    for k, v in meta.items():
        cmd += ["-metadata", f"{k}={v}"]
    cmd += ["-c:v", "libx264", "-crf", "18", "-c:a", "copy", "-movflags", "+faststart", str(out)]
    src = str(args.input)
    cmd = [src if a == "%INPUT%" else a for a in cmd]
    subprocess.run(cmd, check=True)
    print(f"✅ 双标识完成: {out}（{w}x{h}）")
    print("   隐式元数据:", json.dumps(meta, ensure_ascii=False))

if __name__ == "__main__":
    main()
