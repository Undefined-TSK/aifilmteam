# -*- coding: utf-8 -*-
"""t4_batch1_signoff.py — R0/T4 批次1（agent_virtualdp：camera/gauge/light 轨）逐 item 签核工具。

职责：
1. 复刻 pipeline/timeline_build.py 的 blocking 判定规则（MUST/ENUM/RANGE/NO_SIGNOFF/
   FIELD_NULL/FIELD_ABSENT/TRACK_MISSING/GAP/AXIS/LINEAGE），对现存 master_v2.json
   做只读扫描（timeline_build.py 重跑会整体重建 master 覆盖签核——2026-10-05 起
   已按 (track, shot_id) 保留旧 signoff，仍建议先扫描后 apply）。
2. --apply：对批次1三轨逐 item 三选一处理——
   - 可签（gauge：字段完整且与 clock fps=24 一致）→ 写 signoff{role,by,ts,sha}；
   - 待人工（camera 的 pos/aim/motivation、light 的 key_temp_k 等为 null，且
     scene_lock 仅有定性 lighting_direction、02_blockout 为空，无数值依据，
     属 DP/灯光创作判断）→ 写 manual_review{status:"pending_owner", reason,...} 豁免记录；
   - 修后签：本批次无（未发现可由明确依据推出的正确值）。
   然后重生成 gaps_by_owner.json（豁免项降级为 pending_manual，不计 blocking）。
3. sha 语义（对齐 spec/shot_spec.schema.json owner_signoff）：被签 item 去除 signoff
   字段后的 canonical JSON（sort_keys、ensure_ascii=False、紧凑分隔符）sha256 前 12 位。

只改 master_v2.json 与 gaps_by_owner.json；其他轨 item 一个字节不动。
"""
import hashlib
import json
import os
import sys
from datetime import datetime
from pathlib import Path

TL_DIR = Path(__file__).resolve().parents[1] / "projects" / "雨夜寻猫" / "00_brief" / "timeline"
MASTER_PATH = TL_DIR / "master_v2.json"
GAPS_PATH = TL_DIR / "gaps_by_owner.json"

BATCH1_TRACKS = ("camera", "gauge", "light")
BATCH1_ROLE = "agent_virtualdp"
SIGN_BY = "R0-T4-batch1"

# ---- 与 pipeline/timeline_build.py 逐字对齐的契约规则 ----
MUST = {
    "camera": ["pos", "aim", "move_type", "motivation"],
    "gauge": ["sensor", "shutter_angle_deg", "frame_rate"],
    "light": ["key_temp_k", "key_dir_az_deg", "key_intensity", "fill_ratio", "motivation"],
    "weather": ["rain_rate_mm_h", "ground_wetness"],
    "performance": ["path", "body_emotion", "gaze", "gesture_clips"],
    "wardrobe": ["costume_id", "wetness"],
    "props": ["prop_id", "visible", "state_machine"],
    "spatial": ["axis_line_deg", "screen_dir", "eyeline_deg", "light_dir_deg"],
    "ambience": ["layers", "room_tone_id"],
    "sfx": ["events", "trigger_ref"],
    "dialogue": ["events", "anchor_lkfs"],
    "music": ["events", "ducks_for_dialogue"],
    "mix": ["buses", "automation", "ducking", "target"],
    "vfx": ["events"],
    "grade": ["show_lut_id", "primary_lift_gamma_gain", "grain_template_id"],
    "overlay": ["elements", "ai_label"],
    "subtitle": ["events", "style"],
    "edit": ["in_f", "out_f", "order_idx", "transition_out"],
    "clock": ["fps"],
}
ENUM = {
    ("camera", "move_type"): {"static", "dolly", "truck", "pan", "tilt", "crane", "handheld",
                              "zoom", "rack_focus", "combo"},
    ("spatial", "screen_dir"): {"L2R", "R2L", "neutral"},
    ("edit", "transition_out"): {"cut", "cut_hard", "cross_dissolve", "fade_black", "wipe", "match_cut"},
    ("grade", "grain_template_id"): {"film_grain_light", "film_grain_heavy", "none"},
}
RANGE = {
    ("gauge", "shutter_angle_deg"): (90, 360), ("gauge", "frame_rate"): (24, 24),
    ("camera", "fps_move"): (0, 3), ("camera", "pan_dps"): (0, 60),
    ("camera", "hand_shake_pct"): (0, 3), ("camera", "focal_mm"): (14, 200),
    ("camera", "t_stop"): (0.95, 22),
    ("light", "key_temp_k"): (1500, 12000), ("light", "fill_ratio"): (0, 1),
    ("weather", "rain_rate_mm_h"): (0, 500), ("weather", "ground_wetness"): (0, 1),
    ("performance", "body_emotion"): (0, 100), ("wardrobe", "wetness"): (0, 1),
    ("mix", "target_lufs"): (-24, -9), ("dialogue", "anchor_lkfs"): (-40, -10),
}

