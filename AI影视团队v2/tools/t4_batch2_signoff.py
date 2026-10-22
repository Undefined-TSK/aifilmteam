# -*- coding: utf-8 -*-
"""t4_batch2_signoff.py — R0/T4 批次2（agent_set_props：weather/wardrobe/props 轨）逐 item 签核工具。

复用批次1模块的校验器/sha/load/regen（t4_batch1_signoff），本模块只做批次2的差异部分：
- 批次2三轨全部必填字段为 null，且均无明确数值依据：
  weather：剧本/场景锁仅定性"中雨""地面水渍反光"（mm/h 与逐镜湿程度属岗位判断）；
  wardrobe：character_lock/林小雨.json 仅定性"米色风衣"，无 costume 资产 ID 登记，
            wetness 逐镜数值无依据；
  props：剧本有逐场定性道具列表，但 locks/props/ 为空目录，无 prop_id 登记与状态机设计。
- 故本批次 0 可签 / 0 修后签 / 54 待人工，逐条落 manual_review 豁免记录后重生成 gaps。
- 只改 master_v2.json（批次2三轨）与 gaps_by_owner.json；批次1战果与其他轨不动。
"""
import json
import sys
from datetime import datetime

sys.path.insert(0, __file__.rsplit("\\", 1)[0])
from t4_batch1_signoff import (MASTER_PATH, item_sha, load_master, regen_gaps, validate)

BATCH2_TRACKS = ("weather", "wardrobe", "props")
BATCH2_ROLE = "agent_set_props"
SIGN_BY = "R0-T4-batch2"

WAIVE_REASON = {
    "weather": ("rain_rate_mm_h/ground_wetness 为必填且为 null：剧本/scene_lock 仅定性"
                "（'中雨打在伞面上''地面水渍反光'），且第1场为室内景、第4场'雨还在下'暗示雨势"
                "随场次变化，mm/h 数值与逐镜湿程度属 set_props 岗位判断，无明确依据不可代填"
                " → 待逐镜定值后修后签。"),
    "wardrobe": ("costume_id/wetness 为必填且为 null：character_lock/林小雨.json 仅定性"
                 "'米色风衣'（K13 已锁林小雨 v2 基准），但项目无 costume 资产登记"
                 "（costume_id 无既定 ID 体系），wetness 逐镜淋雨程度（0~1）无依据，"
                 "属 set_props 岗位判断 → 建议先立 costume 资产 ID 登记再逐镜回填。"),
    "props": ("prop_id/visible/state_machine 为必填且为 null：剧本逐场有定性道具列表"
              "（台灯/空猫窝/飘动窗帘/开着的窗/伏案的书本/伞/垃圾桶/车底/纸箱/水洼等），"
              "但 locks/props/ 为空目录、无道具 ID 登记与状态机设计，prop_id 编制与逐镜"
              " state_machine 属 set_props 岗位创作判断 → 待登记后逐镜回填。"),
}

REGEN_NOTE = ("T4 批次2（agent_set_props weather/wardrobe/props）处理于 %s：三轨必填字段全 null"
              "且无明确依据（scene_lock/character_lock/剧本均定性、无 costume/prop ID 登记），"
              "按纪律 0 签 / 54 待人工，逐条带 manual_review 豁免记录降级为 pending_manual"
              "（不计 blocking）；批次1与其他轨未动。")


def main(argv):
    master = load_master()
    errs, gaps, pending = validate(master)
    if "--apply" not in argv:
        print("== 批次2 只读扫描（baseline 对照）==")
        print("blocking_errs =", len(errs), " gaps 合计 =", sum(gaps.values()))
        for o, n in sorted(gaps.items(), key=lambda x: -x[1]):
            print("  %-18s %4d" % (o, n))
        for k in BATCH2_TRACKS:
            b = [e for e in errs if e["track"] == k]
            print("  轨 %-9s blocking = %d" % (k, len(b)))
        return 0

    ts = datetime.now().astimezone().isoformat(timespec="seconds")
    n_waive = 0
    for k in BATCH2_TRACKS:
        for it in master["tracks"][k]["items"]:
            if it.get("signoff") or it.get("manual_review"):
                continue  # 幂等：已处理不重处理
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
    g = regen_gaps(master, errs, gaps, pending,
                   note=REGEN_NOTE % ts)
    print("== --apply 完成 ==")
    print("weather/wardrobe/props 落待人工豁免 item=%d（0 签 / 0 修后签）" % n_waive)
    print("重生成 gaps：blocking_errs=%d gaps合计=%d pending_manual_errs=%d"
          % (g["blocking_errs"], sum(g["gaps_by_owner"].values()), g["pending_manual_errs"]))
    print("agent_set_props blocking gaps =", g["gaps_by_owner"].get(BATCH2_ROLE, 0))
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
