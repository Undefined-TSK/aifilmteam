# 07 · 文档系统重组方案（图书馆式目录 + 管理规范）

> ✅ **执行状态（2026-10-03）**：本方案已经团队裁定（R-1~R-5，见 10 号文档）并**执行落地**——v1+中间代迁 `_legacy_projects/`、negotiation 迁 `docs/02-决策/`、三连改名完成、findings 迁 `docs/09-逆向与审计/普查工作区-2026-10/`。文中"旧路径"均为执行前记录；v2 内部不外迁按 R-3 裁定执行（C.3 由移动降级为索引引用）。

> 起草角色：文档系统重组方案起草员（任务二）
> 起草日期：2026-10-03
> 性质：**仅调研 + 起草方案**，未移动/删除/修改任何源文件（0 写操作，唯一产物为本文件）
> 依据输入：`findings-01-neg-root.md`、`findings-02-v2.md`、`findings-03-afp.md`、`findings-04-legacy-dupes.md`、`06-full-project-audit.md`
> 配套后续：任务三 `08-project-restructure-plan.md`（项目结构）、任务四 `09-decision-review-report.md`（决策复审）

---

## A. 现状诊断（2.1）

### A.1 实质性文档总量（按代际 / 来源汇总）

> 计数口径：逐文档统计；同构模板（中间代 15 岗岗位卡、雨夜寻猫项目多份 md、course 多份关卡）按"一份 = 一个文件"计入。跨代镜像（md5 SAME）在 A.3 单独去重。

