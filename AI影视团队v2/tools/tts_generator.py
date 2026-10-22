"""音效工程师TTS生成工具（合规版 v2.0）：音色候选对比 + 全片对白生成

2026-10-05 重构（A6 拍板落地）：
- 移除 edge-tts（违微软自动化条款，2026-09-25 判定必换）
- 后端 = 本地合规引擎：CosyVoice 3（首选）→ Qwen3-TTS（备选）
- 无本地模型时明确报错并给安装指引，绝不静默回落违规后端
- 路径改为 v2 现役结构（projects/雨夜寻猫/05_audio），不再硬编码旧接合点路径
"""
import argparse
import json
import shutil
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]          # AI影视团队v2
AUDIO = PROJECT_ROOT / "projects" / "雨夜寻猫" / "05_audio"
DIALOGUE_DIR = AUDIO / "dialogue"
TEST_DIR = AUDIO / "voice_test"

# 岗位卡对白清单（demo 内置，正式对白应经 --dialogues 外置文件，来源=R5 shot_spec 派生）
DIALOGUE = [
    ("1-1", "……小白？", "平静疑问"),
    ("1-3", "窗没关……它肯定出去了。", "焦虑惊觉"),
    ("1-4", "等我，我马上回来。", "决然"),
    ("2-2", "小白——小白？", "焦虑呼喊"),
    ("2-4", "不吓你，我们回家。", "失落轻哄"),
    ("3-2", "是小白的声音。", "惊喜"),
    ("3-4", "找到你了。", "释然"),
    ("3-5", "吓死我了……走，回家。", "温柔哽咽"),
]

# 本地模型路径约定（下载后放置于此；与 models/wan_vace_1.3b 同级）
COSYVOICE3_DIR = PROJECT_ROOT / "models" / "Fun-CosyVoice3-0.5B-2512"
QWEN3TTS_DIR = PROJECT_ROOT / "models" / "Qwen3-TTS"

INSTALL_HINTS = {
    "cosyvoice3": "CosyVoice 3（Fun-CosyVoice3-0.5B-2512）需下载权重放 models/，"
                  "并 pip install cosyvoice；权重许可须先读 LICENSE 终核（R0 下载后核对）",
    "qwen3-tts": "Qwen3-TTS（0.6B/1.7B，双 Apache-2.0）需下载权重放 models/，"
                 "并 pip install qwen3-tts；API 档 0.115 USD/万字符（云端最低价）",
}


class TTSBackend:
    """本地合规 TTS 后端。构造即就绪检查，不加载模型。"""
    name = "base"

    def is_ready(self):
        raise NotImplementedError

    def gen(self, text, out, **kw):
        raise NotImplementedError


class CosyVoice3Backend(TTSBackend):
    name = "cosyvoice3"

    def is_ready(self):
        return COSYVOICE3_DIR.is_dir() and shutil.which("python")

    def gen(self, text, out, emotion="中性", **kw):
        # 延迟导入：模型在则用，不在则报错（导入失败=未安装）
        try:
            from cosyvoice.cli.cosyvoice import CosyVoice3
        except ImportError:
            sys.exit(f"[{self.name}] 未安装 cosyvoice 包。{INSTALL_HINTS[self.name]}")
        model = CosyVoice3(str(COSYVOICE3_DIR))
        model.inference_zero_shot(text, emotion, str(out))  # 按 CosyVoice3 实际 API 适配


class Qwen3TTSBackend(TTSBackend):
    name = "qwen3-tts"

    def is_ready(self):
        return QWEN3TTS_DIR.is_dir()

    def gen(self, text, out, emotion="中性", **kw):
        try:
            import qwen3_tts
        except ImportError:
            sys.exit(f"[{self.name}] 未安装 qwen3-tts 包。{INSTALL_HINTS[self.name]}")
        qwen3_tts.synthesize(text=str(text), model_dir=str(QWEN3TTS_DIR), out_path=str(out))


BACKENDS = {"cosyvoice3": CosyVoice3Backend(), "qwen3-tts": Qwen3TTSBackend()}


def pick_backend(force=None):
    """auto：CosyVoice3 → Qwen3-TTS；force：指定后端（不存在则报错退出）"""
    if force:
        b = BACKENDS.get(force)
        if not b:
            sys.exit(f"未知后端: {force}（可选: auto/cosyvoice3/qwen3-tts）")
        if not b.is_ready():
            sys.exit(f"[{force}] 未就绪。{INSTALL_HINTS[force]}")
        return b
    for name in ("cosyvoice3", "qwen3-tts"):
        if BACKENDS[name].is_ready():
            return BACKENDS[name]
    sys.exit(
        "无可用本地 TTS 后端（CosyVoice3/Qwen3-TTS 均未就绪）。\n"
        + "\n".join(f"  - {hint}" for hint in INSTALL_HINTS.values())
        + "\n合规纪律：不回落 edge-tts（违微软自动化条款）。")


def load_dialogues(path=None):
    if path:
        with open(path, encoding="utf-8") as f:
            raw = json.load(f)
        if isinstance(raw, list):
            return [(d["shot"], d["line"], d.get("emotion", "中性")) for d in raw]
        return [(k, v["line"], v.get("emotion", "中性")) for k, v in raw.items()]
    return DIALOGUE


def check():
    print(f"项目根: {PROJECT_ROOT}")
    print(f"音频目录: {AUDIO}")
    for name, b in BACKENDS.items():
        print(f"后端 {name}: {'就绪' if b.is_ready() else '未就绪'}")
    if not AUDIO.is_dir():
        print(f"⚠️ {AUDIO} 不存在（R5 项目结构未建？）")


def gen_dialogue(backend, dialogues):
    DIALOGUE_DIR.mkdir(parents=True, exist_ok=True)
    for shot, line, emotion in dialogues:
        out = DIALOGUE_DIR / f"{shot}.mp3"
        backend.gen(line, out, emotion=emotion)
        print(f"[对白] {shot} [{emotion}] {line} -> {out.name}")


def gen_voice_test(backend):
    TEST_DIR.mkdir(parents=True, exist_ok=True)
    samples = [
        ("音色A_中性", "小白——小白？窗没关，它肯定出去了。等我，我马上回来。", "中性"),
        ("音色B_哽咽", "吓死我了……走，回家。", "温柔哽咽"),
    ]
    for tag, text, emotion in samples:
        out = TEST_DIR / f"{tag}.mp3"
        backend.gen(text, out, emotion=emotion)
        print(f"[试听] {tag} -> {out.name}")


def main():
    p = argparse.ArgumentParser(description="TTS 对白生成（合规版，无 edge-tts）")
    p.add_argument("mode", choices=["test", "dialogue", "check"], nargs="?", default="check",
                   help="test=音色试听 / dialogue=全片对白 / check=后端就绪检查")
    p.add_argument("--backend", choices=["auto", "cosyvoice3", "qwen3-tts"], default="auto")
    p.add_argument("--dialogues", help="对白清单 JSON 外置文件（覆盖内置 demo）")
    args = p.parse_args()

    if args.mode == "check":
        check()
        return
    backend = pick_backend(args.backend)
    print(f"[后端] {backend.name} 就绪")
    if args.mode == "test":
        gen_voice_test(backend)
    else:
        gen_dialogue(backend, load_dialogues(args.dialogues))


if __name__ == "__main__":
    main()
