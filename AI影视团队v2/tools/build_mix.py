"""剪辑师混音执行：四轨按音轨清单时码合成粗剪v3（分轨预合成→总混，amix normalize=0保留相对音量）"""
import subprocess
import sys
from pathlib import Path

# 维度25：ffmpeg/ffprobe 改由 config/paths.py 中心化解析（原硬编码 C:\Users\LZH\...，换机即失效）
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from config.paths import ffmpeg, ffprobe  # noqa: E402

FF = ffmpeg()
FP = ffprobe()
PROJ = Path(__file__).resolve().parents[1] / "projects" / "雨夜寻猫"
AUDIO = PROJ / "audio"
OUT = PROJ / "output"
TMP = AUDIO / "mix_tmp"
TOTAL = 80.0


def ff(args):
    subprocess.run([FF, "-y", "-hide_banner", "-loglevel", "error"] + args, check=True)


def probe_dur(p):
    r = subprocess.run([FP, "-v", "error", "-show_entries", "format=duration",
                        "-of", "csv=p=0", str(p)], capture_output=True, text=True)
    return float(r.stdout.strip())


def main():
    TMP.mkdir(parents=True, exist_ok=True)

    # ===== 阶段1：环境底轨（4场拼接=80s）=====
    env_files = ["出租屋雨声", "街道雨声", "巷口雨声", "雨声渐弱"]
    env_args = []
    for n in env_files:
        env_args += ["-i", str(AUDIO / "ambient" / (n + ".mp3"))]
    ff(env_args + [
        "-filter_complex", "[0:a][1:a][2:a][3:a]concat=n=4:v=0:a=1[out]",
        "-map", "[out]", "-b:a", "128k", str(TMP / "env_80s.mp3")])
    print("环境底轨:", probe_dur(TMP / "env_80s.mp3"), "s")

    # ===== 阶段2：BGM轨（4段拼接=80s）=====
    bgm_files = ["第1场-平静惊变", "第2场-焦虑", "第3场-希望", "第4场-温暖"]
    bgm_args = []
    for n in bgm_files:
        bgm_args += ["-i", str(AUDIO / "bgm" / (n + ".mp3"))]
    ff(bgm_args + [
        "-filter_complex", "[0:a][1:a][2:a][3:a]concat=n=4:v=0:a=1[out]",
        "-map", "[out]", "-b:a", "128k", str(TMP / "bgm_80s.mp3")])
    print("BGM轨:", probe_dur(TMP / "bgm_80s.mp3"), "s")

    # ===== 阶段3：对白轨（8句adelay到时点）=====
    # (文件, 进入时点ms, 对白时长)——时码来自音轨清单v1
    dialogue = [
        ("1-1", 1500), ("1-3", 6500), ("1-4", 11000), ("2-2", 20000),
        ("2-4", 29000), ("3-2", 40000), ("3-4", 46000), ("3-5", 51000),
    ]
    dial_args = []
    fc_parts = []
    for i, (shot, delay) in enumerate(dialogue):
        dial_args += ["-i", str(AUDIO / "dialogue" / f"{shot}.mp3")]
        fc_parts.append(
            f"[{i}:a]aresample=44100,aformat=channel_layouts=stereo,"
            f"adelay={delay}|{delay},apad=whole_dur={TOTAL}[d{i}]")
    fc_parts.append(
        "".join(f"[d{i}]" for i in range(len(dialogue)))
        + f"amix=inputs={len(dialogue)}:duration=longest:normalize=0[out]")
    ff(dial_args + [
        "-filter_complex", ";".join(fc_parts),
        "-map", "[out]", "-b:a", "128k", str(TMP / "dialogue_80s.mp3")])
    print("对白轨:", probe_dur(TMP / "dialogue_80s.mp3"), "s")

    # ===== 阶段4：SFX轨（9条adelay+差异化音量+踩水洼循环）=====
    # (文件名, 进入时点ms, 相对音量, 循环次数或0)
    sfx = [
        ("纸张翻动", 500, 0.30, 0),
        ("雨声穿窗", 3000, 0.40, 0),
        ("开关门", 12500, 0.50, 0),
        ("踩水洼", 15000, 0.35, 5),       # aloop×5 → 15s铺满2-1~2-3
        ("伞收起滴水", 36000, 0.30, 0),
        ("猫叫-微弱单声", 38500, 0.70, 0),  # -6dB突出：声音先于画面0.5s
        ("纸箱窸窣", 43000, 0.22, 0),
        ("布料摩擦咕噜", 47000, 0.22, 0),
        ("猫叫-应答单声", 69500, 0.70, 0),
    ]
    sfx_args = []
    fc_parts = []
    for i, (name, delay, vol, loop) in enumerate(sfx):
        sfx_args += ["-i", str(AUDIO / "sfx" / f"{name}.mp3")]
        loop_f = f"aloop=loop={loop}:size={110250}," if loop > 0 else ""
        fc_parts.append(
            f"[{i}:a]aresample=44100,aformat=channel_layouts=stereo,{loop_f}"
            f"volume={vol},adelay={delay}|{delay},apad=whole_dur={TOTAL}[s{i}]")
    fc_parts.append(
        "".join(f"[s{i}]" for i in range(len(sfx)))
        + f"amix=inputs={len(sfx)}:duration=longest:normalize=0[out]")
    ff(sfx_args + [
        "-filter_complex", ";".join(fc_parts),
        "-map", "[out]", "-b:a", "128k", str(TMP / "sfx_80s.mp3")])
    print("SFX轨:", probe_dur(TMP / "sfx_80s.mp3"), "s")

    # ===== 阶段5：总混（视频copy + 四轨amix）=====
    # 相对音量：对白0dB基准=1.0；SFX轨0.8；环境打底0.55；BGM衬底0.32
    ff([
        "-i", str(OUT / "雨夜寻猫_粗剪_v2.mp4"),
        "-i", str(TMP / "env_80s.mp3"),
        "-i", str(TMP / "bgm_80s.mp3"),
        "-i", str(TMP / "dialogue_80s.mp3"),
        "-i", str(TMP / "sfx_80s.mp3"),
        "-filter_complex",
        "[1:a]volume=0.55[env];[2:a]volume=0.32[bgm];[3:a]volume=1.0[dial];[4:a]volume=0.8[sfx];"
        "[env][bgm][dial][sfx]amix=inputs=4:duration=first:normalize=0,"
        "alimiter=limit=0.95[aout]",
        "-map", "0:v", "-map", "[aout]",
        "-c:v", "copy", "-b:a", "192k", "-ar", "44100",
        str(OUT / "雨夜寻猫_粗剪_v3.mp4")])
    d = probe_dur(OUT / "雨夜寻猫_粗剪_v3.mp4")
    size = (OUT / "雨夜寻猫_粗剪_v3.mp4").stat().st_size / 1048576
    print(f"粗剪v3: {d:.2f}s, {size:.2f}MB")


if __name__ == "__main__":
    sys.exit(main())
