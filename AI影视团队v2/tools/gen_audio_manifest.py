"""音轨清单落盘：JSON+MD双格式（音效工程师交付物）"""
import json
from datetime import datetime
from pathlib import Path

AUDIO = Path(__file__).resolve().parents[1] / "projects" / "雨夜寻猫" / "audio"

tracks = [
    # ========== 环境轨（4场打底） ==========
    {"track_no": 1, "shot_no": "1-1~1-4", "scene": 1, "track_type": "ambience",
     "file": "audio/ambient/出租屋雨声.mp3", "duration_sec": 15.0, "timecode": "0:00-0:15",
     "emotion": "室内闷雨+挂钟滴答", "fade": {"in": 3.0, "out": 1.0},
     "mix_level": "打底（-18dB）", "source": "程序合成（ffmpeg白噪声双低通500Hz+滴答aevalsrc）"},
    {"track_no": 2, "shot_no": "2-1~2-5", "scene": 2, "track_type": "ambience",
     "file": "audio/ambient/街道雨声.mp3", "duration_sec": 20.0, "timecode": "0:15-0:35",
     "emotion": "开阔雨声+远处车流", "fade": {"in": 1.5, "out": 1.5},
     "mix_level": "打底（-16dB）", "source": "程序合成（白噪声高通150低通7000+棕噪声车流）"},
    {"track_no": 3, "shot_no": "3-1~3-6", "scene": 3, "track_type": "ambience",
     "file": "audio/ambient/巷口雨声.mp3", "duration_sec": 25.0, "timecode": "0:35-1:00",
     "emotion": "空旷回声感", "fade": {"in": 1.5, "out": 1.5},
     "mix_level": "打底（-16dB，猫叫前0:39压低-6dB）", "source": "程序合成（aecho回声60ms）"},
    {"track_no": 4, "shot_no": "4-1~4-3", "scene": 4, "track_type": "ambience",
     "file": "audio/ambient/雨声渐弱.mp3", "duration_sec": 20.0, "timecode": "1:00-1:20",
     "emotion": "雨声渐弱收尾", "fade": {"in": 1.5, "out": 5.0},
     "mix_level": "打底（-16dB→-28dB渐弱）", "source": "程序合成（音量线性缓降0.6→0.15）"},

    # ========== 对白轨（8句，全片统一音色） ==========
    {"track_no": 5, "shot_no": "1-1", "scene": 1, "track_type": "dialogue",
     "file": "audio/dialogue/1-1.mp3", "duration_sec": 1.61, "timecode": "0:01.5起（镜0:00-0:03）",
     "emotion": "平静疑问", "fade": {"in": 0.1, "out": 0.2},
     "mix_level": "主导轨（0dB）", "source": "edge-tts zh-CN-XiaoyiNeural rate-5%"},
    {"track_no": 6, "shot_no": "1-3", "scene": 1, "track_type": "dialogue",
     "file": "audio/dialogue/1-3.mp3", "duration_sec": 2.74, "timecode": "0:06.5起（镜0:06-0:10）",
     "emotion": "焦虑惊觉", "fade": {"in": 0.1, "out": 0.2},
     "mix_level": "主导轨（0dB）", "source": "edge-tts rate+10% pitch+2Hz"},
    {"track_no": 7, "shot_no": "1-4", "scene": 1, "track_type": "dialogue",
     "file": "audio/dialogue/1-4.mp3", "duration_sec": 2.33, "timecode": "0:11起（镜0:10-0:15）",
     "emotion": "决然", "fade": {"in": 0.1, "out": 0.2},
     "mix_level": "主导轨（0dB）", "source": "edge-tts 默认参数"},
    {"track_no": 8, "shot_no": "2-2", "scene": 2, "track_type": "dialogue",
     "file": "audio/dialogue/2-2.mp3", "duration_sec": 2.02, "timecode": "0:20起（镜0:19-0:24）",
     "emotion": "焦虑呼喊", "fade": {"in": 0.1, "out": 0.3},
     "mix_level": "主导轨（0dB）", "source": "edge-tts rate+5% pitch+5Hz"},
    {"track_no": 9, "shot_no": "2-4", "scene": 2, "track_type": "dialogue",
     "file": "audio/dialogue/2-4.mp3", "duration_sec": 2.59, "timecode": "0:29起（镜0:28-0:32）",
     "emotion": "失落轻哄", "fade": {"in": 0.1, "out": 0.3},
     "mix_level": "主导轨（0dB）", "source": "edge-tts rate-5%"},
    {"track_no": 10, "shot_no": "3-2", "scene": 3, "track_type": "dialogue",
     "file": "audio/dialogue/3-2.mp3", "duration_sec": 1.99, "timecode": "0:40起（镜0:39-0:42）",
     "emotion": "惊喜", "fade": {"in": 0.1, "out": 0.2},
     "mix_level": "主导轨（0dB）", "source": "edge-tts rate+8% pitch+2Hz（重生成以满足时长上限）"},
    {"track_no": 11, "shot_no": "3-4", "scene": 3, "track_type": "dialogue",
     "file": "audio/dialogue/3-4.mp3", "duration_sec": 1.75, "timecode": "0:46起（镜0:45-0:50）",
     "emotion": "释然", "fade": {"in": 0.1, "out": 0.2},
     "mix_level": "主导轨（0dB）", "source": "edge-tts rate-5%"},
    {"track_no": 12, "shot_no": "3-5", "scene": 3, "track_type": "dialogue",
     "file": "audio/dialogue/3-5.mp3", "duration_sec": 3.41, "timecode": "0:51起（镜0:50-0:55）",
     "emotion": "温柔哽咽", "fade": {"in": 0.1, "out": 0.3},
     "mix_level": "主导轨（0dB）", "source": "edge-tts rate-10% pitch-2Hz"},

    # ========== 动效轨（SFX 9条） ==========
    {"track_no": 13, "shot_no": "1-1", "scene": 1, "track_type": "sfx",
     "file": "audio/sfx/纸张翻动.mp3", "duration_sec": 1.0, "timecode": "0:00.5起",
     "emotion": "伏案翻纸（微弱）", "fade": {"in": 0.05, "out": 0.3},
     "mix_level": "突出（-12dB）", "source": "程序合成（高通2500Hz白噪声快衰减）"},
    {"track_no": 14, "shot_no": "1-2", "scene": 1, "track_type": "sfx",
     "file": "audio/sfx/雨声穿窗.mp3", "duration_sec": 3.0, "timecode": "0:03-0:06（空猫窝镜全覆盖）",
     "emotion": "开窗风雨灌入（1-2空猫窝拍板方案：雨声风声打底）", "fade": {"in": 0.3, "out": 0.5},
     "mix_level": "突出（-10dB）", "timing_note": "与1-3台词'窗没关'形成听觉因果链",
     "source": "程序合成（高通800+tremolo风声感）"},
    {"track_no": 15, "shot_no": "1-4", "scene": 1, "track_type": "sfx",
     "file": "audio/sfx/开关门.mp3", "duration_sec": 2.0, "timecode": "0:12.5起（出门三连）",
     "emotion": "关门砰+脚步远去", "fade": {"in": 0.0, "out": 0.5},
     "mix_level": "突出（-8dB）", "source": "程序合成（55Hz低频砰+脚步衰减）"},
    {"track_no": 16, "shot_no": "2-1", "scene": 2, "track_type": "sfx",
     "file": "audio/sfx/踩水洼.mp3", "duration_sec": 2.5, "timecode": "0:15起（2-1起铺，全程可循环）",
     "emotion": "雨靴踩水洼", "fade": {"in": 0.2, "out": 0.3},
     "mix_level": "突出（-12dB）", "timing_note": "节奏随行走，2-1~2-5按脚步循环铺",
     "source": "程序合成（高通300Hz三步脉冲）"},
    {"track_no": 17, "shot_no": "3-1", "scene": 3, "track_type": "sfx",
     "file": "audio/sfx/伞收起滴水.mp3", "duration_sec": 2.5, "timecode": "0:36起",
     "emotion": "伞收起静→滴", "fade": {"in": 0.1, "out": 0.5},
     "mix_level": "突出（-12dB）", "source": "程序合成（1400Hz水滴脉冲不规则间隔）"},
    {"track_no": 18, "shot_no": "3-2", "scene": 3, "track_type": "sfx",
     "file": "audio/sfx/猫叫-微弱单声.mp3", "duration_sec": 1.52, "timecode": "0:38.5起（声音先于画面0.5s）",
     "emotion": "微弱猫叫（剧情关键）", "fade": {"in": 0.0, "out": 0.3},
     "mix_level": "突出（-6dB）", "timing_note": "声音先于画面：观众与林小雨同时听见（0:39镜头才切）",
     "source": "sounddino.com 'Single squeak baby'（免注册免署名，2026-09-25下载）"},
    {"track_no": 19, "shot_no": "3-3", "scene": 3, "track_type": "sfx",
     "file": "audio/sfx/纸箱窸窣.mp3", "duration_sec": 1.5, "timecode": "0:43起（绿眼亮起镜）",
     "emotion": "纸箱窸窣（轻）", "fade": {"in": 0.1, "out": 0.3},
     "mix_level": "突出（-14dB）", "source": "程序合成（中频tremolo起伏）"},
    {"track_no": 20, "shot_no": "3-4", "scene": 3, "track_type": "sfx",
     "file": "audio/sfx/布料摩擦咕噜.mp3", "duration_sec": 2.5, "timecode": "0:47起（3-4~3-5铺）",
     "emotion": "布料摩擦+小猫咕噜（温暖）", "fade": {"in": 0.2, "out": 0.5},
     "mix_level": "突出（-14dB）", "source": "程序合成（粉噪布料+28Hz颤音咕噜）"},
    {"track_no": 21, "shot_no": "4-2", "scene": 4, "track_type": "sfx",
     "file": "audio/sfx/猫叫-喵叫长段.mp3", "duration_sec": 22.73, "timecode": "0:69起取其中1声（约0:69.5-0:71）",
     "emotion": "猫叫应答（呼应3-2）", "fade": {"in": 0.0, "out": 0.3},
     "mix_level": "突出（-6dB）", "timing_note": "从22.7s长段中剪辑取材1声，混音时按分镜台词'走，回家'后0.5s进入",
     "source": "sounddino.com 'meowing kitten'（免注册免署名，2026-09-25下载）"},

    # ========== BGM（4段，待拍板） ==========
    {"track_no": 22, "scene": 1, "track_type": "bgm",
     "file": "audio/bgm/（待拍板生成）", "duration_sec": 15.0, "timecode": "0:00-0:15",
     "emotion": "平静→惊变（钢琴单音→骤停，0:06惊变点静默1s）",
     "fade": {"in": 2.0, "out": 0.5}, "mix_level": "衬底（-20dB）", "status": "pending",
     "source": "待拍板：CC0钢琴曲下载（老板选听）或程序合成降级版"},
    {"track_no": 23, "scene": 2, "track_type": "bgm",
     "file": "audio/bgm/（待拍板生成）", "duration_sec": 20.0, "timecode": "0:15-0:35",
     "emotion": "焦虑寻索（钢琴急促+弦乐铺底）",
     "fade": {"in": 1.0, "out": 1.5}, "mix_level": "衬底（-20dB）", "status": "pending",
     "source": "待拍板"},
    {"track_no": 24, "scene": 3, "track_type": "bgm",
     "file": "audio/bgm/（待拍板生成）", "duration_sec": 25.0, "timecode": "0:35-1:00",
     "emotion": "希望重现（0:42绿眼亮起时进主题）",
     "fade": {"in": 2.0, "out": 1.0}, "mix_level": "衬底（-20dB）", "status": "pending",
     "source": "待拍板"},
    {"track_no": 25, "scene": 4, "track_type": "bgm",
     "file": "audio/bgm/（待拍板生成）", "duration_sec": 20.0, "timecode": "1:00-1:20",
     "emotion": "温暖释然（主题完整呈现→随雨声淡出）",
     "fade": {"in": 1.0, "out": 5.0}, "mix_level": "衬底（-20dB）", "status": "pending",
     "source": "待拍板"},
]

