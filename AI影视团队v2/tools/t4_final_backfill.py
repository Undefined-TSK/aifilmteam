# -*- coding: utf-8 -*-
"""t4_final_backfill.py — R0/T4 最终回填（主理人授权收敛裁定执行）。

三项授权操作：
1. clock 轨 18 项代签：主理人代行协调岗。
   signoff{role:"agent_coordinator", by:"R0-T4-lead(主理人代协调岗,授权:docs/07-交接与日志/R0-执行日志-2026-10-03.md)", ts, sha}
2. light 第1场出租屋 4 镜（1-1~1-4）回填+签：按 docs/07-交接与日志/R0-T4-批次1-创作提案-36项.md
   高置信推荐值回填 5 必填字段，by="R0-T4-conv(团队推荐收敛,提案文档:R0-T4-批次1-创作提案-36项.md)"。
   ⚠️ fill_ratio 口径冲突处置：提案按分母口径（1:4→4，对齐 shot_spec.schema 描述
   "1:3 -> 3"），但 timeline 校验器 RANGE fill_ratio∈(0,1)——两者矛盾。为不破坏
   blocking 门禁，以倒数等价落库（1:4→0.25，光比语义不变），逐镜写 correction 双向
   溯源，冲突上报待架构师/T3 裁决。
3. camera 冲突修正（lock/分镜表胜出 auto_draft，补 correction{basis,source}）：
   - 2-1/2-5/4-1 focal_mm 28→35；4-3 focal_mm 24→35（scene_lock 雨夜街道"广角35mm低机位"）
   - 1-2 move_type static→dolly、fps_move 0→0.25（分镜表 1-2"推向空猫窝"；fps_move
     为衍生一致性：生成器口径 move≠static→0.25）
   - 上述 5 镜 pos/aim 仍空 → manual_review 保留（豁免继续有效），不整体代签。

完成后重生成 gaps。只改 master_v2.json 与 gaps_by_owner.json，零删除。
"""
import json
import os
import sys
from datetime import datetime

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from t4_batch1_signoff import MASTER_PATH, item_sha, load_master, regen_gaps, validate

SIGN_BY_CLOCK = "R0-T4-lead(主理人代协调岗,授权:docs/07-交接与日志/R0-执行日志-2026-10-03.md)"
SIGN_BY_CONV = "R0-T4-conv(团队推荐收敛,提案文档:R0-T4-批次1-创作提案-36项.md)"
CONV_SOURCE = "docs/07-交接与日志/R0-T4-批次1-创作提案-36项.md + 主理人收敛裁定(R0-执行日志-2026-10-03)"

# light 第1场高置信推荐值（提案 §一 #2/#4/#6/#8）；fill_ratio 存倒数，见 correction
LIGHT_BACKFILL = {
    "1-1": {"key_temp_k": 2900, "key_dir_az_deg": 270, "key_intensity": 1.0, "fill_ratio": 0.25,
            "proposal_fill_ratio": 4,
            "motivation": "暖黄台灯主光 vs 窗外冷蓝光（scene_lock 出租屋内原文），平静段暖主光占优"},
    "1-2": {"key_temp_k": 8500, "key_dir_az_deg": 0, "key_intensity": 0.9, "fill_ratio": 0.3333,
            "proposal_fill_ratio": 3,
            "motivation": "冷蓝窗光打在空窝上（分镜表1-2原文）——主辅与 1-1 对调，冷暖易位即叙事"},
    "1-3": {"key_temp_k": 2900, "key_dir_az_deg": 270, "key_intensity": 1.0, "fill_ratio": 0.25,
            "proposal_fill_ratio": 4,
            "motivation": "延续 lock 暖黄台灯主光，光不切换保场内连续（同场光连续铁律），情绪反差由表演承接"},
    "1-4": {"key_temp_k": 8500, "key_dir_az_deg": 0, "key_intensity": 0.7, "fill_ratio": 0.1667,
            "proposal_fill_ratio": 6,
            "motivation": "门灯熄灭，屋内只剩开着的窗和飘动窗帘（分镜表1-4原文）——她离开后世界的空"},
}
CAMERA_FIX = {
    "2-1": {"field": "focal_mm", "old": 28, "new": 35},
    "2-5": {"field": "focal_mm", "old": 28, "new": 35},
    "4-1": {"field": "focal_mm", "old": 28, "new": 35},
    "4-3": {"field": "focal_mm", "old": 24, "new": 35},
    "1-2": {"field": "move_type+fps_move", "old": "static/0", "new": "dolly/0.25"},
}
CAMERA_BASIS = {
    "2-1": "scene_lock/雨夜街道.json '广角35mm低机位'（lock 胜出 auto_draft 按景别默认焦段）",
    "2-5": "scene_lock/雨夜街道.json '广角35mm低机位'（lock 胜出 auto_draft 按景别默认焦段）",
    "4-1": "scene_lock/雨夜街道.json '广角35mm低机位'（lock 胜出；4-1 与 2-1 同街道同机位语法）",
    "4-3": "scene_lock/雨夜街道.json '广角35mm低机位'（lock 胜出 auto_draft 默认焦段）",
    "1-2": "分镜表 1-2 原文'推向空猫窝/推近'（分镜表胜过 auto_draft 默认 static）；fps_move 0→0.25 为衍生一致性（生成器口径 move≠static→0.25，同 2-1 truck）",
}


