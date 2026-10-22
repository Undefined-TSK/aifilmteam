# -*- coding: utf-8 -*-
"""t4_batch3_signoff.py — R0/T4 批次3（剩余六 owner 13 轨）逐 item 签核工具。

复用 t4_batch1_signoff 的校验器/sha/load/regen。批次3处置方案（全部经现场核验依据）：

可签（35）：
- sfx 9：events+trigger_ref 完整，src 音频文件已核存在（05_audio/sfx/ 10 个 mp3）。
- dialogue 8：events 完整（text/src 对齐 05_audio/dialogue/ 8 个 mp3），anchor_lkfs=-27
  在 RANGE[-40,-10]。注：1-1 事件含 voice_license="🟡需替换"，为事实状态记录，非契约字段。
- edit 18：in_f/out_f/order_idx/transition_out 完整合法（cut 在 ENUM），帧区间连续
  0→1919 与 clock total_frames=1920 一致。gen.engine="TBD"×16 非 MUST 字段。

修后签（19，补显式空 item）：
- sfx 9 镜、dialogue 10 镜无 item：audio_cues_v1.json 确认无该镜事件（事件型轨，
  "无事件"是合法状态而非缺数据）→ 补显式空 item（events=[]，带 source_state/basis
  溯源字段）后签。dialogue 空 item anchor_lkfs=-27.0 与既有 8 项统一。

待人工（144，item 级豁免）：
- ambience 18（room_tone_id null 且无 room tone 资产登记）、music 18（ducks_for_dialogue
  null 混音决策）、performance 18、spatial 18、grade 18（lift_gamma_gain null 调色数值 +
  lut/grain 无资产登记）、overlay 18、subtitle 18（whisper 产物仅 1-1 一镜）、vfx 18。

轨级豁免（mix）：items=0 整轨未设计，混音配置非"空可合法"的事件型轨，补空即伪造 →
tracks.mix.manual_review 轨级豁免（validate 已支持 TRACK_MISSING 轨级豁免）。

不处置（如实上报）：clock 18 项（owner=agent_coordinator 不在批次3授权范围，不代签不越权）；
LINEAGE 16 条 errs 经核验为真实数据状态（见回报），保留在 blocking_errs，不进 pending_manual。
"""
import json
import os
import sys
from datetime import datetime

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from t4_batch1_signoff import MASTER_PATH, item_sha, load_master, regen_gaps, validate

BATCH3_SIGN = {"sfx": "agent_sound", "dialogue": "agent_sound", "edit": "agent_editor"}
BATCH3_WAIVE = {"ambience": "agent_sound", "music": "agent_sound", "performance": "agent_director",
                "spatial": "agent_script_super", "grade": "agent_color", "overlay": "agent_editor",
                "subtitle": "agent_editor", "vfx": "agent_vfx"}
TRACK_WAIVE = {"mix": "agent_sound"}
SIGN_BY = "R0-T4-batch3"

WAIVE_REASON = {
    "ambience": ("layers 已填（audio_cues_v1 真实事件，05_audio/ambient/ 4 个 mp3 已核存在），"
                 "但 room_tone_id=null 且项目无 room tone 资产登记；layers 自记 layers_missing"
                 "（远景低鸣/雷/滴水混响等待补层）→ 待音频岗立 room tone 资产登记后回填。"),
    "music": ("events 已填（4 场 cue，05_audio/bgm/ 4 个 mp3 已核存在），ducks_for_dialogue=null"
              " 为音乐-对白闪避混音决策，属 agent_sound/music 岗创作判断 → 待定值后签。"),
    "performance": ("path/body_emotion/gaze/gesture_clips 全 null：剧本 action 为定性描述"
                    "（'蹲下查看''撑伞快步'等），逐镜走位坐标/情绪数值(0-100)/视线/手势剪辑"
                    "属导演创作判断，无明确依据不可代填 → 待导演逐镜设计后修后签。"),
    "spatial": ("axis_line_deg/screen_dir/eyeline_deg/light_dir_deg 全 null：轴线/视线/光位"
                "角度数值需依分镜与机位定（scene_lock 仅'广角35mm低机位'定性，无机位 lock 数值）"
                " → 待场记岗逐镜定值。"),
    "grade": ("primary_lift_gamma_gain=null（调色数值创作判断）；show_lut_id='cold_blue_gray_v1'/"
              "grain_template_id='film_grain_light' 为管线默认值且无 LUT/颗粒模板资产登记可核"
              " → 待调色岗确认 LUT 登记并逐镜定值后签。"),
    "overlay": ("elements/ai_label 全 null：ai_label 为 AI 生成内容标识（交付合规硬要求），"
                "其呈现方案与 elements 字幕条/角标设计属剪辑岗创作 → 待回填。"),
    "subtitle": ("events/style 全 null：whisper 字幕产物仅 1-1 一镜（05_audio/dialogue/"
                 "subtitles/ 仅 1-1.json/.srt，对照 8 镜台词缺口大），style 无登记 → "
                 "待字幕岗批量产出并对齐时间轴后回填。"),
    "vfx": ("events 全 null：绿眼亮起、雨幕增强等 VFX 设计属创作判断，项目无 vfx 清单 lock"
            " → 待 vfx 岗逐镜设计后修后签。"),
}
TRACK_WAIVE_REASON = {
    "mix": ("整轨 items=0（buses/automation/ducking/target 无任何值）：混音母带设计未开始。"
            "mix 为全镜必需的技术配置轨（非'无事件即合法'的事件型轨），补空 item 即伪造 → "
            "轨级待人工：待音频岗整轨产出（target_lufs 参考 spec/delivery_spec.json mix 区间）。"),
}