manifest = {
    "project": "雨夜寻猫",
    "doc_type": "音轨清单（音效工程师交付）",
    "version": 1,
    "created_at": datetime.now().strftime("%Y-%m-%d"),
    "owner": "sound_engineer",
    "based_on": [
        "screenplay/雨夜寻猫_剧本_v1.json",
        "shots/雨夜寻猫_镜头清单_v1.json（粗剪v2时间线）",
        "handoff:SOUN-20260925-024B",
        "roles/sound_engineer/02-工作流卡片.md（四轨设计规范）",
    ],
    "total_duration_sec": 80,
    "voice": "zh-CN-XiaoyiNeural（候选A默认；候选B待老板试听拍板，替换零成本）",
    "mixing_note": "混音由剪辑师执行（ffmpeg amix分层）；音量基准：对白0dB / SFX-6~-14dB / 环境打底-16~-18dB / BGM衬底-20dB",
    "stats": {
        "ambience": 4, "dialogue": 8, "sfx": 9, "bgm_pending": 4,
        "real_samples": 2, "synthesized": 15,
    },
    "license_note": "程序合成15条（零授权风险）；真实采样2条来自sounddino.com（免注册免署名）；edge-tts对白为微软神经网络语音（免费无API限制）",
    "voice_policy_update": "2026-10-05 A6 落地：edge-tts 已合规移除（违微软自动化条款）。8 句对白 source 为 v1 历史产物，保留记录供审计；R5 开工前由 CosyVoice3（首选）→ Qwen3-TTS（备选）重生成，与 pipeline/audio_cues_v1.json voice_policy 同步。",
    "pending_items": [
        "音色拍板：候选A（XiaoyiNeural已生成8句）vs 候选B（XiaoxiaoNeural，audio/voice_test/）——老板试听拍板",
        "BGM四段选型：CC0钢琴曲下载（老板选听）vs 程序合成降级版（钢琴单音sine合成）——老板拍板",
    ],
    "tracks": tracks,
}

