# -*- coding: utf-8 -*-
"""test_schema_patch.py — R0-T3 shot_spec.schema 补丁验收断言（A1~A5 + T3b A6）。

对应 R0-执行计划.md §3 T3 验收断言：
  A1: duration_s enum 长度 = 59 且全部满足 n%8==1 and 17<=n<=481 → 打印 "59 True"。
  A2: aspect_ratio pattern == ^(16:9|9:16|21:9)$（R5-C7 收紧）。
  A3: 4 个非法实例（duration_s=24 / duration_s=9 / aspect_ratio=2.39:1 / aspect_ratio=4:3）
      全部抛 ValidationError；2 个合法实例（duration_s=121 / aspect_ratio=16:9）通过。
  A4: 活动区 projects/ 内 .json 中 '"2.39:1"' / '"4:3"' / '"1:1"' 命中 0 条
      （冻结区 _legacy_projects/ 只读盘点，另行记录，不参与本断言）。
  A5: duration_s=121 实例通过校验（D-10 伪矛盾实证：121 帧 ≈ 5.04s ≥ 17 帧下限）。
  A6: fill_ratio 统一 (0,1) 开区间小数域（R0-T3b 主理人裁定）：
      exclusiveMinimum=0 / exclusiveMaximum=1 约束存在、描述含 "(0,1)"；
      合法用例 0.25 通过，非法用例 3 / 1.5 被拒。

运行：python tools/test_schema_patch.py
退出码：0 = 全部断言通过；1 = 任一断言失败。
"""

import json
import sys
from pathlib import Path

from jsonschema import Draft7Validator, ValidationError

V2_ROOT = Path(__file__).resolve().parent.parent
SCHEMA_PATH = V2_ROOT / "spec" / "shot_spec.schema.json"
PROJECTS_DIR = V2_ROOT / "projects"

RESULTS = []


def check(name, ok, detail=""):
    """记录并打印单条断言结果。"""
    status = "PASS" if ok else "FAIL"
    line = f"[{status}] {name}" + (f" — {detail}" if detail else "")
    print(line)
    RESULTS.append((name, ok))


def build_base_instance(duration_s=121, aspect_ratio="16:9"):
    """构造一个满足 schema 全部 required 字段的最小合法 shot_spec 实例。"""
    return {
        "shot_id": "0-1",
        "project": "r0_schema_patch_selftest",
        "scene_id": "SC00",
        "duration_s": duration_s,
        "fps": 24,
        "aspect_ratio": aspect_ratio,
        "purpose": "建立",
        "shot_size": "WS",
        "narrative": "R0-T3 schema 补丁自检用例实例。",
        "camera": {
            "focal_mm": 50.0,
            "t_stop": 2.8,
            "height_cm": 160.0,
            "move_type": "static",
            "one_readable_idea": True,
            "physics_note": "uniform_speed_or_true_parabola_no_fake_easing",
        },
        "lighting": {
            "key_dir_az_deg": 135.0,
            "key_temp_k": 5600.0,
            "key_intensity": 1.0,
            "fill_ratio": 0.25,
            "lighting_fragment": (
                "低角度侧逆主光自画面右侧 135 度射入，5600K 中性白，"
                "光比填充率 0.25（1:4），雨后柏油路面反光作为底部补光，全程锁死光向与色温。"
            ),
        },
        "subject": {
            "characters": [
                {"name": "测试角色", "screen_dir": "左->右", "action": "静立"}
            ]
        },
        "props": [
            {"prop_id": "P001", "visible": True, "state": "完整"}
        ],
        "weather": {},
        "beats": [{"t_s": 0.0, "what": "角色静立于巷口"}],
        "first_frame_key_elements": ["角色", "巷口", "湿路面"],
        "locks": ["服装", "道具状态", "座次"],
        "reference_assets": {"appearance_anchor": "assets/anchor/placeholder.png"},
    }


def validate(schema, instance):
    """返回 ValidationError 列表（空列表 = 通过）。"""
    validator = Draft7Validator(schema)
    return sorted(validator.iter_errors(instance), key=lambda e: e.path)


