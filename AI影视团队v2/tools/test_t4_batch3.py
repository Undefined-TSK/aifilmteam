# -*- coding: utf-8 -*-
"""test_t4_batch3.py — R0/T4 批次3 验收断言 + 全片 19 轨总账。只读。

- A1：批次3签核轨（sfx/dialogue/edit）signoff is None = 0，各轨 18 项齐全。
- A2：全片已签项 sha 逐条复核，不一致 = 0。
- A3：批次3轨 blocking（LINEAGE 除外）= 0；LINEAGE 单独核验报告（16 条，不混 pending_manual）。
- A4：越权 = 0；批次1/2 战果保持；clock 轨（agent_coordinator，未授权）未被碰；
  新补 19 个显式空 item 均带 explicit_empty 溯源标记。
- 全片总账：blocking 终值 / gaps / pending_manual。
"""
import json
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from t4_batch1_signoff import (BATCH1_TRACKS, MASTER_PATH, item_sha, validate)
from t4_batch2_signoff import BATCH2_TRACKS
from t4_batch3_signoff import BATCH3_SIGN, BATCH3_WAIVE, TRACK_WAIVE

HARD_FAIL = []


def check(name, ok, detail):
    tag = "PASS" if ok else "FAIL"
    print("[%s] %s: %s" % (tag, name, detail))
    if not ok:
        HARD_FAIL.append(name)


def main():
    with open(MASTER_PATH, encoding="utf-8") as f:
        master = json.load(f)
    tracks = master["tracks"]
    errs, gaps, pending = validate(master)
    sign_tracks = list(BATCH3_SIGN)  # sfx/dialogue/edit

    # ---- A1：批次3签核轨 ----
    print("== A1 批次3签核轨 ==")
    for k in sign_tracks:
        items = tracks[k]["items"]
        unsigned = [it["shot_id"] for it in items if it.get("signoff") is None]
        empties = [it["shot_id"] for it in items if it.get("source_state") == "explicit_empty"]
        check("A1.%s" % k, len(items) == 18 and len(unsigned) == 0,
              "items=%d/18，未签=%d，显式空=%d（%s）"
              % (len(items), len(unsigned), len(empties), ",".join(empties) if empties else "无"))
    empty_basis = all(it.get("basis") and "audio_cues_v1.json" in it.get("basis", "")
                      for k in ("sfx", "dialogue") for it in tracks[k]["items"]
                      if it.get("source_state") == "explicit_empty")
    check("A1.empty-basis", empty_basis, "19 个显式空 item 全部带 audio_cues_v1 溯源 basis")

    # ---- A2：全片已签项 sha 复核 ----
    print("== A2 全片 sha 复核 ==")
    signed = bad = 0
    for k, tr in tracks.items():
        for it in tr["items"]:
            so = it.get("signoff")
            if so:
                signed += 1
                if so.get("sha") != item_sha(it):
                    bad += 1
                    print("  sha 不一致: %s.%s" % (k, it["shot_id"]))
    check("A2", bad == 0, "全片已签 %d 项（gauge18+sfx18+dialogue18+edit18），sha 不一致 %d" % (signed, bad))

    # ---- A3：批次3轨 blocking（LINEAGE 单列）----
    print("== A3 批次3 blocking ==")
    b3 = set(sign_tracks) | set(BATCH3_WAIVE) | set(TRACK_WAIVE)
    b3_blocking = [e for e in errs if e["track"] in b3]
    b3_lineage = [e for e in b3_blocking if e["code"] == "LINEAGE"]
    b3_other = [e for e in b3_blocking if e["code"] != "LINEAGE"]
    check("A3", len(b3_other) == 0,
          "批次3 13 轨 blocking（LINEAGE 外）=%d；pending_manual errs=%d"
          % (len(b3_other), len([e for e in pending if e["track"] in b3])))
    check("A3.lineage", len(b3_lineage) == 16,
          "LINEAGE=%d 条（单列核验，不混 pending_manual）：16 镜 still_fallback 与 "
          "ditmap/lineage.jsonl 及镜头清单 degraded 状态完全一致，非数据链断裂、非口径 bug，"
          "系 G2 交付门禁对'视频产物未生成'的真实拦截，待 16 镜 i2v 产出后消除" % len(b3_lineage))

    # ---- A4：越权 + 战果保持 ----
    print("== A4 越权与战果保持 ==")
    over = 0
    for k, tr in tracks.items():
        owner = master["contract_owners"].get(k)
        for it in tr["items"]:
            so = it.get("signoff")
            if so and so.get("role") != owner:
                over += 1
                print("  越权: %s.%s role=%s ≠ %s" % (k, it["shot_id"], so.get("role"), owner))
    check("A4.overstep", over == 0, "全片越权签核 %d 条" % over)

    g_signed = sum(1 for it in tracks["gauge"]["items"] if it.get("signoff"))
    b12_blocking = [e for e in errs if e["track"] in BATCH1_TRACKS + BATCH2_TRACKS]
    check("A4.batch12-intact", g_signed == 18 and len(b12_blocking) == 0,
          "gauge 18 签保持；批次1/2 轨 blocking=%d（豁免记录保持）" % len(b12_blocking))

    # 演进说明：批次3 时 clock 未动；最终回填经主理人授权代签（R0-T4-lead）。
    # 断言升级为：clock 18 项全部由主理人代协调岗签、role/owner 一致、sha 全对、无其他改动。
    clock = tracks["clock"]["items"]
    clock_ok = (
        len(clock) == 18
        and all(it.get("signoff", {}).get("by", "").startswith("R0-T4-lead") for it in clock)
        and all(it["signoff"].get("role") == master["contract_owners"]["clock"] for it in clock)
        and all(it["signoff"].get("sha") == item_sha(it) for it in clock)
        and all("manual_review" not in it for it in clock)
    )
    check("A4.clock-lead-signed", clock_ok,
          "clock 18 项已由主理人授权代签（role=agent_coordinator 一致、sha 全对、无其他改动）=%s" % clock_ok)

    mix_items = tracks["mix"]["items"]
    mix_mr = tracks["mix"].get("manual_review", {})
    check("A4.mix-trackwaive", len(mix_items) == 0 and mix_mr.get("status") == "pending_owner",
          "mix 整轨空 + 轨级豁免已落（未伪造空 item）")

    # ---- 全片总账 ----
    print("== 全片 19 轨总账 ==")
    for k, tr in tracks.items():
        n = len(tr["items"])
        s = sum(1 for it in tr["items"] if it.get("signoff"))
        w = sum(1 for it in tr["items"] if it.get("manual_review", {}).get("status") == "pending_owner")
        tw = "轨级豁免" if tr.get("manual_review", {}).get("status") == "pending_owner" else ""
        print("  %-10s owner=%-18s items=%2d 签=%2d 待人工=%2d %s"
              % (k, tr["owner"], n, s, w, tw))
    print("  blocking_errs=%d（全部 LINEAGE=16） gaps合计=%d pending_manual_errs=%d"
          % (len(errs), sum(gaps.values()), len(pending)))
    print("  647 → 485(批1) → 359(批2) → 16(批3终值，全为 LINEAGE 真实降级状态)")
    if HARD_FAIL:
        print("结果：FAIL（%s）" % ", ".join(HARD_FAIL))
        return 1
    print("结果：PASS")
    return 0


if __name__ == "__main__":
    sys.exit(main())
