# -*- coding: utf-8 -*-
"""timeline_build.py — 轨道契约 + 校验器 + 主时间轴生成（P-0b）
「每镜每条轨道有 owner、有值或标 missing，缺即阻塞」——不写在文档里，写成代码。
数据源（全是工作区已有真件）：pipeline/clock_shots.json、pipeline/audio_cues_v1.json、
projects/<片>/ditmap/lineage.jsonl、storyboard/雨夜寻猫_镜头清单_v1.md
输出：projects/<片>/timeline/master_v2.json + gaps_by_owner.json（谁还缺几项）

2026-10-05 修复（债务5）：重跑不再覆盖已签核——新生成前读旧 master_v2.json，
按 (track, shot_id) 保留已有 signoff{role,by,ts,sha}；根路径改 v2 相对定位（不再指旧接合点）。
"""
import json
import os
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]          # AI影视团队v2
PROJ = "雨夜寻猫"
PB = ROOT / "projects" / PROJ
FPS, RATE = 24, 48000
TOTAL_F = 1920

# 19 条轨道 → owner。owner 是"职责"，不等于bot；脚本化的岗位不占 Agent。
OWNER = {
    "camera": "agent_virtualdp", "gauge": "agent_virtualdp", "light": "agent_virtualdp",
    "weather": "agent_set_props", "performance": "agent_director", "wardrobe": "agent_set_props",
    "props": "agent_set_props", "spatial": "agent_script_super", "ambience": "agent_sound",
    "sfx": "agent_sound", "dialogue": "agent_sound", "music": "agent_sound", "mix": "agent_sound",
    "vfx": "agent_vfx", "grade": "agent_color", "overlay": "agent_editor", "subtitle": "agent_editor",
    "edit": "agent_editor", "clock": "agent_coordinator",
}
# 允许"值可为 null 但仍算填"的字段（例如 static 镜头的运镜速率）
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


def load(p):
    p = Path(p)
    return json.load(open(p, encoding="utf-8")) if p.exists() else None


def find_first(sub_dirs, pattern):
    for sub in sub_dirs:
        d = PB / sub
        if not d.is_dir():
            continue
        for fn in sorted(d.iterdir()):
            if fn.name.endswith(".json") and pattern in fn.name:
                return json.load(open(fn, encoding="utf-8"))
    return None


def num(x):
    x = str(x).replace("s", "").strip()
    try:
        return float(x)
    except Exception:
        return None


