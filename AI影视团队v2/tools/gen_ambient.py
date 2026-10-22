"""环境音合成：4场雨声变体（程序合成，零授权风险，覆盖1-2空猫窝的雨声风声需求）"""
import subprocess
import sys
from pathlib import Path

# 维度25：ffmpeg 改由 config/paths.py 中心化解析（原硬编码 C:\Users\LZH\...）
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from config.paths import ffmpeg  # noqa: E402

FF = ffmpeg()
AMBIENT = Path(__file__).resolve().parents[1] / "projects" / "雨夜寻猫" / "audio" / "ambient"
SEED = 20260925

# 挂钟滴答：每0.5s一个衰减脉冲，tick/tock频率交替（1600/1200Hz）
# lavfi URL中逗号必须转义为\,
TICK = "sin(2*PI*if(lt(mod(t\\,1)\\,0.5)\\,1600\\,1200)*t)*exp(-25*mod(t*2\\,1))"


def run(args, out):
    cmd = [FF, "-y", "-hide_banner", "-loglevel", "error"] + args + [str(out)]
    subprocess.run(cmd, check=True)
    print("生成:", out.name)


def stereo():
    return "pan=stereo|c0=c0|c1=c0"


def main():
    AMBIENT.mkdir(parents=True, exist_ok=True)

    # 第1场 出租屋（15s）：室内闷雨（双低通500Hz）+挂钟滴答，开场3s淡入
    run([
        "-f", "lavfi", "-i", f"anoisesrc=color=white:duration=15:amplitude=0.8:seed={SEED}",
        "-f", "lavfi", "-i", f"aevalsrc={TICK}:s=44100:d=15",
        "-filter_complex",
        "[0:a]lowpass=f=500,lowpass=f=500,volume=0.5[rain];"
        "[1:a]volume=0.10[tick];"
        "[rain][tick]amix=inputs=2:duration=first,"
        + stereo() + ",afade=t=in:d=3[out]",
        "-map", "[out]", "-ar", "44100", "-b:a", "128k",
    ], AMBIENT / "出租屋雨声.mp3")

    # 第2场 街道（20s）：开阔雨声（高通150/低通7000）+远处车流（棕噪声低频+慢颤动）
    run([
        "-f", "lavfi", "-i", f"anoisesrc=color=white:duration=20:amplitude=0.8:seed={SEED+1}",
        "-f", "lavfi", "-i", f"anoisesrc=color=brown:duration=20:amplitude=0.6:seed={SEED+2}",
        "-filter_complex",
        "[0:a]highpass=f=150,lowpass=f=7000,volume=0.62[rain];"
        "[1:a]lowpass=f=200,tremolo=f=0.3:d=0.4,volume=0.20[traffic];"
        "[rain][traffic]amix=inputs=2:duration=first,"
        + stereo() + "[out]",
        "-map", "[out]", "-ar", "44100", "-b:a", "128k",
    ], AMBIENT / "街道雨声.mp3")

    # 第3场 巷口（25s）：空旷回声感雨声（aecho延迟60ms衰减）
    run([
        "-f", "lavfi", "-i", f"anoisesrc=color=white:duration=25:amplitude=0.8:seed={SEED+3}",
        "-filter_complex",
        "[0:a]highpass=f=200,lowpass=f=6000,aecho=0.8:0.7:60:0.25,volume=0.55,"
        + stereo() + "[out]",
        "-map", "[out]", "-ar", "44100", "-b:a", "128k",
    ], AMBIENT / "巷口雨声.mp3")

    # 第4场 归途（20s）：雨声渐弱（音量线性缓降0.6→0.15）+结尾5s淡出
    run([
        "-f", "lavfi", "-i", f"anoisesrc=color=white:duration=20:amplitude=0.8:seed={SEED+4}",
        "-filter_complex",
        "[0:a]highpass=f=180,lowpass=f=6500,"
        "volume=volume='max(0.6-0.0225*t,0.15)':eval=frame,"
        + stereo() + ",afade=t=out:st=15:d=5[out]",
        "-map", "[out]", "-ar", "44100", "-b:a", "128k",
    ], AMBIENT / "雨声渐弱.mp3")


if __name__ == "__main__":
    sys.exit(main())
