# VERSION · 文档版本矩阵

> 依据 07 方案 §E.3 建立。契约/规格类用 SemVer；文档类用 vX.Y。变更必须在此留痕。
> 只登记"活文档"；归档代际文档不登记（冻结状态见 STATUS_MATRIX）。

| 文档 | 当前版本 | 上次更新 | 说明 |
|---|---|---|---|
| `02-决策/DECISIONS.md` | v1.0 | 2026-10-03 | 15 轮 + 1.5 轮全批准；唯一决策事实源 |
| `02-决策/NEGOTIATION_PROGRESS.md` | v1.0 | 2026-10-03 | 15/15 收官看板 |
| `02-决策/06-full-project-audit.md` | v1.0 | 2026-10-03 | 全项目普查总报告 |
| `02-决策/07-document-reorganization-plan.md` | v1.1 | 2026-10-03 | 含 R-1~R-5 裁定修正；已执行落地 |
| `02-决策/08-project-restructure-plan.md` | v1.1 | 2026-10-03 | 含裁定修正；已执行落地 |
| `02-决策/09-decision-review-report.md` | v1.0 | 2026-10-03 | 六维度复审，零推翻 |
| `02-决策/10-team-collaboration-log.md` | v1.0 | 2026-10-03 | 协作与裁定全程记录 |
| `02-决策/11-development-readiness-report.md` | v1.2 | 2026-10-03 | 阻塞项排除后终审见 §5 |
| `03-规划与调研/R0-执行计划.md` | v1.1 | 2026-10-03 | QA 终检后补 T0 并订正（七项 26 断言） |
| v2 `spec/delivery_spec.json` | 见文件内 version 字段 | — | 档位契约（L1/L2/L3） |
| v2 `pipeline/tech_delivery_spec.json` | v1.7（沿袭，仅改名） | 2026-10-03 | R0-T0 同名消歧：原 `pipeline/delivery_spec.json` 改名，消除与 `spec/delivery_spec.json` 同名异 schema 碰撞（07 方案 §C.6 / E-N1）；内容零改动 |
| v2 `spec/qc_rubric.json` | 见文件内 version 字段 | — | 五项硬指标 |
| v2 `spec/shot_spec.schema.json` | 见文件内 version 字段 | 2026-10-03 | R0-T3 duration_s 59 值 enum + aspect_ratio 收紧 + R0-T3b fill_ratio (0,1) 域已落地 |

**破坏性契约变更（MAJOR）须经文档 owner + 相关 Agent 复核并在此留痕**（AU-C6 教训）。
