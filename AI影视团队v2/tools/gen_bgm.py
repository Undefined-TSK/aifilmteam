"""BGM四段程序合成：钢琴音色（泛音叠加+指数衰减），主题旋律第3场首现、第4场完整呈现"""
import subprocess
import sys
import wave
from pathlib import Path

import numpy as np

# 维度25：ffmpeg 改由 config/paths.py 中心化解析（原硬编码 C:\Users\LZH\...）
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from config.paths import ffmpeg  # noqa: E402

FF = ffmpeg()
BGM = Path(__file__).resolve().parents[1] / "projects" / "雨夜寻猫" / "audio" / "bgm"
SR = 44100

NOTE_FREQ = {
    "C3": 130.81, "Eb4": 311.13, "E3": 164.81, "F4": 349.23,
    "G3": 196.00, "A3": 220.00,
    "C4": 261.63, "D4": 293.66, "E4": 329.63, "G4": 392.00, "A4": 440.00,
}


def piano_note(freq, dur=1.8, sr=SR):
    t = np.arange(int(dur * sr)) / sr
    env = np.minimum(t / 0.008, 1) * np.exp(-2.0 * t)
    wave_ = (np.sin(2 * np.pi * freq * t)
             + 0.5 * np.sin(2 * np.pi * 2 * freq * t)
             + 0.25 * np.sin(2 * np.pi * 3 * freq * t)
             + 0.125 * np.sin(2 * np.pi * 4 * freq * t))
    return wave_ * env


def place(canvas, note, start, gain=1.0):
    idx = int(start * SR)
    end = min(idx + len(note), len(canvas))
    if idx < len(canvas):
        canvas[idx:end] += note[: end - idx] * gain


def render(name, dur, notes, pad_gain=0.0, pad_freq=110.0, pad_t=None, fade_out=None):
    """notes: [(start, note名, gain)]"""
    canvas = np.zeros(int(dur * SR))
    for start, note, gain in notes:
        place(canvas, piano_note(NOTE_FREQ[note]), start, gain)
    if pad_t:  # 低频铺底（弦乐感）
        t = np.arange(int(pad_t[1] * SR) - int(pad_t[0] * SR)) / SR
        pad = np.sin(2 * np.pi * pad_freq * t) * np.sin(np.pi * t / (pad_t[1] - pad_t[0]))
        place(canvas, pad, pad_t[0], pad_gain)
    if fade_out:
        n = int(fade_out * SR)
        canvas[-n:] *= np.linspace(1, 0, n)
    canvas = canvas / max(1e-9, np.abs(canvas).max()) * 0.6

    wav = BGM / (name + ".wav")
    with wave.open(str(wav), "w") as f:
        f.setnchannels(1)
        f.setsampwidth(2)
        f.setframerate(SR)
        f.writeframes((canvas * 32767).astype(np.int16).tobytes())

    mp3 = BGM / (name + ".mp3")
    subprocess.run([FF, "-y", "-hide_banner", "-loglevel", "error", "-i", str(wav),
                    "-b:a", "128k", str(mp3)], check=True)
    wav.unlink()
    print("生成:", mp3.name)


def main():
    BGM.mkdir(parents=True, exist_ok=True)

    # 第1场15s 平静→惊变：慢速单音→6.5s骤停静默→低音不安
    render("第1场-平静惊变", 15, [
        (0.3, "C4", 0.7), (1.8, "E4", 0.7), (3.3, "G4", 0.7), (4.8, "E4", 0.6),
        (7.5, "C3", 0.55), (9.5, "C3", 0.5), (11.5, "C3", 0.45), (13.3, "C3", 0.4),
    ])

    # 第2场20s 焦虑寻索：低音铺底+中音快速跳动（无解决）
    render("第2场-焦虑", 20, [
        (0.2, "E4", 0.5), (1.0, "F4", 0.5), (1.8, "E4", 0.5), (2.6, "Eb4", 0.5),
        (3.4, "E4", 0.45), (4.2, "F4", 0.45), (5.0, "E4", 0.45), (5.8, "D4", 0.45),
        (6.8, "E4", 0.4), (7.6, "F4", 0.4), (8.4, "Eb4", 0.4), (9.2, "D4", 0.4),
        (10.4, "E4", 0.38), (11.2, "F4", 0.38), (12.0, "E4", 0.38), (12.8, "D4", 0.38),
        (14.0, "E4", 0.35), (14.8, "F4", 0.35), (15.6, "E4", 0.35), (16.4, "D4", 0.35),
        (17.6, "E3", 0.35), (18.6, "D4", 0.3),
    ], pad_gain=0.10, pad_freq=110, pad_t=(0, 19))

    # 第3场25s 希望重现：7s稀疏寂静→主题首次呈现（对应全片42s绿眼亮起）→温暖变奏
    render("第3场-希望", 25, [
        (0.5, "C3", 0.4), (3.0, "G3", 0.35),
        (7.0, "C4", 0.75), (7.9, "E4", 0.75), (8.8, "G4", 0.8), (9.7, "A4", 0.8),
        (10.6, "G4", 0.75), (11.5, "E4", 0.7),
        (14.0, "G4", 0.65), (15.4, "E4", 0.6), (16.8, "C4", 0.6),
        (19.0, "E4", 0.5), (20.5, "G4", 0.5), (22.0, "E4", 0.45),
    ])

    # 第4场20s 温暖释然：主题完整呈现（慢速）→尾音渐弱（随雨声淡出）
    render("第4场-温暖", 20, [
        (0.2, "C4", 0.7), (1.4, "E4", 0.7), (2.6, "G4", 0.75), (3.8, "A4", 0.75),
        (5.0, "G4", 0.7), (6.2, "E4", 0.65), (7.4, "C4", 0.65),
        (9.6, "E4", 0.55), (11.0, "G4", 0.55), (12.4, "A4", 0.5),
        (14.0, "G4", 0.45), (15.6, "C4", 0.45),
    ], fade_out=5)


if __name__ == "__main__":
    main()