out_json = AUDIO / "音轨清单_v1.json"
with open(out_json, "w", encoding="utf-8") as f:
    json.dump(manifest, f, ensure_ascii=False, indent=2)
print("JSON落盘:", out_json)

# MD版
md = []
md.append("# 雨夜寻猫 音轨清单 v1\n")
md.append("> 音效工程师交付 | 2026-09-25 | 输入：剧本v1+粗剪v2时间线 → 输出：四轨素材+本清单\n")
md.append("> 混音由剪辑师执行；音量基准：对白0dB / SFX突出 / 环境打底 / BGM衬底\n")
md.append("## 总览\n")
md.append("| 轨别 | 条数 | 状态 |\n|---|---|---|")
md.append("| 环境音 | 4场 | ✅程序合成（覆盖15/20/25/20s时长轴） |")
md.append("| 对白 | 8句 | ⏳edge-tts候选A为历史产物；2026-10-05 起待 CosyVoice3/Qwen3-TTS 合规重生成 |")
md.append("| 动效 | 9条 | ✅7条程序合成+2条真实猫叫采样（sounddino免署名） |")
md.append("| BGM | 4段 | ⏳待老板拍板选型（CC0下载 vs 程序合成降级） |")
md.append("\n## 环境轨（打底）\n")
md.append("| # | 场 | 文件 | 时长 | 时码 | 说明 |\n|---|---|---|---|---|---|")
for t in tracks[:4]:
    md.append(f"| {t['track_no']} | 第{t['scene']}场 | {Path(t['file']).name} | {t['duration_sec']}s | {t['timecode']} | {t['emotion']} |")
