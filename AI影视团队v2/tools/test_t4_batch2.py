# -*- coding: utf-8 -*-
"""test_t4_batch2.py — R0/T4 批次2（agent_set_props：weather/wardrobe/props 轨）验收断言。

只读，不改任何文件。断言：
- A1：批次2各轨 items `signoff is None` 计数如实报告（本批次三轨必填字段全 null 且无
  明确依据，按纪律不许签 → 未签项必须 100% 带待人工豁免记录）。
- A2：批次2已签项 sha 复核 = 0 失败（本批次 0 签，则恒真但如实报告）。
- A3：批次2轨 blocking = 0（全部降级为带 reason 的 pending_manual 豁免）。
- A4：越权 = 0；批次1战果不回退：gauge 18 项签核保持且 sha 全对、批次1三轨 blocking 仍 0、
  批次1/2 之外 14 轨字节级未动（signoff 全 None 且无 manual_review）。

运行：C:\\Users\\LZH\\.workbuddy\\binaries\\python\\versions\\3.13.12\\python.exe test_t4_batch2.py
退出码 0 = 通过。
"""
import json
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from t4_batch1_signoff import (BATCH1_TRACKS, MASTER_PATH, item_sha, load_master, validate)
from t4_batch2_signoff import BATCH2_TRACKS
from t4_batch3_signoff import BATCH3_SIGN, BATCH3_WAIVE  # noqa: F401 批次3授权处置校验用

HARD_FAIL = []


def check(name, ok, detail):
    tag = "PASS" if ok else "FAIL"
    print("[%s] %s: %s" % (tag, name, detail))
    if not ok:
        HARD_FAIL.append(name)


def is_pending(item):
    mr = item.get("manual_review")
    return isinstance(mr, dict) and mr.get("status") == "pending_owner" and mr.get("reason")