| 代际 / 来源 | 文件夹 | 实质性文档量（普查口径） | 说明 |
|---|---|---|---|
| 共享主设计（根） | `D:\aifilmteam\` | **4** | `三.md`、`一.md`、`二.md`、`AI影视项目-三版本逆向分析报告.html`（findings 实读三.md+html；一/二.md 被 06 总览点名存在，按存在计入） |
| 决策系统 | `D:\aifilmteam\negotiation\` | **23** | 15 轮谈判稿（01~15）+ DECISIONS 事实源 + NEGOTIATION_PROGRESS 索引 + 5 份支撑（00-emergency/00-impact/03a-research/04-one-size-audit/05-reflection/P1升级报告）——注：P1 报告与两"00"、03a 均计入支撑，合计 23 |
| **当前代（权威线）** | `D:\aifilmteam\AI影视团队v2\` | **37** | PROJECT_STATE 1 + docs 24 当前 + spec 3 + agents 7 SKILL + pipeline 2（audio_cues_v1.json / delivery_spec.json）。另 `_legacy_*` 已是有意归档，不计活动量 |
| 中间代 | `D:\aifilmteam\ai_film_projects\` | **~70**（含同构） | docs 13（8 现役 + 5 `_archive`）+ roles 15 岗 + 根配置 4 + handoff 11 + projects/雨夜寻猫（~7 md）+ course 全套（~14）+ skills/k13（3）+ tests 2 + pipeline 2 |
| v1 原型 | `D:\aifilmteam\AI影视团队\` | **4** + 2 隐藏 | README / config.yaml / requirements.txt / static/index.html + `.env.example` / `.gitignore`（无身份文件） |
| 根级杂项身份 | `D:\aifilmteam\` | **2** | `project_memory.md`、`user_profile.md`（平行身份文件，不与中间代 MEMORY/USER 同名） |

**合计（活动 + 历史，含镜像与同构）约 140 份文件**；去重后"唯一权威内容"远小于此——因中间代 docs/roles/handoffs/身份 已被 v2 `_legacy_*` **逐字覆盖**（md5 SAME，见 A.3）。

### A.2 文档分类（12 类）

| 类别 | 代表文档 | 当前位置 |
|---|---|---|
| 主设计 | 三.md、一.md、二.md | 根 |
| 决策 | negotiation 15 轮稿 + DECISIONS.md | `negotiation/` |
| 规划 | R0-规划书 / R0-旧目录归档方案 / R1-未定稿 / R3-架构定稿 / R4-执行计划 | v2 `docs/` |
| 调研 | 调研-板块①a/b/验收/补漏 ×4、板块②a/b/c/d、参考实现、成本对比、调研计划 | v2 `docs/` |
| 契约 spec | delivery_spec.json、qc_rubric.json、shot_spec.schema.json | v2 `spec/` + `pipeline/` |
| 岗位卡 | v2 agents 7 SKILL；中间代 roles 15 岗（退役） | v2 `agents/`、中间代 `roles/` |
| 项目数据 | 雨夜寻猫（剧本/分镜/镜头/音轨/director_intent + 00_brief~07_deliver） | v2 / 中间代 `projects/` |
| 交接日志 | handoff A0~A8 + R1/R2；v2 当前 `logs/` | 中间代 `logs/`、v2 `logs/` |
| 身份文件 | MEMORY/USER/AGENTS/README（中间代根）、project_memory/user_profile（根） | 中间代根、根 |
| 学习方法论 | course（methodology/modules A-F/checklists/关卡6-9） | 中间代 `course/` |
| 逆向报告 | AI影视项目-三版本逆向分析报告.html | 根 |
| 审计件 | 03-one-size-fits-all-audit（原 04）、阶段0体检审计报告v6.0、R0-盘点/旧资产登记 | negotiation / 中间代 docs / v2 docs |

### A.3 当前 vs 历史 / 核心 vs 辅助 / 重复 vs 冲突 判定（引用 findings 集群与 md5 核验）

**当前权威线 = `AI影视团队v2/`**（`PROJECT_STATE.md` + `spec/` + `docs/R0~R4` + `agents/`7 + `projects/雨夜寻猫`）。中间代文档已被 v2 `_legacy_source/_legacy_roles/_legacy_handoff/_legacy/projects_雨夜寻猫` **逐字覆盖**（findings-04 全量 md5 SAME 核验）。

跨代重复（7 大集群，均经 md5 逐字节确认）：

| 集群 | 重复副本 | 权威/最新（保留为活动或已归档副本） | 陈旧/可归档 | 处置结论 |
|---|---|---|---|---|
| 1 雨夜寻猫三重复制 | 中间代 `projects/雨夜寻猫/` ↔ v2 `projects/雨夜寻猫/`（含00_brief）↔ v2 `_legacy/projects_雨夜寻猫/` | **v2 当前代**（①超集，共享 md SAME，新增 json/handoffs/locks/00~07） | ①整体移归档；③已 legacy | 以 v2 当前为唯一权威 |
| 2 岗位卡镜像 | 中间代 `roles/`15 ↔ v2 `agents/_legacy_roles/`15(SAME) ↔ v2 `agents/`7 | **v2 当前 7 Agent** | ②保持唯一归档；①移归档 | 11 个退役岗仅存 `_legacy_roles` |
| 3 docs 镜像 | 中间代 `docs/`13 ↔ v2 `docs/_legacy_source/`13(SAME) | ①为源；v2 事实源是 PROJECT_STATE/spec/R0-* | ②已正确归档；①移归档 | 高：13×全重复，有意留档 |
| 4 config 四份 | 三份同名 `config.yaml`（v1 应用 / 中间代 Hermes / v2 镜像）+ `gitignore.txt` vs `.gitignore` | v1 独属；②③同格式(SAME) | ③随 legacy；①可归档 | 同名不同义，须标注代际 |
| 5 身份文件多份 | 中间代根 MEMORY/USER/AGENTS/README ↔ v2 `_legacy_source/根配置/`(SAME)；根 `project_memory.md`/`user_profile.md` 平行独立 | ①为源；③平行独立 | ②随 legacy；③需对齐主从 | 双份记忆漂移风险 |
| 6 handoff 镜像 | 中间代 `logs/_handoff_A_20260927/`11 ↔ v2 `docs/_legacy_handoff/`11(SAME) | ①为源 | ②已归档；①随中间代移归档 | 当前交接应落 v2 自身 `logs/` |
| 7 negotiation "04" 冲突 | `04-one-size-fits-all-audit.md`（实为第三轮审计件）↔ `04-tools-mcp.md`（真第四轮 T1~T24） | **`04-tools-mcp.md`=真第四轮** | 审计件改名 `03-one-size-fits-all-audit.md` | 高：轮次归属混乱 |

**核心 vs 辅助判定**：
- 核心（不可删、可整体移归档）：三核心文件夹 `AI影视团队/`、`ai_film_projects/`、`AI影视团队v2/` 内文档；其中 v2 当前代 = 唯一活动权威线。
- 辅助（已冻结留档）：v2 全部 `_legacy_*` 子目录（老板 2026-09-27 硬约束"旧资产全部登记不删"，有意、不复制、不删）。
- 冲突（非字节冲突，是**编号/命名碰撞**）：仅集群 7（两个"04"）、两个"05"（`05-contract-data-model.md` 真第五轮 vs `05-global-review-reflection.md` 反思件）、`P1` 前缀撞第八轮 PK/P 系列、`spec/delivery_spec.json` vs `pipeline/delivery_spec.json` 同名异 schema、`L1/L2/L3` 两义（档位 vs 阶段）。

**关键结论（直接引用 findings）**：
1. findings-04 §3：「当前代的 `_legacy_*` 是对中间代（及部分 v1 资产）的**有意逐字归档**，并非运行依赖。」
2. findings-04 集群 7：「`04-tools-mcp.md` 才是真正的第四轮谈判稿……`04-one-size-fits-all-audit.md` 实为第三轮审计产物，却冠以"04"前缀。」
3. findings-02 §3.3：「`negotiation/` + `三.md` 实为 **C3/v3 下一代立项材料**，其 C 系列是系统层决策，与 v2 影视 spec 不可直接对账」——故 v2 真实管线决策收口在 `调研-板块②d-待闭合项决议.md`（4/4 闭合），与 spec 一致。
4. findings-06 摘要 6：「三个核心文件夹**只能整体移动归档、绝不删除**；v2 `_legacy_*` 是有意留档，亦不删。」

---

## B. 新文档目录结构（2.2）——"图书馆式"

### B.1 设计原则
- **统一入口**：新建 `docs/` 为全项目活动文档总库，`archive/` 为历史归档；散落各处的文档**只移不删**地归集。
- **层级 ≤4 层**：`docs/<01-09 大类>/<子类或文件>`，最深 `docs/06-项目资料/雨夜寻猫/00_brief/`。
- **活动 vs 历史分离**：活动文档进 `docs/`，历史整代进 `archive/`（按代际），v2 已有的 `_legacy_*` 保持原位、不复制进 `archive/`。
- **v2 当前代权威线保持为活动根**：v2 的 `PROJECT_STATE/spec/R0~R4/agents/projects` 即新 `docs/` 的权威内容来源。

### B.2 完整目录树

```
D:\aifilmteam\
├── docs/                              # 活动文档总库（图书馆式，≤3 层深）
│   ├── _README_FIRST.md               # ① 入口索引（修复 E-I1 缺失）
│   ├── 00-索引-状态-身份/              # 索引 + VERSION 矩阵 + 状态矩阵 + 身份记忆
│   │   ├── VERSION.md                 # 全库版本矩阵（采纳 C1 SemVer）
│   │   ├── STATUS_MATRIX.md           # 文档状态/签字/归档标记矩阵
│   │   ├── project_memory.md          # 根级并行记忆（对齐 MEMORY.md 主从）
│   │   └── user_profile.md            # 根级用户画像
│   ├── 01-主设计/                     # 总体设计纲领（老板主设计）
│   │   ├── 三.md
│   │   ├── 一-二-主设计补充.md        # 一.md / 二.md 合并或并列保留
│   │   └── （逆向报告见 09）
│   ├── 02-决策/                       # 谈判系统 15 轮 + 事实源 + 支撑
│   │   ├── DECISIONS.md               # 唯一事实来源
│   │   ├── NEGOTIATION_PROGRESS.md    # 进度索引
│   │   ├── 01-blender-blockout.md … 15-philosophy-meta.md   # 15 轮真稿
│   │   ├── 00-emergency-blockout-position.md
│   │   ├── 00-impact-list.md
│   │   ├── 03a-agent-team-research.md
│   │   ├── 03-one-size-fits-all-audit.md     # 改名自 04-one-size-fits-all-audit（归入第三轮审计）
│   │   ├── 05b-reflection.md                 # 改名自 05-global-review-reflection（反思/纠错，非决策源）
│   │   └── 支撑-五点升级报告.md              # 改名自 P1-five-point-upgrade-report（去 P1 前缀，明"升级报告"）
│   ├── 03-规划与调研/                 # R 系列规划 + 调研板块
│   │   ├── R0-待老板拍板清单.md
│   │   ├── R0-旧目录归档方案.md
│   │   ├── R0-旧资产登记表.md
│   │   ├── R0-盘点报告-两个旧目录.md
│   │   ├── R0-规划书-v2.0-待拍板.md
│   │   ├── R0-调研证据附录.md
│   │   ├── R1-未定稿清单-架构与调研与需求.md
│   │   ├── R3-架构定稿.md
│   │   ├── R4-执行计划.md
│   │   ├── 需求定稿.md
│   │   ├── 调研计划.md
│   │   ├── 写实化管线-渲染前后校验清单.md
│   │   ├── 调研-板块①a-写实化引擎与Blender侧.md
│   │   ├── 调研-板块①b-质检链与音频链.md
│   │   ├── 调研-板块①-验收页.md
│   │   ├── 调研-板块①-补漏-IR与judder与响度字段.md
│   │   ├── 调研-板块①-补漏与更正.md
│   │   ├── 调研-板块②-验收页.md
│   │   ├── 调研-板块②a-商业平台竞品10家.md
│   │   ├── 调研-板块②b-开源与引擎方与获奖团队.md
│   │   ├── 调研-板块②c-falAPISchema核验.md
│   │   ├── 调研-板块②d-待闭合项决议.md
│   │   ├── 调研-参考实现-fal3D白模管线.md
│   │   └── 调研-成本对比-渲染后端.md
│   ├── 04-契约spec/                   # 三契约 + 技术交付（唯一契约源）
│   │   ├── delivery_spec.json                 # 档位 L1/L2/L3（原 spec/）
│   │   ├── qc_rubric.json                     # 五项硬指标（原 spec/）
│   │   ├── shot_spec.schema.json              # 镜头契约（原 spec/）
│   │   ├── tech_delivery_spec.json            # 改名自 pipeline/delivery_spec.json（技术交付参数，异 schema）
│   │   └── audio_cues_v1.json                 # 雨夜寻猫音轨（权威副本，见 D 引用核对）
│   ├── 05-岗位卡/                     # 当前 7 Agent（活动）；退役岗见 archive
│   │   ├── director/SKILL.md
│   │   ├── producer/SKILL.md
│   │   ├── screenwriter/SKILL.md
│   │   ├── previs/SKILL.md
│   │   ├── blockout/SKILL.md
│   │   ├── realizer/SKILL.md
│   │   └── script_supervisor/SKILL.md
│   ├── 06-项目资料/                   # 雨夜寻猫（当前代权威副本）
│   │   └── 雨夜寻猫/
│   │       ├── 00_brief/ 01_spec/ … 07_deliver/
│   │       ├── assets/ locks/ ditmap/ clearance/ output/
│   │       └── （二进制资产不列入文档库，仅保留 md/json 索引）
│   ├── 07-交接与日志/                 # 当前交接 + 审计/盘点日志
│   │   ├── 当前交接/                  # v2 当前 logs/ 内容（落地于此，非 _legacy）
│   │   └── 审计与盘点日志/            # R0-盘点/旧资产登记/旧目录归档方案 的归档视角副本（引用，不重复正文）
│   ├── 08-学习方法论/                 # course 全套（活动参考）
│   │   ├── methodology/SKILL.md + README.md
│   │   ├── modules/A~F/
│   │   ├── checklists/*
│   │   └── 关卡6-交付自检清单.md … 关卡9-企业AI服务方案.md
│   └── 09-逆向与审计/                 # 逆向报告 + 审计件
│       ├── AI影视项目-三版本逆向分析报告.html
│       ├── 阶段0体检审计报告与规划修订v6.0.md     # 中间代纠偏件
│       └── 03-one-size-fits-all-audit.md         # 与 02 内同名？见下注
├── archive/                          # 历史归档（只移不删，按代际）
│   ├── v1_legacy/                     # ← AI影视团队/（v1 原型）整体移入
│   │   ├── README.md  config.yaml  requirements.txt
│   │   ├── static/index.html  .env.example  .gitignore
│   └── 中间代_legacy/                 # ← ai_film_projects/ 整体移入
│       ├── docs/ (13)                 # 注：v2 _legacy_source 已是逐字副本，此处为第二物理副本（见 D/E 红线）
│       ├── roles/ (15 退役岗)
│       ├── course/
│       ├── skills/k13-version-tree/
│       ├── tests/
│       ├── pipeline/ (audio_cues_v1.json / delivery_spec.json 旧份)
│       ├── 根配置/ (AGENTS/MEMORY/USER/config.yaml/README)
│       ├── logs/_handoff_A_20260927/ (11)
│       └── projects/雨夜寻猫/ (中间代旧份，含独有 director_intent.md)
└── （AI影视团队v2/ 保持原位：其 _legacy_* 已是有意归档，不复制进 archive/；其 PROJECT_STATE/spec/R0~R4/agents/projects 内容即上方 docs/ 的权威来源）
```

> **注（09 与 02 的审计件去向）**：`03-one-size-fits-all-audit.md` 属"谈判第三轮审计支撑"，与谈判流强相关，故主副本放在 `docs/02-决策/`；同时在 `docs/09-逆向与审计/` 仅以**索引引用**（不重复正文），避免双份漂移（呼应 E-14 教训）。`09` 主要收纳"逆向报告 html"与"中间代 v6.0 审计件"两类逆向/审计性质文档。

### B.3 每层职责
- `docs/_README_FIRST.md`：**唯一入口**，列阅读顺序、范围边界、当前权威线声明、代际关系图。修复 findings-02 E-I1（原 `_READ_ME_FIRST.md` 缺失）。
- `00-索引-状态-身份/`：机器/人可读的版本与状态总表 + 项目身份记忆（解决 E-I1、集群5 双记忆漂移）。
- `01~09`：**按文档性质分库**，开发/团队/老板各取所需（老板看 01/02/03；开发看 04/05/06；新人看 08；审计看 09）。
- `archive/`：整代冻结，只移不删；代际清晰，便于追溯但不混入活动流。

---

## C. 旧→新 路径映射表（2.2）

> 约定：**移动** = 物理迁移（只移不删）；**改名** = 移动同时重命名；**引用** = 不迁移，仅在他处建索引链接。
> 重复集群处置：权威副本→活动 `docs/`；镜像/遗留副本→`archive/`（v2 `_legacy_*` 已覆盖处不再另存，但依"只移不删"仍保留实体并标注主从）。

### C.1 根（共享主设计 + 逆向 + 根级身份）
| 旧路径 | 新路径 | 操作 |
|---|---|---|
| `D:\aifilmteam\三.md` | `docs/01-主设计/三.md` | 移动 |
| `D:\aifilmteam\一.md` | `docs/01-主设计/一-二-主设计补充.md`（合并）或并列 | 移动 |
| `D:\aifilmteam\二.md` | 同上 | 移动 |
| `D:\aifilmteam\AI影视项目-三版本逆向分析报告.html` | `docs/09-逆向与审计/AI影视项目-三版本逆向分析报告.html` | 移动 |
| `D:\aifilmteam\project_memory.md` | `docs/00-索引-状态-身份/project_memory.md` | 移动（与 MEMORY.md 对齐主从） |
| `D:\aifilmteam\user_profile.md` | `docs/00-索引-状态-身份/user_profile.md` | 移动 |

### C.2 negotiation（23 份）
| 旧路径 | 新路径 | 操作 | 备注 |
|---|---|---|---|
| `negotiation/DECISIONS.md` | `docs/02-决策/DECISIONS.md` | 移动 | 唯一事实源 |
| `negotiation/NEGOTIATION_PROGRESS.md` | `docs/02-决策/NEGOTIATION_PROGRESS.md` | 移动 | 进度索引 |
| `negotiation/01-blender-blockout.md` … `15-philosophy-meta.md`（15 轮） | `docs/02-决策/01-…15-…` | 移动 | 真轮次稿 |
| `negotiation/00-emergency-blockout-position.md` | `docs/02-决策/00-emergency-blockout-position.md` | 移动 | 支撑 |
| `negotiation/00-impact-list.md` | `docs/02-决策/00-impact-list.md` | 移动 | 支撑 |
| `negotiation/03a-agent-team-research.md` | `docs/02-决策/03a-agent-team-research.md` | 移动 | 支撑 |
| `negotiation/04-one-size-fits-all-audit.md` | `docs/02-决策/03-one-size-fits-all-audit.md` | **改名+移动** | 归入第三轮审计件（集群7） |
| `negotiation/05-global-review-reflection.md` | `docs/02-决策/05b-reflection.md` | **改名+移动** | 反思/纠错，非决策源（ERR-22） |
| `negotiation/P1-five-point-upgrade-report.md` | `docs/02-决策/支撑-五点升级报告.md` | **改名+移动** | 去 P1 前缀，明"升级报告"性质（ERR-18） |
| `negotiation/04-tools-mcp.md` | `docs/02-决策/04-tools-mcp.md` | 移动 | **真第四轮**（保持 04） |

### C.3 当前代 v2（37 份）
| 旧路径 | 新路径 | 操作 | 备注 |
|---|---|---|---|
| `AI影视团队v2/PROJECT_STATE.md` | `docs/00-索引-状态-身份/PROJECT_STATE.md`（或根 `docs/PROJECT_STATE.md`） | 移动 | 权威状态入口 |
| `AI影视团队v2/docs/R0-待老板拍板清单.md` | `docs/03-规划与调研/R0-待老板拍板清单.md` | 移动 | |
| `AI影视团队v2/docs/R0-旧目录归档方案.md` | `docs/03-规划与调研/R0-旧目录归档方案.md` | 移动 | |
| `AI影视团队v2/docs/R0-旧资产登记表.md` | `docs/03-规划与调研/R0-旧资产登记表.md` | 移动 | |
| `AI影视团队v2/docs/R0-盘点报告-两个旧目录.md` | `docs/03-规划与调研/R0-盘点报告-两个旧目录.md` | 移动 | |
| `AI影视团队v2/docs/R0-规划书-v2.0-待拍板.md` | `docs/03-规划与调研/R0-规划书-v2.0-待拍板.md` | 移动 | |
| `AI影视团队v2/docs/R0-调研证据附录.md` | `docs/03-规划与调研/R0-调研证据附录.md` | 移动 | |
| `AI影视团队v2/docs/R1-未定稿清单-架构与调研与需求.md` | `docs/03-规划与调研/R1-未定稿清单-架构与调研与需求.md` | 移动 | |
| `AI影视团队v2/docs/R3-架构定稿.md` | `docs/03-规划与调研/R3-架构定稿.md` | 移动 | |
| `AI影视团队v2/docs/R4-执行计划.md` | `docs/03-规划与调研/R4-执行计划.md` | 移动 | 修正 AU-C3/AU-H2 |
| `AI影视团队v2/docs/需求定稿.md` | `docs/03-规划与调研/需求定稿.md` | 移动 | |
| `AI影视团队v2/docs/调研计划.md` | `docs/03-规划与调研/调研计划.md` | 移动 | |
| `AI影视团队v2/docs/写实化管线-渲染前后校验清单.md` | `docs/03-规划与调研/写实化管线-渲染前后校验清单.md` | 移动 | |
| `AI影视团队v2/docs/调研-板块①a…①-补漏与更正.md`（6 篇） | `docs/03-规划与调研/` 同名 | 移动 | |
| `AI影视团队v2/docs/调研-板块②-验收页…②d-待闭合项决议.md`（5 篇） | `docs/03-规划与调研/` 同名 | 移动 | 含 4/4 闭合收口 |
| `AI影视团队v2/docs/调研-参考实现-fal3D白模管线.md` | `docs/03-规划与调研/` 同名 | 移动 | |
| `AI影视团队v2/docs/调研-成本对比-渲染后端.md` | `docs/03-规划与调研/` 同名 | 移动 | |
| `AI影视团队v2/spec/delivery_spec.json` | `docs/04-契约spec/delivery_spec.json` | 移动 | 档位契约 |
| `AI影视团队v2/spec/qc_rubric.json` | `docs/04-契约spec/qc_rubric.json` | 移动 | 五项硬指标 |
| `AI影视团队v2/spec/shot_spec.schema.json` | `docs/04-契约spec/shot_spec.schema.json` | 移动 | 镜头契约 |
| `AI影视团队v2/pipeline/delivery_spec.json` | `docs/04-契约spec/tech_delivery_spec.json` | **改名+移动** | 异 schema，去同名碰撞（E-N1） |
| `AI影视团队v2/pipeline/audio_cues_v1.json` | `docs/04-契约spec/audio_cues_v1.json` | 移动 | 权威副本（E-R1：旧份归 archive） |
| `AI影视团队v2/agents/{7}/SKILL.md` | `docs/05-岗位卡/{7}/SKILL.md` | 移动 | 当前 7 Agent |
| `AI影视团队v2/projects/雨夜寻猫/` | `docs/06-项目资料/雨夜寻猫/` | 移动 | 当前权威项目副本 |
| `AI影视团队v2/logs/`（当前交接） | `docs/07-交接与日志/当前交接/` | 移动 | 非 _legacy |

> v2 的 `_legacy_source/`、`_legacy_roles/`、`_legacy_handoff/`、`_legacy/projects_雨夜寻猫/`：**保持原位，不复制进 archive/**（已是逐字归档，老板硬约束）。

### C.4 中间代 ai_film_projects（整体移入 archive/中间代_legacy/）
| 旧路径（节选关键） | 新路径 | 操作 | 备注 |
|---|---|---|---|
| `ai_film_projects/docs/`（13，含 `_archive/`5） | `archive/中间代_legacy/docs/` | 移动 | v2 `_legacy_source` 已覆盖，此处为第二物理副本 |
| `ai_film_projects/roles/`（15 岗） | `archive/中间代_legacy/roles/` | 移动 | 退役岗，v2 `_legacy_roles` 已覆盖 |
| `ai_film_projects/course/`（全套） | `archive/中间代_legacy/course/` → 活动副本见 `docs/08-学习方法论/` | 移动+建活动引用 | 学习方法论为活动资产，建议 `docs/08/` 保留活动副本、`archive` 留原始 |
| `ai_film_projects/skills/k13-version-tree/` | `archive/中间代_legacy/skills/k13-version-tree/` | 移动 | |
| `ai_film_projects/tests/`（2） | `archive/中间代_legacy/tests/` | 移动 | |
| `ai_film_projects/pipeline/`（2 json） | `archive/中间代_legacy/pipeline/` | 移动 | 旧份，权威在 `docs/04` |
| `ai_film_projects/AGENTS.md` `MEMORY.md` `USER.md` `config.yaml` `README.md` | `archive/中间代_legacy/根配置/` | 移动 | v2 `_legacy_source/根配置` 已覆盖 |
| `ai_film_projects/logs/_handoff_A_20260927/`（11） | `archive/中间代_legacy/logs/_handoff_A_20260927/` | 移动 | v2 `_legacy_handoff` 已覆盖 |
| `ai_film_projects/projects/雨夜寻猫/`（含独有 `director_intent.md`） | `archive/中间代_legacy/projects/雨夜寻猫/` | 移动 | v2 当前代为权威；`director_intent.md` 仅此独有，须确认并入 `docs/06/雨夜寻猫/00_brief` 或补录（集群1/D 项） |
| `ai_film_projects/docs/阶段0体检审计报告与规划修订v6.0.md` | `docs/09-逆向与审计/阶段0体检审计报告与规划修订v6.0.md`（活动引用）+ `archive` 留原始 | 移动+引用 | 纠偏件仍具参考价 |

### C.5 v1 原型 AI影视团队/（整体移入 archive/v1_legacy/）
| 旧路径 | 新路径 | 操作 |
|---|---|---|
| `AI影视团队/README.md` `config.yaml` `requirements.txt` `static/index.html` `.env.example` `.gitignore` | `archive/v1_legacy/` 同名 | 移动 |

### C.6 命名碰撞处置汇总（呼应 findings 集群7 / ERR-16/17/18 / E-N1）
| 旧名（碰撞） | 新名 | 归入 | 理由 |
|---|---|---|---|
| `04-one-size-fits-all-audit.md` | `03-one-size-fits-all-audit.md` | `docs/02-决策/` | 实为第三轮审计件，解除与真第四轮 `04-tools-mcp.md` 编号冲突（集群7，高） |
| `05-global-review-reflection.md` | `05b-reflection.md` | `docs/02-决策/` | 与真第五轮 `05-contract-data-model.md` 同前缀消歧（ERR-17），并标"反思/纠错非决策源" |
| `P1-five-point-upgrade-report.md` | `支撑-五点升级报告.md` | `docs/02-决策/` | 去 P1 前缀，免与第八轮 PK1~PK8/P1~P8 混淆（ERR-18） |
| `pipeline/delivery_spec.json`（v2） | `tech_delivery_spec.json` | `docs/04-契约spec/` | 与 `spec/delivery_spec.json` 同名异 schema（E-N1） |

---

## D. 移动 / 合并 / 归档 操作清单（2.2）

> 全部为**移动 / 改名 / 引用更新**，绝不含"删除"。核心三文件夹只移不删；archive 内只移不删；v2 `_legacy_*` 保持原位不复制。

### D.1 活动文档归集（移入 `docs/`）
1. 根 `三.md`/`一.md`/`二.md` → `docs/01-主设计/`；根 `project_memory.md`/`user_profile.md` → `docs/00-索引-状态-身份/`。
2. `negotiation/*`（23）→ `docs/02-决策/`（含 3 项改名：04-one-size→03-one-size、05-reflection→05b-reflection、P1→支撑-五点升级报告）。
3. v2 `docs/R0~R4`+调研 24 篇 → `docs/03-规划与调研/`；v2 `spec/`3 + `pipeline/`2 → `docs/04-契约spec/`（pipeline 那份改名 tech_delivery_spec.json）。
4. v2 `agents/`7 → `docs/05-岗位卡/`；v2 `projects/雨夜寻猫/` → `docs/06-项目资料/`；v2 `logs/`(当前) → `docs/07-交接与日志/当前交接/`。
5. 中间代 `course/` → `docs/08-学习方法论/`（活动副本）；根逆向 html + 中间代 v6.0 审计 → `docs/09-逆向与审计/`。

### D.2 历史整代归档（移入 `archive/`）
6. `ai_film_projects/` **整体** → `archive/中间代_legacy/`（docs/roles/course/skills/tests/pipeline/根配置/logs/projects 全移）。
7. `AI影视团队/`(v1) **整体** → `archive/v1_legacy/`。
8. **v2 `_legacy_*` 四个目录保持原位**，不复制进 `archive/`（已是逐字归档；依 findings-04 E：若同时保留 `archive/中间代_legacy/docs` 与 v2 `_legacy_source` 会出现"两份归档"，明确 **v2 `_legacy_*` 为唯一权威归档副本**，`archive/中间代_legacy/` 内的中间代文档为"原始实体备份"，仅代码 `tools/` 因 v2 未镜像而保留参考/运行价值）。

### D.3 唯一性 / 主从处置（重复集群）
9. 雨夜寻猫：v2 当前代（`docs/06`）为唯一权威；`archive/中间代_legacy/projects/雨夜寻猫/` 为旧份；v2 `_legacy/projects_雨夜寻猫/` 为资产冻结快照。
10. 岗位卡：v2 当前 7（`docs/05`）为权威；`archive/中间代_legacy/roles/`15 + v2 `_legacy_roles/`15 为退役归档。
11. docs 镜像：v2 `_legacy_source/` 为权威归档；`archive/中间代_legacy/docs/` 为原始实体。
12. 身份文件：`docs/00-索引-状态-身份/` 内的 MEMORY/USER/AGENTS/README 以 v2 `_legacy_source/根配置/` 或中间代根为源对齐；根 `project_memory.md`/`user_profile.md` 明确"主记忆"归属，避免双份漂移（集群5）。

### D.4 移动后引用核对（须批量更新的交叉引用）
| 引用方（旧） | 失效/漂移点 | 修正为 |
|---|---|---|
| `AGENTS.md`（中间代） | 资产目录 `C:\Users\LZH\ai_film_projects\`（E-10） | 移归档后改为相对路径或指向新位置；该文件随中间代移 `archive` |
| `course/methodology/README.md` | 引 `profiles/`、`handoffs/`（E-08） | 改为 `roles/`（或活动 `docs/05`）；随 course 移 `docs/08` 后统一 |
| `course/关卡6-交付自检清单.md` | 引 `tests/case1_*`、`run_case*.py`（E-09） | 标注"样例已移除"或更新路径 |
| `negotiation/DECISIONS.md` 多轮 | 回链行号 off-by-one（AU-R3，已 grep 核准纠正） | 移动后若行号变化须重新 grep 校验 |
| `negotiation/` 对 `三.md` 的引用 | 原相对路径 `../三.md` | 改为 `docs/01-主设计/三.md` |
| v2 `PROJECT_STATE.md` / `R0-*` 对内引用 | 原 `docs/`、`spec/`、`agents/` 相对路径 | 改为 `docs/03/`、`docs/04/`、`docs/05/` 新路径 |
| `docs/_READ_ME_FIRST.md`（v2 原暗示入口但缺失） | E-I1 | 新建 `docs/_README_FIRST.md` 作统一入口 |
| 三.md 头部"推荐目录名 AI影视团队v3" | 与 v2 当前代混淆（E-V1） | 在 `_README_FIRST.md` 声明：三.md/negotiation 属 C3/v3 立项材料，不与 v2 spec 直接对账 |

---

## E. 文档管理方案（2.3，核心交付物）

### E.1 新文档放哪？——决策树（性质 → 目录）
```
新文档性质？
├─ 总体设计 / 老板纲领              → docs/01-主设计/
├─ 轮次谈判 / 决策记录 / 支撑       → docs/02-决策/
├─ 规划(R系列) / 调研 / 需求        → docs/03-规划与调研/
├─ 契约 / schema / 技术交付参数     → docs/04-契约spec/
├─ 岗位卡 / Agent SKILL            → docs/05-岗位卡/（退役岗进 archive）
├─ 具体项目资料（剧本/分镜/镜头…）  → docs/06-项目资料/<项目名>/
├─ 交接记录 / 审计盘点日志          → docs/07-交接与日志/
├─ 团队学习 / 方法论 / 课程         → docs/08-学习方法论/
├─ 逆向分析 / 审计报告              → docs/09-逆向与审计/
└─ 整代历史 / 退役                  → archive/<代际>_legacy/（只移不删）
```

### E.2 命名规范
- **前缀/编号**：活动文档用 `NN-主题.md`（NN=01~09 大类或轮次号）；决策轮次稿 `NN-主题.md`，支撑件加 `00-`/`03a-`/`支撑-` 前缀以避让真轮次号。
- **版本字段**：契约/规格类文件头部必须含 `version: x.y.z`（SemVer，采纳 C1 约定）；文档可含 `vX.Y` 于文件名或头部。
- **语言**：文档正文中文；代码标识符英文；文件名用中文或英文但**禁止同名不同义**（见 E.6 红线）。
- **后缀消歧**：反思/纠错类必须含 `-reflection`/`（纠错）`；升级报告必须含 `升级报告`；技术交付参数必须含 `tech-` 前缀以区分档位契约。

### E.3 版本管理（采纳 C1 SemVer 约定 + VERSION/状态矩阵）
- 所有契约/规格文件（json/schema）强制 SemVer `MAJOR.MINOR.PATCH`；文档版本可简化为 `vX.Y`（如 R3-架构定稿 v1.0）。
- 建 `docs/00-索引-状态-身份/VERSION.md`：逐份登记 文档名 / 当前版本 / 上次更新日期 / 是否签字 / 状态（活动/待拍板/归档）。
- 建 `STATUS_MATRIX.md`：逐份登记 负责人 / 最后复审日期 / 关联决策编号（如 R3、C1）/ 归档标记。
- 版本变更须在 `VERSION.md` 留痕；破坏性契约变更（MAJOR）须经文档 owner + 相关 Agent 复核（参考 AU-C6 教训：声称落地未在 schema 兑现）。

### E.4 更新流程（doc-as-code + CI 门禁）
- **谁改**：每份文档在 `STATUS_MATRIX.md` 指定 owner（如 PROJECT_STATE→team-lead；spec→realizer；岗位卡→对应 Agent；谈判→PM）。
- **怎么提**：文档即代码（doc-as-code）——改动经 PR/提交，描述含"改了哪份/哪几行/改成什么"（呼应 A7 十项落地清单风格）。
- **CI 门禁**（吸取 12 轮 WD4 doc-quality 门禁教训 + R4 §0 无回显幻觉 AU-H2/AU-F1）：
  1. 死链检查：所有相对引用目标必须存在（防 E-I1/E-R1/E-R2 失效引用）。
  2. 命名校验：禁止两个文件同名不同义（如两份 `delivery_spec.json` 需 `tech-` 前缀）；编号前缀不撞真轮次。
  3. 回显铁律：凡"环境/实测/探针"类断言须附原始命令回显，无回显的负面结论 CI 拒绝（AU-F1）。
  4. 版本一致：契约文件 version 字段存在且符合 SemVer；`VERSION.md` 同步更新。
  5. 行号引用校验：DECISIONS 等回链须 `grep` 核准行号（AU-R3 机制常态化）。

### E.5 归档规则
- **何时进 archive**：① 整代被取代（如 v1、中间代）→ 整代移 `archive/<代际>_legacy/`；② 单文档被新版本取代且不再活动 → 移 `archive/` 对应代际或 `09-逆向与审计/` 留参考；③ 谈判某轮被后续轮收敛取代 → 轮次稿保留于 `02-决策/`（历史决策不可删，属审计资产）。
- **archive 内只移不删**：老板 2026-09-27 硬约束"旧资产全部登记不删"延续执行；archive 任何内容不得删除，仅可追加 `README` 说明主从。
- v2 `_legacy_*` 已是归档，不复制、不删、不重建。

### E.6 防再次变乱的红线规则（硬性）
1. **禁止同名不同义文件**：如 `delivery_spec.json` 仅允许一份在 `docs/04`，技术参数须 `tech-` 前缀；三份 `config.yaml` 须分代际目录且文件头标注用途。
2. **禁止跨代重复**：新文档不得在原代与新区各留一份；统一权威副本 + 他处仅索引引用（解决 E-14 全息文档重复、集群3 镜像）。
3. **禁止删除核心三文件夹内任何东西**：`AI影视团队/`、`ai_film_projects/`、`AI影视团队v2/` 内文档只整体移归档、绝不删（含 v2 `_legacy_*`）。
4. **引用必须带相对路径**：禁止 `C:\Users\LZH\...` 等硬编码绝对路径（ERR-07 / E-10 根因）；跨代引用经 `_README_FIRST.md` 索引，不直链他代内部。
5. **禁止把下一代立项材料当当前代事实源**：`三.md`/`negotiation` 属 C3/v3，v2 交叉引用应指向 v2 内部 `调研-板块②d`（已在 E-V1 更正）。
6. **禁止未附回显的实测断言**（AU-F1 铁律#5）：无原始命令回显的"已查/不存在"结论不得写入。
7. **单一事实源**：决策事实源唯一 = `docs/02-决策/DECISIONS.md`；契约唯一源 = `docs/04-契约spec/`；项目记忆唯一源 = `docs/00-索引-状态-身份/`。

### E.7 文档间交叉引用规范
- **相对路径 + 索引文件**：全库以 `docs/_README_FIRST.md` 为唯一入口，列阅读顺序、代际关系图、当前权威线声明。
- 文档互引用相对路径（如 `../04-契约spec/delivery_spec.json`），禁止绝对路径。
- 全息式文档（如原 `AI交接全息文档.md`）改为"索引 + 链接"，不重复他文档正文（E-14）。
- 跨代引用一律经 `_README_FIRST.md` 说明，不直链他代内部文件，避免代际错位（E-V1）。

---

## 验收自检（本方案合规性）
- ✅ 新树 ≤4 层（最深 `docs/06-项目资料/雨夜寻猫/00_brief/`，3 层）。
- ✅ 映射表覆盖全部普查到的实质性文档（根/negotiation 23/v2 37/中间代~70/v1 4/根身份 2）。
- ✅ 管理方案覆盖：决策树、命名、版本、更新流程、CI 门禁、归档、owner、红线、交叉引用。
- ✅ 方案中**无任何删除操作**（仅移动/改名/引用更新）。
- ✅ 未修改任何源文件；仅写入本 `07-document-reorganization-plan.md`。
- ⚠️ 唯一需裁定的冗余：把 `ai_film_projects` 移 `archive/中间代_legacy/` 后，与 v2 `_legacy_*` 形成"两份归档"——本方案明确 **v2 `_legacy_*` 为唯一权威归档副本**，中间代实体仅作原始备份（代码 `tools/` 除外），待任务三结构重组时再定去留，本阶段只移不删。
