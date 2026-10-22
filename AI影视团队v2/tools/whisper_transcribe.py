#!/usr/bin/env python3
"""对白/音频转写工具（剪辑师字幕轴 + 场记对白核对用）
基于 faster-whisper（CTranslate2），本地CPU推理零现金成本。
输出：同名 .srt（字幕）+ .json（分段+词级时间戳，供口型/字幕精对齐）。
用法：
  python whisper_transcribe.py <audio_path> [--model small] [--lang zh] [--outdir DIR]
模型档位：tiny/base/small/medium/large-v3（base/small 使用项目本地模型目录，其余首次使用自动经 hf-mirror 下载）
"""
import argparse
import json
import os
from pathlib import Path

os.environ.setdefault("HF_ENDPOINT", "https://hf-mirror.com")
os.environ.setdefault("HF_HUB_DISABLE_XET", "1")
os.environ.setdefault("HF_HUB_DISABLE_SYMLINKS_WARNING", "1")

from faster_whisper import WhisperModel

# 本地模型目录（迁移自 ~/.cache/huggingface，2026-10-06 整理；2026-10-15 修正根路径 D:/aifilmteam -> D:/项目/aifilmteam）
LOCAL_MODEL_DIRS = {
    "base": r"D:/项目/aifilmteam/models/faster-whisper/hub/models--Systran--faster-whisper-base/snapshots/ebe41f70d5b6dfa9166e2c581c45c9c0cfc57b66",
    "small": r"D:/项目/aifilmteam/models/faster-whisper/hub/models--Systran--faster-whisper-small/snapshots/536b0662742c02347bc0e980a01041f333bce120",
}


def fmt_ts(seconds: float) -> str:
    ms = int(round(seconds * 1000))
    h, ms = divmod(ms, 3600000)
    m, ms = divmod(ms, 60000)
    s, ms = divmod(ms, 1000)
    return f"{h:02d}:{m:02d}:{s:02d},{ms:03d}"


def transcribe(audio_path: Path, model_size: str, lang: str, outdir: Path):
    model_path = LOCAL_MODEL_DIRS.get(model_size, model_size)
    model = WhisperModel(model_path, device="cpu", compute_type="int8",
                         download_root="D:/项目/aifilmteam/models/faster-whisper")
    segments, info = model.transcribe(
        str(audio_path), language=lang, beam_size=5, word_timestamps=True, vad_filter=True
    )
    seg_list = []
    srt_lines = []
    for i, seg in enumerate(segments, 1):
        words = [
            {"w": w.word, "start": round(w.start, 3), "end": round(w.end, 3)}
            for w in (seg.words or [])
        ]
        seg_list.append(
            {
                "id": i,
                "start": round(seg.start, 3),
                "end": round(seg.end, 3),
                "text": seg.text.strip(),
                "words": words,
            }
        )
        srt_lines.append(f"{i}\n{fmt_ts(seg.start)} --> {fmt_ts(seg.end)}\n{seg.text.strip()}\n")

    outdir.mkdir(parents=True, exist_ok=True)
    stem = audio_path.stem
    srt_path = outdir / f"{stem}.srt"
    json_path = outdir / f"{stem}.json"
    srt_path.write_text("\n".join(srt_lines), encoding="utf-8")
    payload = {
        "source": str(audio_path),
        "model": model_size,
        "language": lang,
        "duration": round(info.duration, 3),
        "segments": seg_list,
    }
    json_path.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")
    return payload


def main():
    parser = argparse.ArgumentParser(description="faster-whisper 转写（SRT+JSON）")
    parser.add_argument("audio", help="音频文件路径")
    parser.add_argument("--model", default="small", help="模型档位，默认 small；生产字幕建议 large-v3")
    parser.add_argument("--lang", default="zh", help="语言，默认 zh")
    parser.add_argument("--outdir", default=None, help="输出目录，默认与音频同目录的 subtitles/")
    args = parser.parse_args()

    audio_path = Path(args.audio)
    if not audio_path.exists():
        raise SystemExit(f"音频不存在: {audio_path}")
    outdir = Path(args.outdir) if args.outdir else audio_path.parent / "subtitles"
    payload = transcribe(audio_path, args.model, args.lang, outdir)
    print(json.dumps({
        "srt": str(outdir / f"{audio_path.stem}.srt"),
        "json": str(outdir / f"{audio_path.stem}.json"),
        "segments": len(payload["segments"]),
        "text": " | ".join(s["text"] for s in payload["segments"]),
    }, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