REGEN_NOTE = ("T4 批次3（agent_sound/director/script_super/color/editor/vfx 共 13 轨）处理于 %s："
              "可签 35（sfx9/dialogue8/edit18）+ 修后签 19（sfx/dialogue 补显式空 item，依据 "
              "audio_cues_v1.json 确认无事件）= 54 签；待人工 144 项 item 级豁免 + mix 轨级豁免；"
              "LINEAGE 16 条经核验为真实降级状态（16 still_fallback/2 video，与 ditmap 一致），"
              "保留 blocking 待 i2v 产出消除；clock 轨属 agent_coordinator 未在授权范围未动。"
              "批次1/2 战果未动。")


def empty_item(track, sid):
    """补显式空 item（事件型轨合法空），带溯源字段。"""
    if track == "sfx":
        return {"shot_id": sid, "events": [], "trigger_ref": [],
                "source_state": "explicit_empty",
                "basis": "audio_cues_v1.json sfx 无该镜事件（权威源核对）"}
    return {"shot_id": sid, "events": [], "anchor_lkfs": -27.0,
            "source_state": "explicit_empty",
            "basis": "audio_cues_v1.json dialogue 无该镜台词（权威源核对）；anchor 与既有 8 项统一 -27.0"}


def main(argv):
    master = load_master()
    errs, gaps, pending = validate(master)
    if "--apply" not in argv:
        print("== 批次3 只读扫描（baseline 对照）==")
        print("blocking_errs =", len(errs), " gaps 合计 =", sum(gaps.values()))
        for o, n in sorted(gaps.items(), key=lambda x: -x[1]):
            print("  %-18s %4d" % (o, n))
        lin_codes = {}
        for e in errs:
            lin_codes[e["code"]] = lin_codes.get(e["code"], 0) + 1
        print("errs 按类型:", lin_codes)
        return 0

    ts = datetime.now().astimezone().isoformat(timespec="seconds")
    shot_ids = [it["shot_id"] for it in master["tracks"]["edit"]["items"]]
    n_sign = n_added = n_waive = 0

    # ① sfx/dialogue：补显式空 item（按 edit 镜序插入），然后全轨签核
    for k, role in BATCH3_SIGN.items():
        tr = master["tracks"][k]
        have = {it["shot_id"]: it for it in tr["items"]}
        rebuilt = []
        for sid in shot_ids:
            if sid in have:
                rebuilt.append(have[sid])
            elif k in ("sfx", "dialogue"):
                rebuilt.append(empty_item(k, sid))
                n_added += 1
        tr["items"] = rebuilt
        for it in tr["items"]:
            if not it.get("signoff"):
                it["signoff"] = {"role": role, "by": SIGN_BY, "ts": ts, "sha": item_sha(it)}
                n_sign += 1

    # ② edit：直接签（MUST 完整合法、帧连续）
    tr = master["tracks"]["edit"]
    for it in tr["items"]:
        if not it.get("signoff"):
            it["signoff"] = {"role": BATCH3_SIGN["edit"], "by": SIGN_BY, "ts": ts, "sha": item_sha(it)}
            n_sign += 1

    # ③ 待人工：8 轨 item 级豁免
    for k in BATCH3_WAIVE:
        for it in master["tracks"][k]["items"]:
            if it.get("signoff") or it.get("manual_review"):
                continue
            it["manual_review"] = {"status": "pending_owner", "reason": WAIVE_REASON[k],
                                   "recorded_by": SIGN_BY, "recorded_at": ts}
            n_waive += 1

    # ④ mix：轨级豁免（整轨未设计，不伪造空 item）
    master["tracks"]["mix"]["manual_review"] = {
        "status": "pending_owner", "reason": TRACK_WAIVE_REASON["mix"],
        "recorded_by": SIGN_BY, "recorded_at": ts}

    with open(MASTER_PATH, "w", encoding="utf-8") as f:
        json.dump(master, f, ensure_ascii=False, indent=1)
    errs, gaps, pending = validate(load_master())
    g = regen_gaps(master, errs, gaps, pending, note=REGEN_NOTE % ts)
    lin = [e for e in errs if e["code"] == "LINEAGE"]
    print("== --apply 完成 ==")
    print("签核=%d（含修后签，新补显式空 item=%d） item级待人工=%d 轨级豁免=mix"
          % (n_sign, n_added, n_waive))
    print("重生成 gaps：blocking_errs=%d gaps合计=%d pending_manual_errs=%d"
          % (g["blocking_errs"], sum(g["gaps_by_owner"].values()), g["pending_manual_errs"]))
    print("残留 blocking 类型:", {e["code"] for e in errs}, " LINEAGE=%d 条" % len(lin))
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
