"""SFX动效音合成：7条程序合成动效（MVP质量，可后续替换真实CC0采样）"""
import subprocess
import sys
from pathlib import Path

# 维度25：ffmpeg 改由 config/paths.py 中心化解析（原硬编码 C:\Users\LZH\...）
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from config.paths import ffmpeg  # noqa: E402

FF = ffmpeg()
SFX = Path(__file__).resolve().parents[1] / "projects" / "雨夜寻猫" / "audio" / "sfx"
SEED = 20260926

# lavfi URL（-i参数）内表达式逗号转义为\,；filter_complex内用普通逗号
D = "\\,"


def run(name, args):
    out = SFX / name
    cmd = [FF, "-y", "-hide_banner", "-loglevel", "error"] + args + [str(out)]
    subprocess.run(cmd, check=True)
    print("生成:", name)


def stereo():
    return "pan=stereo|c0=c0|c1=c0"


def noise(dur, seed, color="white", amp=0.8):
    return ["-f", "lavfi", "-i", f"anoisesrc=color={color}:duration={dur}:amplitude={amp}:seed={seed}"]


def main():
    SFX.mkdir(parents=True, exist_ok=True)

    # 1-2镜专用：雨声穿窗+风声（拍板方案：1-2空猫窝补雨声/风声）
    run("雨声穿窗.mp3", noise(3, SEED) + [
        "-filter_complex",
        f"[0:a]highpass=f=800,lowpass=f=6000,tremolo=f=0.5:d=0.5,volume=0.5,{stereo()}[out]",
        "-map", "[out]", "-ar", "44100", "-b:a", "128k",
    ])

    # 踩水洼（2.5s）：三步水花（高通300Hz白噪声短促衰减）
    run("踩水洼.mp3", noise(2.5, SEED + 1) + [
        "-filter_complex",
        f"[0:a]highpass=f=300,lowpass=f=4000,"
        "volume=volume='0.9*exp(-12*mod(t,0.8))+0.05':eval=frame,volume=0.7,"
        + stereo() + "[out]",
        "-map", "[out]", "-ar", "44100", "-b:a", "128k",
    ])

    # 开关门（2s）：关门低频砰（50Hz+快衰减）+脚步远去（低通白噪声衰减）
    run("开关门.mp3", noise(2, SEED + 2) + [
        "-f", "lavfi", "-i",
        f"aevalsrc=sin(2*PI*55*t)*exp(-18*mod(t{D}2)):s=44100:d=2",
        "-filter_complex",
        "[0:a]lowpass=f=1200,"
        "volume=volume='(1-0.5*t)*exp(-6*mod(t,0.6))*0.5':eval=frame[step];"
        "[1:a]volume=0.8[door];"
        f"[door][step]amix=inputs=2:duration=longest,{stereo()}[out]",
        "-map", "[out]", "-ar", "44100", "-b:a", "128k",
    ])

    # 纸箱窸窣（1.5s）：中频白噪声缓起伏
    run("纸箱窸窣.mp3", noise(1.5, SEED + 3) + [
        "-filter_complex",
        f"[0:a]highpass=f=1000,lowpass=f=3500,tremolo=f=8:d=0.7,volume=0.35,"
        f"afade=t=in:d=0.1,afade=t=out:st=1.2:d=0.3,{stereo()}[out]",
        "-map", "[out]", "-ar", "44100", "-b:a", "128k",
    ])

    # 伞收起滴水（2.5s）：不规则水滴（高频正弦短脉冲）
    run("伞收起滴水.mp3", [
        "-f", "lavfi", "-i",
        f"aevalsrc=sin(2*PI*1400*t)*exp(-35*mod(t{D}0.55))+0.5*sin(2*PI*900*t)*exp(-35*mod(t+0.3{D}0.55)):s=44100:d=2.5",
        "-filter_complex",
        f"[0:a]volume=0.4,afade=t=out:st=2:d=0.5,{stereo()}[out]",
        "-map", "[out]", "-ar", "44100", "-b:a", "128k",
    ])

    # 布料摩擦+小猫咕噜（2.5s）：布料（低高通起伏）+咕噜（28Hz低频颤音调制）
    run("布料摩擦咕噜.mp3", noise(2.5, SEED + 4, "pink", 0.7) + [
        "-f", "lavfi", "-i",
        f"aevalsrc=sin(2*PI*220*t)*(0.5+0.5*sin(2*PI*28*t)):s=44100:d=2.5",
        "-filter_complex",
        "[0:a]highpass=f=500,lowpass=f=2000,tremolo=f=5:d=0.5,volume=0.25[cloth];"
        "[1:a]volume=0.30[purr];"
        f"[cloth][purr]amix=inputs=2:duration=first,afade=t=out:st=2:d=0.5,{stereo()}[out]",
        "-map", "[out]", "-ar", "44100", "-b:a", "128k",
    ])

    # 纸张翻动（1s）：高频白噪声快衰减扫频感
    run("纸张翻动.mp3", noise(1, SEED + 5) + [
        "-filter_complex",
        f"[0:a]highpass=f=2500,tremolo=f=15:d=0.8,"
        "volume=volume='0.5*exp(-2*t)+0.08':eval=frame,"
        f"afade=t=out:st=0.7:d=0.3,{stereo()}[out]",
        "-map", "[out]", "-ar", "44100", "-b:a", "128k",
    ])


if __name__ == "__main__":
    sys.exit(main())