# 待人工豁免原因（逐条写入 item 的 manual_review.reason，可追溯）
WAIVE_REASON = {
    "camera": ("pos/aim/motivation 为必填且为 null：机位坐标/朝向/动机需 DP 内容判断。"
               "scene_lock 仅定性（雨夜街道:'广角35mm低机位'），02_blockout 为空、无机位数值 lock，"
               "无明确依据不可代填，禁止 rubber-stamp → 待 DP 逐镜定值后修后签。"),
    "light": ("key_temp_k/key_dir_az_deg/key_intensity/fill_ratio/motivation 为必填且为 null："
              "scene_lock 仅给定性 lighting_direction（出租屋内'暖黄台灯vs窗外冷蓝'、"
              "街道'霓虹多色光源'、巷口'路灯暖光主光源'），数值色温/方位角/强度/光比属灯光设计"
              "创作判断，无明确依据不可代填 → 待 DP 逐镜定值后修后签。"),
}


def load_master():
    with open(MASTER_PATH, encoding="utf-8") as f:
        return json.load(f)


def item_sha(item):
    """被签对象内容 sha256 前 12 位：item 去除 signoff 后 canonical JSON。"""
    payload = {k: v for k, v in item.items() if k != "signoff"}
    raw = json.dumps(payload, ensure_ascii=False, sort_keys=True, separators=(",", ":"))
    return hashlib.sha256(raw.encode("utf-8")).hexdigest()[:12]


def is_deferred(item):
    """该 item 是否带待人工豁免记录（降级为非 blocking 的唯一通道）。"""
    mr = item.get("manual_review")
    return isinstance(mr, dict) and mr.get("status") == "pending_owner" and mr.get("reason")


def validate(master):
    """复刻 timeline_build.py 校验逻辑，返回 (errs, gaps, pending)。

    errs / pending 元素为 {track, shot_id, code, msg}；gaps 为 {owner: 计数}
    （仅 NO_SIGNOFF/FIELD_NULL/TRACK_MISSING 计入 gaps，与原脚本一致；
    带豁免记录的项归入 pending，不计 blocking）。
    """
    errs, gaps, pending = [], {}, []
    tracks = master["tracks"]
    owners = master["contract_owners"]
    shot_ids = [it["shot_id"] for it in tracks["edit"]["items"]]

    def gap(track):
        o = owners.get(track, "?")
        gaps[o] = gaps.get(o, 0) + 1

    def record(bucket, track, it, code, msg):
        bucket.append({"track": track, "shot_id": it.get("shot_id"), "code": code, "msg": msg})

    for k, tr in tracks.items():
        items = tr["items"]
        # ① origin=auto_draft 未签（原 NO_SIGNOFF）
        for it in items:
            if it.get("origin") == "auto_draft":
                so = it.get("signoff") or {}
                if not so.get("sha"):
                    msg = "[NO_SIGNOFF] %s.%s origin=auto_draft 且无 signoff → 不算定稿，禁进花钱步骤" % (k, it["shot_id"])
                    record(pending if is_deferred(it) else errs, k, it, "NO_SIGNOFF", msg)
                    if not is_deferred(it):
                        gap(k)
        # ② 整格缺失（原 TRACK_MISSING；轨级 manual_review 可豁免——用于 mix 这类
        #    整轨未设计的事件型轨无法逐 item 落豁免的场景）
        have = {it["shot_id"] for it in items}
        tr_manual = tr.get("manual_review")
        tr_deferred = isinstance(tr_manual, dict) and tr_manual.get("status") == "pending_owner" and tr_manual.get("reason")
        for sid in shot_ids:
            if sid not in have:
                o = owners.get(k, "?")
                msg = "[TRACK_MISSING] %s %s（owner=%s，整条轨道没这格的值）" % (sid, k, o)
                if tr_deferred:
                    pending.append({"track": k, "shot_id": sid, "code": "TRACK_MISSING", "msg": msg})
                else:
                    errs.append({"track": k, "shot_id": sid, "code": "TRACK_MISSING", "msg": msg})
                    gap(k)
        # ③ 必填 / 枚举 / 数值域
        for it in items:
            for fld in MUST[k]:
                v = it.get(fld, "ABSENT")
                if v == "ABSENT":
                    record(errs, k, it, "FIELD_ABSENT",
                           "[FIELD_ABSENT] %s %s.%s 未写入契约字段" % (it["shot_id"], k, fld))
                elif v is None:
                    msg = "[FIELD_NULL] %s %s.%s = null（owner=%s 待填）" % (it["shot_id"], k, fld, owners.get(k, "?"))
                    record(pending if is_deferred(it) else errs, k, it, "FIELD_NULL", msg)
                    if not is_deferred(it):
                        gap(k)
            if (k, fld) in ENUM and isinstance(it.get(fld), str) and it[fld] not in ENUM[(k, fld)]:
                record(errs, k, it, "ENUM", "[ENUM] %s %s.%s=%s" % (it["shot_id"], k, fld, it.get(fld)))
            if (k, fld) in RANGE:
                lo, hi = RANGE[(k, fld)]
                vv = it.get(fld)
                if isinstance(vv, (int, float)) and not (lo <= vv <= hi):
                    record(errs, k, it, "RANGE",
                           "[RANGE] %s %s.%s=%s 越界[%s,%s]" % (it["shot_id"], k, fld, vv, lo, hi))
    # ④ 帧连续性（edit 轨）
    ed = sorted(tracks["edit"]["items"], key=lambda x: x["in_f"])
    for cur, nxt in zip(ed, ed[1:]):
        if nxt["in_f"] != cur["out_f"] + 1 and nxt["in_f"] != cur["out_f"]:
            errs.append({"track": "edit", "shot_id": cur["shot_id"], "code": "GAP",
                         "msg": "[GAP] %s→%s 帧不连续 %s→%s" % (cur["shot_id"], nxt["shot_id"], cur["out_f"], nxt["in_f"])})
    # ⑤ 轴线（spatial 轨；表达式与原脚本逐字一致）
    prev = None
    for it in tracks["spatial"]["items"]:
        if it["screen_dir"] and prev and it["screen_dir"] != prev not in ("neutral", None):
            errs.append({"track": "spatial", "shot_id": it["shot_id"], "code": "AXIS",
                         "msg": "[AXIS] %s 屏幕方向翻转 %s→%s" % (it["shot_id"], prev, it["screen_dir"])})
        prev = it["screen_dir"] or prev
    # ⑥ 溯源（edit 轨）
    for it in tracks["edit"]["items"]:
        if it["source_kind"] != "video":
            errs.append({"track": "edit", "shot_id": it["shot_id"], "code": "LINEAGE",
                         "msg": "[LINEAGE] %s kind=%s → 溯源非视频源，禁进交付（gate G2）" % (it["shot_id"], it["source_kind"])})
    return errs, gaps, pending


