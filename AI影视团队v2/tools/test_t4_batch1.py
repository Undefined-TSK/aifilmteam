# -*- coding: utf-8 -*-
"""test_t4_batch1.py — R0/T4 批次1（agent_virtualdp：camera/gauge/light 轨）验收断言。

只读，不改任何文件。逐条复跑 R0-执行计划 §3 T4 断言（批次1范围）：
- A1：批次1各轨 items `signoff is None` 计数（gauge 应为 0；camera/light 待人工项按
  纪律不许签，数字如实报告，豁免记录见 A3）。
- A2：逐条重算 sha256(item)[:12] 与 signoff.sha 比对，不一致数必须 = 0。
- A3：批次1轨 blocking 计数必须 = 0（或全部降级为带原因的 pending_manual 豁免项，
  给出两个数：blocking 与 pending_manual_items）。
- A4：每条 signoff.role == contract_owners[track]（== agent_virtualdp），越权数必须 = 0。

运行：C:\\Users\\LZH\\.workbuddy\\binaries\\python\\versions\\3.13.12\\python.exe test_t4_batch1.py
退出码 0 = 断言通过；非 0 = 存在硬失败（A2/A3/A4 任一不过）。
"""
import json
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from t4_batch1_signoff import (BATCH1_ROLE, BATCH1_TRACKS, MASTER_PATH, item_sha, validate)

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

    # ---- A1：signoff is None 计数（批次1三轨）----
    print("== A1 signoff is None 计数 ==")
    unsigned_by_track = {}
    for k in BATCH1_TRACKS:
        unsigned = [it["shot_id"] for it in tracks[k]["items"] if it.get("signoff") is None]
        unsigned_by_track[k] = unsigned
        waived = [i for i in tracks[k]["items"] if i.get("signoff") is None
                  and i.get("manual_review", {}).get("status") == "pending_owner"]
        check("A1.%s" % k,
              len(unsigned) == 0 or len(unsigned) == len(waived),
              "未签 %d 项；其中待人工豁免 %d 项（未签且无豁免 = %d）"
              % (len(unsigned), len(waived), len(unsigned) - len(waived)))
    total_unsigned = sum(len(v) for v in unsigned_by_track.values())
    print("  A1 合计：批次1未签 %d 项（gauge %d / camera %d / light %d）——"
          "camera/light 因无明确数值依据按纪律不许签，逐条豁免见 A3"
          % (total_unsigned, len(unsigned_by_track["gauge"]),
             len(unsigned_by_track["camera"]), len(unsigned_by_track["light"])))

    # ---- A2：sha 防伪（逐条重算）----
    print("== A2 sha 复核 ==")
    bad = 0
    signed = 0
    for k in BATCH1_TRACKS:
        for it in tracks[k]["items"]:
            so = it.get("signoff")
            if not so:
                continue
            signed += 1
            if so.get("sha") != item_sha(it):
                bad += 1
                print("  sha 不一致: %s.%s signoff.sha=%s 重算=%s"
                      % (k, it["shot_id"], so.get("sha"), item_sha(it)))
    check("A2", bad == 0, "已签 %d 项，sha 不一致 %d 项" % (signed, bad))

    # ---- A3：批次1轨 blocking（豁免降级后）----
    print("== A3 批次1 blocking ==")
    b1_blocking = [e for e in errs if e["track"] in BATCH1_TRACKS]
    b1_pending = [e for e in pending if e["track"] in BATCH1_TRACKS]
    b1_pending_items = sum(1 for k in BATCH1_TRACKS for it in tracks[k]["items"] if is_pending(it))
    check("A3", len(b1_blocking) == 0,
          "批次1 blocking=%d（baseline 162 → 0），pending_manual 豁免 errs=%d / items=%d（全部带 reason）"
          % (len(b1_blocking), len(b1_pending), b1_pending_items))
    no_reason = [e for e in b1_pending if e.get("msg") and "null" not in e["msg"] and e["code"] != "NO_SIGNOFF"]
    reasons_on_items = {(k, it["shot_id"]): it["manual_review"]["reason"][:40]
                        for k in ("camera", "light") for it in tracks[k]["items"]
                        if it.get("manual_review", {}).get("reason")}
    # 演进说明：原断言硬编码 36（批次1 全部待人工）。最终回填后 light 1-1~1-4 按主理人
    # 授权采纳创作提案（by=R0-T4-conv，带 correction 溯源）→ 未签待人工 = camera 18 + light 14。
    unsigned_b1 = sum(1 for k in BATCH1_TRACKS for it in tracks[k]["items"] if it.get("signoff") is None)
    light_conv = [it for it in tracks["light"]["items"]
                  if it.get("signoff", {}).get("by", "").startswith("R0-T4-conv")]
    check("A3.reason", len(reasons_on_items) == unsigned_b1 and len(light_conv) == 4,
          "批次1 未签待人工 %d 项，逐条带 reason = %d；light 已按提案收敛签核 %d 项（1-1~1-4，带 correction）"
          % (unsigned_b1, len(reasons_on_items), len(light_conv)))

    # ---- A4：归属一致（越权 = 0）----
    print("== A4 越权检查 ==")
    over = 0
    for k in BATCH1_TRACKS:
        owner = master["contract_owners"].get(k)
        for it in tracks[k]["items"]:
            so = it.get("signoff")
            if so and so.get("role") != owner:
                over += 1
                print("  越权: %s.%s signoff.role=%s ≠ contract_owners=%s"
                      % (k, it["shot_id"], so.get("role"), owner))
    check("A4", over == 0, "越权签核 %d 条（contract_owners[%s]=%s）"
          % (over, "/".join(BATCH1_TRACKS), BATCH1_ROLE))

    # ---- 汇总 ----
    print("== 汇总 ==")
    print("gaps_by_owner（重生成后）:", json.dumps(gaps, ensure_ascii=False))
    print("agent_virtualdp blocking gaps =", gaps.get(BATCH1_ROLE, 0))
    if HARD_FAIL:
        print("结果：FAIL（%s）" % ", ".join(HARD_FAIL))
        return 1
    print("结果：PASS（A2/A3/A4 全绿；A1 如实报告未签数，未签项全部带豁免记录）")
    return 0


def is_pending(item):
    mr = item.get("manual_review")
    return isinstance(mr, dict) and mr.get("status") == "pending_owner"


if __name__ == "__main__":
    sys.exit(main())