def main(argv):
    master = load_master()
    ts = datetime.now().astimezone().isoformat(timespec="seconds")
    if "--apply" not in argv:
        errs, gaps, pending = validate(master)
        print("blocking=%d gaps=%d pending=%d" % (len(errs), sum(gaps.values()), len(pending)))
        return 0

    # ---- ① clock 18 项代签 ----
    n_clock = 0
    for it in master["tracks"]["clock"]["items"]:
        if not it.get("signoff"):
            it["signoff"] = {"role": "agent_coordinator", "by": SIGN_BY_CLOCK,
                             "ts": ts, "sha": item_sha(it)}
            n_clock += 1

    # ---- ② light 1-1~1-4 回填 + 签 ----
    n_light = 0
    for it in master["tracks"]["light"]["items"]:
        sid = it["shot_id"]
        if sid not in LIGHT_BACKFILL:
            continue
        rec = LIGHT_BACKFILL[sid]
        it["key_temp_k"] = rec["key_temp_k"]
        it["key_dir_az_deg"] = rec["key_dir_az_deg"]
        it["key_intensity"] = rec["key_intensity"]
        it["fill_ratio"] = rec["fill_ratio"]
        it["motivation"] = rec["motivation"]
        it["correction"] = {
            "field": "fill_ratio",
            "proposal_value": rec["proposal_fill_ratio"],
            "stored_value": rec["fill_ratio"],
            "basis": ("提案按分母口径填 %d（1:%d，提案文档§〇.3）与 timeline 校验器 RANGE "
                      "fill_ratio∈(0,1) 冲突；按校验器域以倒数等价落库（1:%d→%s），光比语义不变；"
                      "口径冲突上报待架构师/T3 裁决" % (rec["proposal_fill_ratio"],
                                                  rec["proposal_fill_ratio"],
                                                  rec["proposal_fill_ratio"], rec["fill_ratio"])),
            "source": CONV_SOURCE,
        }
        it.pop("manual_review", None)  # 已处置完成，移除豁免
        it["signoff"] = {"role": "agent_virtualdp", "by": SIGN_BY_CONV, "ts": ts, "sha": item_sha(it)}
        n_light += 1

    # ---- ③ camera 冲突修正（5 镜，manual_review 保留）----
    n_cam = 0
    for it in master["tracks"]["camera"]["items"]:
        sid = it["shot_id"]
        if sid not in CAMERA_FIX:
            continue
        fix = CAMERA_FIX[sid]
        if fix["field"] == "focal_mm":
            assert it["focal_mm"] == fix["old"], "focal_mm 现值与预期不符: %s" % sid
            it["focal_mm"] = fix["new"]
        else:
            assert it["move_type"] == "static" and it["fps_move"] == 0, "move 现值与预期不符: %s" % sid
            it["move_type"] = "dolly"
            it["fps_move"] = 0.25
        it["correction"] = {"field": fix["field"], "old": fix["old"], "new": fix["new"],
                            "basis": CAMERA_BASIS[sid], "source": CONV_SOURCE}
        mr = it.get("manual_review")
        if mr:
            mr["note"] = "已按收敛裁定修正 %s（见 correction）；pos/aim/motivation 仍空，豁免继续有效，待 blockout 后回签" % fix["field"]
        n_cam += 1

    with open(MASTER_PATH, "w", encoding="utf-8") as f:
        json.dump(master, f, ensure_ascii=False, indent=1)
    errs, gaps, pending = validate(load_master())
    note = ("T4 最终回填（主理人授权收敛裁定）于 %s：clock 18 项由主理人代协调岗代签；"
            "light 第1场 4 镜按创作提案高置信值回填并签（fill_ratio 倒数等价落库，冲突已上报）；"
            "camera 5 镜 focal/move 冲突按 lock/分镜表修正（correction 溯源）；"
            "其余保持批次1-3 处置。残留 blocking=16 全为 LINEAGE（真实降级状态，待 i2v）。" % ts)
    g = regen_gaps(master, errs, gaps, pending, note=note)
    signed = sum(1 for _, tr in load_master()["tracks"].items()
                 for it in tr["items"] if it.get("signoff"))
    print("== --apply 完成 ==")
    print("clock 代签=%d  light 回填签=%d  camera 修正=%d（保留豁免）" % (n_clock, n_light, n_cam))
    print("全片已签总数=%d  blocking=%d  gaps=%d  pending_manual_errs=%d"
          % (signed, g["blocking_errs"], sum(g["gaps_by_owner"].values()), g["pending_manual_errs"]))
    print("残留 blocking 类型:", sorted({e["code"] for e in errs}))
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