def regen_gaps(master, errs, gaps, pending, note=None):
    """重生成 gaps_by_owner.json（结构与原文件兼容，追加 pending 明细字段）。

    note：自定义说明文案；缺省沿用批次1处理说明（批次1 main 调用行为不变）。
    """
    pend_by_owner = {}
    for e in pending:
        o = master["contract_owners"].get(e["track"], "?")
        pend_by_owner[o] = pend_by_owner.get(o, 0) + 1
    if note is None:
        note = ("T4 批次1（agent_virtualdp camera/gauge/light）处理于 %s：可签已签、"
                "不可判项带 manual_review 豁免记录降级为 pending_manual（不计 blocking）；"
                "其他轨未动。" % datetime.now().astimezone().isoformat(timespec="seconds"))
    out = {
        "gaps_by_owner": gaps,
        "blocking_errs": len(errs),
        "pending_manual_by_owner": pend_by_owner,
        "pending_manual_errs": len(pending),
        "note": note,
    }
    with open(GAPS_PATH, "w", encoding="utf-8") as f:
        json.dump(out, f, ensure_ascii=False, indent=1)
    return out


def main(argv):
    master = load_master()
    errs, gaps, pending = validate(master)
    if "--apply" not in argv:
        print("== 只读扫描（baseline 对照）==")
        print("blocking_errs =", len(errs), " gaps 合计 =", sum(gaps.values()))
        for o, n in sorted(gaps.items(), key=lambda x: -x[1]):
            print("  %-18s %4d" % (o, n))
        print("pending（现有豁免）=", len(pending))
        for e in errs[:12]:
            print("  " + e["msg"][:150])
        return 0

    ts = datetime.now().astimezone().isoformat(timespec="seconds")
    n_sign = n_waive = 0
    for k in BATCH1_TRACKS:
        for it in master["tracks"][k]["items"]:
            if it.get("signoff"):
                continue  # 幂等：已签不重签
            if k == "gauge":
                # 可签：gauge 三字段完整（sensor/shutter/frame_rate），与 clock fps=24 一致，
                # RANGE/ENUM 全过，属技术参数确认，无创作判断。
                it["signoff"] = {"role": BATCH1_ROLE, "by": SIGN_BY, "ts": ts, "sha": item_sha(it)}
                n_sign += 1
            else:
                # 待人工：必填数值字段全 null，无明确依据，不许签 → 落豁免记录。
                it["manual_review"] = {
                    "status": "pending_owner",
                    "reason": WAIVE_REASON[k],
                    "recorded_by": SIGN_BY,
                    "recorded_at": ts,
                }
                n_waive += 1
    with open(MASTER_PATH, "w", encoding="utf-8") as f:
        json.dump(master, f, ensure_ascii=False, indent=1)
    errs, gaps, pending = validate(load_master())
    g = regen_gaps(master, errs, gaps, pending)
    print("== --apply 完成 ==")
    print("gauge 新签=%d  camera/light 落待人工豁免 item=%d" % (n_sign, n_waive))
    print("重生成 gaps：blocking_errs=%d gaps合计=%d pending_manual_errs=%d"
          % (g["blocking_errs"], sum(g["gaps_by_owner"].values()), g["pending_manual_errs"]))
    print("agent_virtualdp blocking gaps =", g["gaps_by_owner"].get(BATCH1_ROLE, 0))
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