md.append("\n## 对白轨（主导，音色候选A默认）\n")
md.append("| # | 镜 | 台词情绪 | 时长 | 进入时点 |\n|---|---|---|---|---|")
lines = {"1-1": "……小白？", "1-3": "窗没关……它肯定出去了。", "1-4": "等我，我马上回来。",
         "2-2": "小白——小白？", "2-4": "不吓你，我们回家。", "3-2": "是小白的声音。",
         "3-4": "找到你了。", "3-5": "吓死我了……走，回家。"}
for t in tracks[4:12]:
    md.append(f"| {t['track_no']} | {t['shot_no']} | {lines[t['shot_no']]}（{t['emotion']}） | {t['duration_sec']}s | {t['timecode']} |")
md.append("\n## 动效轨（突出）\n")
md.append("| # | 镜 | 文件 | 时长 | 时码 | 说明 |\n|---|---|---|---|---|---|")
for t in tracks[12:21]:
    note = t.get("timing_note", t["emotion"])
    md.append(f"| {t['track_no']} | {t['shot_no']} | {Path(t['file']).name} | {t['duration_sec']}s | {t['timecode']} | {note} |")
md.append("\n## BGM轨（衬底，待拍板）\n")
md.append("| # | 场 | 情绪设计 | 时码 | 状态 |\n|---|---|---|---|---|")
for t in tracks[21:]:
    md.append(f"| {t['track_no']} | 第{t['scene']}场 | {t['emotion']} | {t['timecode']} | ⏳{t['source']} |")
md.append("\n## 授权合规\n")
md.append("- 程序合成15条：ffmpeg白噪声/正弦合成，零授权风险")
md.append("- 猫叫×2：sounddino.com（Free download, no signup, no attribution required）")
md.append("- 对白×8：edge-tts微软神经网络语音（免费无API限制）【v1 历史产物；2026-10-05 已合规移除 edge-tts，R5 前 CosyVoice3/Qwen3-TTS 重生成】")
md.append("\n## 待老板拍板\n")
md.append("1. **音色**：候选A `audio/voice_test/候选A_zh-CN-XiaoyiNeural.mp3`（年轻活泼，已用于8句） vs 候选B `候选B_zh-CN-XiaoxiaoNeural.mp3`（标准女声）——二选一，换音色重生成零成本")
md.append("2. **BGM**：CC0钢琴曲下载（需老板选听定曲）vs 程序合成降级版（钢琴单音sine合成，免费即得但质感电子）")

out_md = AUDIO / "音轨清单_v1.md"
out_md.write_text("\n".join(md), encoding="utf-8")
print("MD落盘:", out_md)