def main():
    with open(MASTER_PATH, encoding="utf-8") as f:
        master = json.load(f)
    tracks = master["tracks"]
    errs, gaps, pending = validate(master)

    # ---- A1：signoff is None 计数（批次2三轨）----
    print("== A1 signoff is None 计数 ==")
    for k in BATCH2_TRACKS:
        unsigned = [it["shot_id"] for it in tracks[k]["items"] if it.get("signoff") is None]
        waived = [sid for sid in unsigned
                  if is_pending(next(i for i in tracks[k]["items"] if i["shot_id"] == sid))]
        check("A1.%s" % k, len(unsigned) == len(waived),
              "未签 %d 项；待人工豁免 %d 项（未签且无豁免 = %d）"
              % (len(unsigned), len(waived), len(unsigned) - len(waived)))
    print("  A1 合计：批次2未签 %d 项（weather %d / wardrobe %d / props %d）——三轨必填字段全 null"
          "且无明确数值依据（locks/props 为空、无 costume 登记），按纪律 0 签，全部带豁免"
          % tuple([sum(1 for k in BATCH2_TRACKS for it in tracks[k]["items"] if it.get("signoff") is None)]
                  + [sum(1 for it in tracks[k]["items"] if it.get("signoff") is None) for k in BATCH2_TRACKS]))

    # ---- A2：sha 复核（批次2已签项）----
    print("== A2 sha 复核（批次2）==")
    signed = bad = 0
    for k in BATCH2_TRACKS:
        for it in tracks[k]["items"]:
            so = it.get("signoff")
            if so:
                signed += 1
                if so.get("sha") != item_sha(it):
                    bad += 1
                    print("  sha 不一致: %s.%s" % (k, it["shot_id"]))
    check("A2", bad == 0, "批次2已签 %d 项（本批次按纪律 0 签），sha 不一致 %d 项" % (signed, bad))

    # ---- A3：批次2轨 blocking（豁免降级后）----
    print("== A3 批次2 blocking ==")
    b2_blocking = [e for e in errs if e["track"] in BATCH2_TRACKS]
    b2_pending = [e for e in pending if e["track"] in BATCH2_TRACKS]
    b2_pending_items = sum(1 for k in BATCH2_TRACKS for it in tracks[k]["items"] if is_pending(it))
    check("A3", len(b2_blocking) == 0,
          "批次2 blocking=%d（baseline 126 → 0），pending_manual 豁免 errs=%d / items=%d"
          % (len(b2_blocking), len(b2_pending), b2_pending_items))
    reasons = sum(1 for k in BATCH2_TRACKS for it in tracks[k]["items"] if it.get("manual_review", {}).get("reason"))
    check("A3.reason", reasons == 54, "批次2 54 项豁免，逐条带 reason = %d" % reasons)

    # ---- A4：越权 + 批次1战果不回退 ----
    print("== A4 越权 + 批次1战果回退检查 ==")
    over = 0
    for k in BATCH1_TRACKS + BATCH2_TRACKS:
        owner = master["contract_owners"].get(k)
        for it in tracks[k]["items"]:
            so = it.get("signoff")
            if so and so.get("role") != owner:
                over += 1
                print("  越权: %s.%s role=%s ≠ %s" % (k, it["shot_id"], so.get("role"), owner))
    check("A4.overstep", over == 0, "批次1+2 越权签核 %d 条" % over)

    gauge = tracks["gauge"]["items"]
    g_signed = sum(1 for it in gauge if it.get("signoff"))
    g_bad = sum(1 for it in gauge
                if it.get("signoff") and it["signoff"].get("sha") != item_sha(it))
    check("A4.gauge-intact", g_signed == 18 and g_bad == 0,
          "gauge 签核 %d/18 保持，sha 不一致 %d" % (g_signed, g_bad))
    b1_blocking = [e for e in errs if e["track"] in BATCH1_TRACKS]
    check("A4.batch1-blocking", len(b1_blocking) == 0,
          "批次1三轨 blocking 仍 = %d（camera/light 36 项豁免保持）" % len(b1_blocking))

    # 批次3 已获授权处置其余 14 轨：此处断言语义升级为——这些轨的全部变化必须
    # 来自批次3授权处置（签核 by=R0-T4-batch3 或豁免 recorded_by=R0-T4-batch3），
    # 不得出现来历不明的改动；clock（agent_coordinator）不属任何批次，必须未动。
    b12 = set(BATCH1_TRACKS) | set(BATCH2_TRACKS)
    polluted = []
    for k, tr in tracks.items():
        if k in b12 or k == "clock":
            continue
        for it in tr["items"]:
            so, mr = it.get("signoff"), it.get("manual_review")
            ok_so = so is None or (so.get("by") == "R0-T4-batch3")
            ok_mr = (mr is None) or (mr.get("recorded_by") == "R0-T4-batch3")
            if not (ok_so and ok_mr):
                polluted.append(k + "." + str(it.get("shot_id")))
        trm = tr.get("manual_review")
        if trm is not None and trm.get("recorded_by") != "R0-T4-batch3":
            polluted.append(k + "(track)")
    clock_dirty = [it.get("shot_id") for it in tracks["clock"]["items"]
                   if not (it.get("signoff", {}).get("by", "").startswith("R0-T4-lead")
                           and it["signoff"].get("role") == "agent_coordinator")
                   and (it.get("signoff") is not None or "manual_review" in it)]
    check("A4.others-intact", len(polluted) == 0 and not clock_dirty,
          "批次1/2 之外 14 轨：非批次3授权改动=%d；clock 轨仅允许主理人授权代签（R0-T4-lead）异常=%d"
          % (len(polluted), len(clock_dirty)))

    # ---- 汇总 ----
    print("== 汇总 ==")
    print("gaps_by_owner（重生成后）:", json.dumps(gaps, ensure_ascii=False))
    print("agent_set_props blocking gaps =", gaps.get("agent_set_props", 0),
          "；全片 blocking_errs =", len(errs), "；pending_manual_errs =", len(pending))
    if HARD_FAIL:
        print("结果：FAIL（%s）" % ", ".join(HARD_FAIL))
        return 1
    print("结果：PASS（A2/A3/A4 全绿；A1 如实报告，未签项全部带豁免）")
    return 0


if __name__ == "__main__":
    sys.exit(main())