def main():
    schema = json.loads(SCHEMA_PATH.read_text(encoding="utf-8"))

    # ---- A1: duration_s enum ----
    enum = schema["properties"]["duration_s"].get("enum", [])
    n_ok = all(isinstance(n, int) and n % 8 == 1 and 17 <= n <= 481 for n in enum)
    print(f"A1: len(enum)={len(enum)} all(8k+1 in [17,481])={n_ok}")
    print(f"A1 期望输出: 59 True")
    check("A1 enum 长度=59", len(enum) == 59, f"实际 {len(enum)}")
    check("A1 全部 n%8==1 且 17<=n<=481", n_ok)
    check(
        "A1 minimum/maximum 双保险保留",
        schema["properties"]["duration_s"].get("minimum") == 17
        and schema["properties"]["duration_s"].get("maximum") == 481,
    )

    # ---- A2: aspect_ratio pattern ----
    pattern = schema["properties"]["aspect_ratio"].get("pattern", "")
    print(f"A2: aspect_ratio pattern == {pattern!r}")
    check("A2 pattern == ^(16:9|9:16|21:9)$", pattern == r"^(16:9|9:16|21:9)$")

    # ---- A3: 拒绝用例 + 合法用例 ----
    illegal_cases = [
        ("duration_s=24（非 8k+1）", build_base_instance(duration_s=24)),
        ("duration_s=9（禁用下限以下）", build_base_instance(duration_s=9)),
        ("aspect_ratio=2.39:1（已移除档位）", build_base_instance(aspect_ratio="2.39:1")),
        ("aspect_ratio=4:3（已移除档位）", build_base_instance(aspect_ratio="4:3")),
    ]
    for name, inst in illegal_cases:
        errs = validate(schema, inst)
        check(f"A3 非法用例被拒: {name}", len(errs) > 0,
              f"ValidationError x{len(errs)}" if errs else "未被拒绝！")

    legal_cases = [
        ("duration_s=121", build_base_instance(duration_s=121)),
        ("aspect_ratio=16:9", build_base_instance(aspect_ratio="16:9")),
    ]
    for name, inst in legal_cases:
        errs = validate(schema, inst)
        check(f"A3 合法用例通过: {name}", len(errs) == 0,
              "通过" if not errs else "; ".join(e.message for e in errs[:3]))

    # ---- A4: 活动区 projects 内旧档位残留扫描 ----
    old_tokens = ['"2.39:1"', '"4:3"', '"1:1"']
    hits = []
    if PROJECTS_DIR.exists():
        for f in PROJECTS_DIR.rglob("*.json"):
            text = f.read_text(encoding="utf-8", errors="replace")
            for tok in old_tokens:
                if tok in text:
                    hits.append(f"{f} :: {tok}")
    print(f"A4: 活动区 projects/ 旧档位残留命中 {len(hits)} 条")
    for h in hits:
        print(f"    {h}")
    check("A4 活动区旧档位残留 = 0", len(hits) == 0)

    # ---- A5: D-10 伪矛盾实证 ----
    errs121 = validate(schema, build_base_instance(duration_s=121))
    print("A5: duration_s=121（5 秒验证镜 ≈ 5.04s @24fps）校验"
          f"{'通过' if not errs121 else '失败'}")
    check("A5 duration_s=121 过校验（D-10 伪矛盾实证）", len(errs121) == 0,
          "通过" if not errs121 else "; ".join(e.message for e in errs121[:3]))

    # ---- A6: fill_ratio 统一 (0,1) 小数域（R0-T3b） ----
    fr = schema["properties"]["lighting"]["properties"]["fill_ratio"]
    fr_has_bounds = (fr.get("type") == "number"
                     and fr.get("exclusiveMinimum") == 0
                     and fr.get("exclusiveMaximum") == 1)
    fr_desc_ok = "(0,1)" in fr.get("description", "")
    print(f"A6: fill_ratio 约束 exclusiveMinimum={fr.get('exclusiveMinimum')} "
          f"exclusiveMaximum={fr.get('exclusiveMaximum')} 描述含(0,1)={fr_desc_ok}")
    check("A6 fill_ratio 为 (0,1) 开区间数值约束", fr_has_bounds)
    check("A6 fill_ratio 描述含 '(0,1)' 语义", fr_desc_ok)

    fr_legal = ("fill_ratio=0.25（1:4 合法）",
                build_base_instance(aspect_ratio="16:9"))  # base 已含 fill_ratio=0.25
    fr_errs = validate(schema, fr_legal[1])
    check(f"A6 合法用例通过: {fr_legal[0]}", len(fr_errs) == 0,
          "通过" if not fr_errs else "; ".join(e.message for e in fr_errs[:3]))

    for bad_val in (3.0, 1.5):
        inst = build_base_instance()
        inst["lighting"]["fill_ratio"] = bad_val
        errs = validate(schema, inst)
        check(f"A6 非法用例被拒: fill_ratio={bad_val}", len(errs) > 0,
              f"ValidationError x{len(errs)}" if errs else "未被拒绝！")

    # ---- 汇总 ----
    failed = [name for name, ok in RESULTS if not ok]
    print("-" * 60)
    print(f"总计 {len(RESULTS)} 条断言，通过 {len(RESULTS) - len(failed)}，失败 {len(failed)}")
    if failed:
        for name in failed:
            print(f"  FAIL: {name}")
        return 1
    print("全部断言通过（IS_PASS: YES）")
    return 0


if __name__ == "__main__":
    sys.exit(main())