def main():
    # 主时钟直接由镜头清单派生（单一真相源，不另存一份手工 clock 文件）
    SUB_DIRS = ("00_brief/shots", "shots", "00_brief/storyboard", "storyboard", "00_brief")
    shotjson = find_first(SUB_DIRS, "镜头清单")
    cum = 0
    clock = {"shots": []}
    for r in (shotjson or {}).get("shots", []):
        d = num(r.get("spec_duration_sec") or 3) or 3
        n = int(round(d * FPS))
        clock["shots"].append({"id": r["shot_no"], "in_f": cum, "out_f": cum + n - 1,
                               "order_idx": len(clock["shots"]) + 1, "motion_declared": r.get("camera_move"),
                               "len": n})
        cum += n
    clock["total_frames"] = cum
    cues = load(ROOT / "pipeline" / "audio_cues_v1.json") or {}
    lin = {}
    lp = PB / "ditmap" / "lineage.jsonl"
    if not lp.exists():
        print("ditmap/lineage.jsonl 不存在，中止")
        return 2
    for ln in open(lp, encoding="utf-8"):
        r = json.loads(ln)
        lin[str(r.get("shot_id"))] = r
    shots = clock["shots"]
    if not shots:
        print("镜头清单没解析出任何镜，中止")
        return 2
    if clock["total_frames"] != TOTAL_F:
        warns_clock = f"清单累计 {clock['total_frames']} 帧 ≠ 交付时长预算 {TOTAL_F} 帧（差 {TOTAL_F-clock['total_frames']}）"
        print("!! " + warns_clock)
    else:
        warns_clock = ""
    md = ""
    for sub in SUB_DIRS:
        p = PB / sub / "雨夜寻猫_镜头清单_v1.md"
        if p.exists():
            md = open(p, encoding="utf-8").read()
            break
    sizes = {}
    for ln in md.splitlines():
        cells = [c.strip().strip("*") for c in ln.strip().strip("|").split("|")] if ln.startswith("|") else []
        if len(cells) >= 4 and re.fullmatch(r"\d+-\d+", cells[0]):
            sizes[cells[0]] = cells
    T = (cues or {}).get("tracks") or (cues or {}).get("stems") or {}
    dlg = {e["line"]: e for e in T.get("dialogue", {}).get("events", [])}
    sfx = T.get("sfx", {}).get("events", [])
    amb = T.get("ambience", {}).get("events", [])
    mus = T.get("music", {}).get("events", [])
    out = {"schema": "cineast.timeline/2.0", "project": PROJ, "contract_owners": OWNER,
           "meta": {"total_frames": clock["total_frames"], "clock_note": warns_clock},
           "clock": {"fps": FPS, "total_frames": TOTAL_F, "sample_rate": RATE},
           "tracks": {k: {"owner": OWNER[k], "items": []} for k in OWNER}}
    prev = None
    # 签核保留：读旧 master_v2.json，按 (track, shot_id) 索引已有 signoff（重跑不丢签）
    old = load(PB / "timeline" / "master_v2.json") or {}
    old_signoff = {}
    for tr_name, tr in (old.get("tracks") or {}).items():
        for it in tr.get("items", []):
            so = it.get("signoff") or {}
            if so.get("sha"):
                old_signoff[(tr_name, it.get("shot_id"))] = so
    for s in shots:
        sid, i_f, o_f = s["id"], s["in_f"], s["out_f"]
        L = lin.get(sid, {})
        src = sizes.get(sid, [])
        size_txt = src[2] if len(src) > 2 else ""
        kind = L.get("kind", "missing")
        t = out["tracks"]
        t["edit"]["items"].append({"shot_id": sid, "in_f": i_f, "out_f": o_f, "order_idx": s["order_idx"],
                                   "transition_out": "cut", "source_kind": kind,
                                   "gen": {"engine": "kling3-omni+first_frame" if kind in ("video", "blockout_2d") else "TBD"}})
        t["clock"]["items"].append({"shot_id": sid, "fps": FPS})
        # 表值先按景别给一个真实可执行默认（不是许愿，是拍片常识；导演可改，但必须有值）
        lens = {"ECU": 85, "CU": 75, "MS": 50, "FS": 35, "WS": 28, "LS": 24, "MLS": 40}.get(size_txt, 40)
        move = {"static": "static", "dolly_in": "dolly", "pan": "pan", "tracking": "truck",
                "dolly_out": "dolly"}.get(s.get("motion_declared", "static"), "static")
        t["camera"]["items"].append({"shot_id": sid, "origin": "auto_draft", "needs_owner_confirm": True,
                                    "signoff": old_signoff.get(("camera", sid)),
                                    "pos": None, "aim": None, "move_type": move,
                                    "fps_move": 0.25 if move != "static" else 0, "pan_dps": 3.0 if move == "pan" else 0,
                                    "hand_shake_pct": 0.0, "focal_mm": lens, "t_stop": 2.8,
                                    "focus_curve": None, "motivation": None})
        t["gauge"]["items"].append({"shot_id": sid, "sensor": "super35", "shutter_angle_deg": 180, "frame_rate": 24})
        t["light"]["items"].append({"shot_id": sid, "key_temp_k": None, "key_dir_az_deg": None,
                                   "key_intensity": None, "fill_ratio": None, "motivation": None})
        t["weather"]["items"].append({"shot_id": sid, "rain_rate_mm_h": None, "ground_wetness": None})
        t["performance"]["items"].append({"shot_id": sid, "path": None, "body_emotion": None,
                                          "gaze": None, "gesture_clips": None})
        t["wardrobe"]["items"].append({"shot_id": sid, "costume_id": None, "wetness": None})
        t["props"]["items"].append({"shot_id": sid, "prop_id": None, "visible": None, "state_machine": None})
        t["spatial"]["items"].append({"shot_id": sid, "axis_line_deg": None, "screen_dir": None,
                                      "eyeline_deg": None, "light_dir_deg": None})
        t["vfx"]["items"].append({"shot_id": sid, "events": None})
        t["grade"]["items"].append({"shot_id": sid, "origin": "auto_draft", "needs_owner_confirm": True,
                                   "show_lut_id": "cold_blue_gray_v1",
                                   "signoff": old_signoff.get(("grade", sid)),
                                   "primary_lift_gamma_gain": None, "grain_template_id": "film_grain_light"})
        t["overlay"]["items"].append({"shot_id": sid, "elements": None, "ai_label": None})
        t["subtitle"]["items"].append({"shot_id": sid, "events": None, "style": None})
        if sid in dlg:
            e = dlg[sid]
            t["dialogue"]["items"].append({"shot_id": sid, "events": [dict(e)], "anchor_lkfs": -27.0})
        ss = [x for x in sfx if (s["in_f"] / FPS - 0.6) <= x["start_s"] <= (s["out_f"] / FPS + 0.6)]
        if ss:
            t["sfx"]["items"].append({"shot_id": sid, "events": ss,
                                      "trigger_ref": [{"start_s": x["start_s"], "kind": x.get("trigger_ref", {})} for x in ss]})
        aa = [x for x in amb if x["start_s"] < (s["out_f"] + 1) / FPS and x["end_s"] > s["in_f"] / FPS]
        if aa:
            t["ambience"]["items"].append({"shot_id": sid, "layers": aa, "room_tone_id": None})
        mm = [x for x in mus if x["start_s"] < (s["out_f"] + 1) / FPS and x["end_s"] > s["in_f"] / FPS]
        if mm:
            t["music"]["items"].append({"shot_id": sid, "events": mm, "ducks_for_dialogue": None})

    # ---- 校验：必填 / 枚举 / 数值域 / 帧单调不重叠 / 跨轴翻转 ----
    errs, gaps = [], {}
    auto = []
    for k, tr in out["tracks"].items():
        for it in tr["items"]:
            if it.get("origin") == "auto_draft":
                so = it.get("signoff") or {}
                if not so.get("sha"):
                    auto.append(f"{k}.{it['shot_id']}")
                    gaps[OWNER[k]] = gaps.get(OWNER[k], 0) + 1
                    errs.append(f"[NO_SIGNOFF] {k}.{it['shot_id']} origin=auto_draft 且无 signoff → 不算定稿，禁进花钱步骤")
        have = {it["shot_id"] for it in tr["items"]}
        for s in shots:
            if s["id"] not in have:
                gaps[OWNER[k]] = gaps.get(OWNER[k], 0) + 1
                errs.append(f"[TRACK_MISSING] {s['id']} {k}（owner={OWNER[k]}，整条轨道没这格的值）")
        for it in tr["items"]:
            for fld in MUST[k]:
                v = it.get(fld, "ABSENT")
                if v == "ABSENT":
                    errs.append(f"[FIELD_ABSENT] {it['shot_id']} {k}.{fld} 未写入契约字段")
                elif v is None:
                    gaps[OWNER[k]] = gaps.get(OWNER[k], 0) + 1
                    errs.append(f"[FIELD_NULL] {it['shot_id']} {k}.{fld} = null（owner={OWNER[k]} 待填）")
            e = ENUM.get((k, fld)) if fld in [f for (kk, f) in ENUM] else None
            if (k, fld) in ENUM and isinstance(it.get(fld), str) and it[fld] not in ENUM[(k, fld)]:
                errs.append(f"[ENUM] {it['shot_id']} {k}.{fld}={it.get(fld)}")
            if (k, fld) in RANGE:
                lo, hi = RANGE[(k, fld)]
                vv = it.get(fld)
                if isinstance(vv, (int, float)) and not (lo <= vv <= hi):
                    errs.append(f"[RANGE] {it['shot_id']} {k}.{fld}={vv} 越界[{lo},{hi}]")
    ed = sorted(out["tracks"]["edit"]["items"], key=lambda x: x["in_f"])
    for cur, nxt in zip(ed, ed[1:]):
        if nxt["in_f"] != cur["out_f"] + 1 and nxt["in_f"] != cur["out_f"]:
            errs.append(f"[GAP] {cur['shot_id']}→{nxt['shot_id']} 帧不连续 {cur['out_f']}→{nxt['in_f']}")
    for it in out["tracks"]["spatial"]["items"]:
        if it["screen_dir"] and prev and it["screen_dir"] != prev not in ("neutral", None):
            errs.append(f"[AXIS] {it['shot_id']} 屏幕方向翻转 {prev}→{it['screen_dir']}")
        prev = it["screen_dir"] or prev
    still = [it["shot_id"] for it in out["tracks"]["edit"]["items"] if it["source_kind"] not in ("video",)]
    for it in out["tracks"]["edit"]["items"]:
        if it["source_kind"] != "video":
            errs.append(f"[LINEAGE] {it['shot_id']} kind={it['source_kind']} → 溯源非视频源，禁进交付（gate G2）")
    TL = os.path.join(PB, "timeline")
    os.makedirs(TL, exist_ok=True)
    out["meta"]["auto_draft_needs_confirm"] = auto
    out["meta"]["signoff_rule"] = ("origin=auto_draft 的项必须有 signoff{role,by,ts,sha} 才算定稿；"
                                   "qc_media 按 sha 复核，无签或 sha 不符 → 视为未填，禁止进 g1 之后的花钱步骤")
    json.dump(out, open(os.path.join(TL, "master_v2.json"), "w", encoding="utf-8"),
              ensure_ascii=False, indent=1)
    json.dump({"gaps_by_owner": gaps, "blocking_errs": len(errs)},
              open(os.path.join(TL, "gaps_by_owner.json"), "w", encoding="utf-8"),
              ensure_ascii=False, indent=1)
    os.makedirs(os.path.join(PB, "timeline"), exist_ok=True)
    print(f"主时钟：{len(shots)} 镜 / {clock['total_frames']} 帧 / {clock['total_frames']/FPS:.2f}s {('| ' + warns_clock) if warns_clock else ''}")
    print(f"主时间轴 → {os.path.join(TL,'master_v2.json')}（{len(shots)} 镜 × {len(OWNER)} 轨）")
    print(f"脚本代填的自动草稿 {len(auto)} 项（不算已填，须由该轨道 owner 确认后才能过 g1 门）")
    print(f"阻塞错误 {len(errs)} 条；待填字段按负责人：")
    for k, v in sorted(gaps.items(), key=lambda x: -x[1]):
        print(f"  {k:<18} {v:>3} 项待填")
    print("\n前 12 条错误样本：")
    for x in errs[:12]:
        print("  " + x[:150])
    return 0


if __name__ == "__main__":
    sys.exit(main())

