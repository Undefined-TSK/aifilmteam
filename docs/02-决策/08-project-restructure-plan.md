# 08 · 全项目文档普查与重组 — 项目根目录重组方案

> ✅ **执行状态（2026-10-03）**：本方案已执行落地（零删除）——根级骨架（`_legacy_projects/ docs/ config/ outputs/ runtime/`）建成；`AI影视团队/`→`_legacy_projects/v1-prototype/`、`ai_film_projects/`→`_legacy_projects/v2-intermediate/` 整体迁入；`AI影视团队v2/` 原地保留。归档命名采 R-1 裁定（`_legacy_projects/` 而非 `archive/`）。文中表格为执行前记录。

> 起草人：任务三「项目根目录重组方案起草员」
> 起草日期：2026-10-03
> 性质：**仅调研 + 方案起草**。本文件未移动/删除/修改任何源文件；所有动作均为「建议」，待团队裁定后由执行阶段落地。
> 依据：`findings-04-legacy-dupes.md`（跨代重复映射 + 代际链路 + 重组建议 A~E）、`06-full-project-audit.md`（§2/§3 代际与重复集群）、`findings-01/02/03`（各代内容）、以及 `Glob`/`ls` 对 `D:\aifilmteam\` 真实结构的只读核实。
> 协同：本方案与「任务二 · 07 文档重组方案」协同但独立设计。

---

## A. 现状诊断（3.1）

### A.1 项目根目录 `D:\aifilmteam\` 顶层清单（实测）

通过 `ls`/`Glob` 只读核实，根目录当前含以下顶层项：

| 顶层项 | 类型 | 代际/性质 | 处置倾向 |
|---|---|---|---|
| `AI影视团队/` | 文件夹 | **v1 原型**（CrewAI+FastAPI 纯文本 MVP，Kimi API） | 整体移归档 |
| `ai_film_projects/` | 文件夹 | **中间代**（Hermes Profile 15 岗 Agent 体系 + 雨夜寻猫示例） | 整体移归档 |
| `AI影视团队v2/` | 文件夹 | **当前代（权威活动根）** | **保留为活动根，原地不动** |
| `negotiation/` | 文件夹 | 决策系统（轮次谈判稿 01~15 + DECISIONS 事实源） | 移入活动文档区 |
| `config/` | 文件夹 | 根级杂项配置（仅 `scalability_config.json`，2589B） | 归位为配置区 |
| `project_memory.md` | 文件(7541B,10-02) | 根级独立记忆（与中间代 MEMORY.md 内容不同，平行身份文件） | 归位记忆区 |
| `user_profile.md` | 文件(25B,10-02) | 根级独立用户画像（与 USER.md 平行） | 归位记忆区 |
| `一.md` | 文件 | 跨代共享主设计（老板主设计） | 移入文档区/主设计 |
| `二.md` | 文件 | 跨代共享主设计 | 移入文档区/主设计 |
| `三.md` | 文件(124KB) | 跨代共享主设计（下一代 C3/v3 立项材料） | 移入文档区/主设计 |
| `AI影视项目-三版本逆向分析报告.html` | 文件 | 主设计配套逆向分析报告 | 移入文档区/主设计 |
| `.audit_workspace/` | 隐藏文件夹 | 本次普查工作区（4 份 findings + 06 报告源） | 移入审计归档 |
| `.trae-html-share-packages/` | 隐藏文件夹 | 工具生成产物（Trae 分享包缓存，噪声） | 忽略规则，不删 |
| `.workbuddy/` | 隐藏文件夹 | 工具生成产物（WorkBuddy 运行时，噪声） | 忽略规则，不删 |

> 核实补充：`AI影视团队v2/` 顶层（排除 `_legacy*`）含 `PROJECT_STATE.md / spec/ agents/ projects/ docs/ pipeline/ tools/ models/ wan_runtime/ blender/ web/ assets/ logs/ config/ tests/ _inbox/`，其 `config/` 当前为空；`_legacy/` 内含 `_manifest_files.json / _manifest_migration.json / projects_雨夜寻猫/`，即 R1 对中间代资产的有意逐字冻结留档。

### A.2 命名与层级问题

- **命名不统一**：三个核心文件夹中文名 + 版本号（v1/中间代/v2）混用；`config.yaml` 同名三份但用途各异（v1 应用配置 / 中间代 Hermes Profile / v2 镜像）；`gitignore.txt`(根配置) 与 `.gitignore`(根) 命名不一致；`MEMORY.md/USER.md`（中间代）与 `project_memory.md/user_profile.md`（根级）命名漂移但内容平行。
- **层级不清晰**：决策稿 `negotiation/`、主设计 `三.md`、根记忆、根配置、三个代际文件夹全部平铺在根；运行时噪声（`.workbuddy`、`.trae-html-share-packages`、`.pytest_cache`、模型权重）与活动源码混放。
- **关键纪律**：三个核心文件夹（`AI影视团队/`、`ai_film_projects/`、`AI影视团队v2/`）**只能整体移动归档、绝不能删除**；其中 `AI影视团队v2/` 是当前活动根，原地保留；其 `_legacy_*` 子目录已是 R1 有意归档，保持原位不再复制。

---

## B. 新项目结构（3.2）—— 与文档结构协同但独立

设计原则：v2 为唯一活动根原地不动；其余代际整体移入 `_legacy_projects/`；根级文档/决策/记忆/配置/环境/输出/运行时各自归区。树深 ≤4 层。

```text
D:/aifilmteam/
├── AI影视团队v2/                    # 【活动根·原地保留】当前代权威线，内部 _legacy_* 保持原位
│   ├── PROJECT_STATE.md             #   系统入口（事实来源）
│   ├── spec/  agents/  projects/    #   契约 / 7 Agent / 雨夜寻猫(00~07)
│   ├── docs/  pipeline/             #   当前文档(R0~R4) / 管线数据
│   ├── tools/  models/  wan_runtime/  blender/  web/  assets/   # 活动代码与资产
│   ├── logs/  config/  tests/  _inbox/                       # 运行/配置/测试/收件箱
│   └── _legacy/  docs/_legacy_*  agents/_legacy_roles/       # 内部已有归档，保持
│
├── _legacy_projects/                # 【旧项目归档区·只移不删】三核心中的另两个整体移入
│   ├── v1-prototype/                #   ← AI影视团队（v1 原型，整体移动，含原 config.yaml）
│   └── v2-intermediate/             #   ← ai_film_projects（中间代，整体移动，含 tools/ 代码）
│
├── docs/                            # 【活动文档区·与 07 方案协同】
│   ├── root-design/                 #   一.md/二.md/三.md + 逆向分析报告.html（跨代主设计）
│   ├── negotiation/                 #   ← negotiation/ 决策谈判稿（保持 01~0n 编号）
│   ├── memory/                      #   ← project_memory.md / user_profile.md（当前活动记忆）
│   └── audit/                       #   ← .audit_workspace/ 本次普查产出（06+findings）
│
├── config/                          # 【配置区】解决同名 config 三份冲突（按用途命名）
│   ├── REGISTRY.md                  #   三份 config 的代际/用途对照与路径登记
│   ├── app.v1.yaml                  #   ← v1 应用配置（原 AI影视团队/config.yaml，移入后改名）
│   ├── hermes.profile.yaml          #   ← 中间代 Hermes Profile（原 ai_film_projects/config.yaml，移入后改名）
│   ├── v2.runtime.yaml              #   ← v2 运行时配置（若导出；现 v2/config/ 为空，按需创建）
│   └── scalability_config.json      #   ← 原根 config/scalability_config.json（归位）
│
├── env/                             # 【环境样例区】
│   └── v1.env.example               #   ← AI影视团队/.env.example
│
├── outputs/                         # 【输出区】成片与交付包
│   ├── deliveries/                  #   交付包
│   └── renders/                     #   渲染产物
│
├── runtime/                         # 【运行时区·全部忽略】生成物与第三方噪声
│   ├── logs/  cache/                #   运行时日志/缓存
│   ├── .pytest_cache/               #   pytest 自动生成
│   └── node_modules/                #   第三方依赖（若落盘）
│
└── archive/                         # 【附加历史归档区】
    └── audit-2026-10/               #   （可选）审计工作区归档副本
```

**层级职责说明**
1. 第 1 层：根仅保留 7 个区（`AI影视团队v2`、`_legacy_projects`、`docs`、`config`、`env`、`outputs`、`runtime`、`archive`），两两职责正交。
2. 第 2 层：活动根内部保留 v2 既有子结构（spec/agents/...）；归档区按代际分 `v1-prototype`/`v2-intermediate`；文档区按 `root-design/negotiation/memory/audit` 分。
3. 第 3 层：各代际/文档子域的固有内容，整体原样承载，不拆分。
4. 第 4 层：仅 `_legacy_projects/*` 下可能出现第 4 层（原项目内部深层目录），属「整体移动」自然延续，不新增结构。

---

## C. 迁移映射表（3.2）

> 规则：所有「移动」均为原位 relocate（只移不删）；核心三文件夹整体移动不拆分；文档副本不二次另存（见 E）。

| 现有顶层项 | 新位置 | 动作 | 备注 |
|---|---|---|---|
| `AI影视团队/` | `_legacy_projects/v1-prototype/` | 整体移动 | v1 原型整包移入；其 `config.yaml` 另在 `config/app.v1.yaml` 登记（见下） |
| `ai_film_projects/` | `_legacy_projects/v2-intermediate/` | 整体移动 | 中间代整包移入；**含 `tools/`（~30 脚本）v2 未镜像，须整体原样移，不拆分** |
| `AI影视团队v2/` | `AI影视团队v2/`（原地） | **保留** | 当前活动根，不动；`_legacy_*` 保持原位 |
| `negotiation/` | `docs/negotiation/` | 整体移动 | 决策稿保持 01~0n 编号；落地后更新内部对 三.md 的引用 |
| `config/`（根） | `config/scalability_config.json` | 移动+归位 | 仅 `scalability_config.json`，并入配置区 |
| `project_memory.md` | `docs/memory/project_memory.md` | 移动 | 当前活动记忆，与主设计/决策同级归位 |
| `user_profile.md` | `docs/memory/user_profile.md` | 移动 | 同上 |
| `一.md` | `docs/root-design/一.md` | 移动 | 跨代主设计归档 |
| `二.md` | `docs/root-design/二.md` | 移动 | 同上 |
| `三.md` | `docs/root-design/三.md` | 移动 | 注：与 `negotiation/03-*.md` 编号无冲突（分处不同区） |
| `AI影视项目-三版本逆向分析报告.html` | `docs/root-design/AI影视项目-三版本逆向分析报告.html` | 移动 | 主设计配套报告 |
| `.audit_workspace/` | `docs/audit/`（或 `archive/audit-2026-10/`） | 整体移动 | 本次普查交付物；移动后更新 06 报告中的相对引用 |
| `.trae-html-share-packages/` | （保留原位）+ `.gitignore` | 忽略 | 工具生成噪声，**不删**，仅加忽略规则 |
| `.workbuddy/` | （保留原位）+ `.gitignore` | 忽略 | 工具运行时，**不删**，仅加忽略规则 |

**config.yaml 三份冲突专项映射**（解决同名不同义）
| 原文件 | 新命名/位置 | 动作 | 用途 |
|---|---|---|---|
| `AI影视团队/config.yaml`（728B, v1 应用配置） | `config/app.v1.yaml` | 移动后改名 | 标注「v1 CrewAI/FastAPI 应用配置，已停用」 |
| `ai_film_projects/config.yaml`（814B, Hermes Profile） | `config/hermes.profile.yaml` | 移动后改名 | 标注「中间代 Hermes Agent Profile」 |
| `AI影视团队v2/docs/_legacy_source/根配置/config.yaml` | **不移动、不复制** | 保持 | 系中间代镜像的冻结副本（老板硬约束留档），作为唯一归档副本 |
| v2 自身运行时配置 | `config/v2.runtime.yaml` | 按需创建 | 若 v2 导出运行时配置则沿用此名，避免再出现同名 `config.yaml` |

> 说明：v1、中间代两份 config 改名后为「活动配置登记表」；v2 镜像那份留在 `_legacy_*` 内不重复另存。如此既消除同名碰撞，又零副本、零删除。

---

## D. 清理项清单（3.2）

> 红线：本方案**不含任何删除动作**。下列「清理」一律表达为「加入 `.gitignore` 忽略 / 标记为运行时噪声」，绝不 rm。核心三文件夹内部内容（含其 `_legacy_*`）**一律不清理、不删、不拆**。

**D.1 可加入忽略规则的运行时噪声（仅 v2 活动根内部）**
| 项 | 位置 | 判定标准 | 处理 |
|---|---|---|---|
| `.pytest_cache/` | `AI影视团队v2/` 及 `AI影视团队/.pytest_cache/` | pytest 自动生成、可重产、零人工内容 | 忽略（不删） |
| `node_modules/` | v2 `web/`、`wan_runtime/` 等 | 第三方依赖、可 `npm install` 重建 | 忽略（不删） |
| `logs/`（运行时产物） | v2 `logs/`（非 `_handoff` 历史交接 md） | 运行期滚动日志、生成物 | 忽略（交接 md 除外，保留） |
| `cache/` / 临时中间产物 | v2 各子系统 | 体积大、可重建、非源 | 忽略 |
| `models/`（权重文件） | v2 `models/` | 大体积第三方模型权重（GB 级）、可重下 | 忽略（保留目录占位） |
| `.workbuddy/`、`.trae-html-share-packages/` | 根级隐藏 | 工具生成、非项目源 | 忽略（不删） |

**D.2 清理判定标准（通用）**
1. **是否第三方/可重建**：是 → 忽略，不删（如 node_modules、模型权重、缓存）。
2. **是否自动生成物**：是 → 忽略（如 `.pytest_cache`、构建产物）。
3. **体积阈值**：单文件/目录 > 100MB 且为生成物/权重 → 忽略而非纳入版本管理。
4. **是否人工文档/源**：否 → 不清理；是 → 归位（见 B/C），绝不删。

**D.3 明确不清理的范围**
- 三个核心文件夹整体（含 `AI影视团队/`、`ai_film_projects/`、`AI影视团队v2/` 及其全部子目录、`_legacy_*`）**只移不删、不拆、不清理**。
- `negotiation/`、`三.md`、findings、06 报告等审计/决策知识资产**全部保留**。
- 任何历史交接、身份文件（MEMORY/USER/AGENTS/README）、岗位卡、docs 镜像**只归档不删**。

---

## E. 重组时的硬约束与验证（红线）

### E.1 硬约束（老板 2026-09-27「旧资产全部登记不删」）
- 所有 `_legacy_*` 及拟归档内容 **只移不删**；核心三文件夹整体移动归档不删。
- 本方案全文无任何删除指令，仅「移动 / 改名 / 忽略规则」。
- 唯一归档副本原则：**v2 的 `docs/_legacy_source/`、`agents/_legacy_roles/`、`docs/_legacy_handoff/`、`_legacy/projects_雨夜寻猫/` 已逐字覆盖中间代文档/岗位/交接/资产**（md5 SAME 核验）。因此把 `ai_film_projects` 整体移入 `_legacy_projects/` 时，**不要重复另存文档副本**——代码（`tools/`）除外，因 v2 未镜像，随 `ai_film_projects` 原样保留。即：v2 `_legacy_*` 为中间代文档唯一归档副本。

### E.2 移动后引用断链验证方法
移动会改变多处硬编码路径，须批量核查并更新：
1. **全根 grep 关键旧路径**：
   - `C:\Users\LZH\ai_film_projects\`（见 AU-D5，`ai_film_projects/AGENTS.md` 写死的错误绝对路径）→ 更新为 `D:\aifilmteam\_legacy_projects\v2-intermediate\` 或相对路径。
   - `AI影视团队\`、`ai_film_projects\`、`AI影视团队v2\` 裸名引用 → 更新为新位置。
   - `三.md`、`一.md`、`二.md` 引用（negotiation 多稿引用根级 三.md）→ 更新为 `docs/root-design/三.md`。
2. **`ai_film_projects/AGENTS.md` / `MEMORY.md` / `USER.md` / `README.md`**：移入 `_legacy_projects/v2-intermediate/` 后，内部 `C:\` 路径、岗位数口径、资产路径全部需校正（或标注「历史快照，内容已过时，以 v2 为准」）。
3. **`course/methodology/README.md`**：引用 `profiles/`、`handoffs/`（见 AU-R1，实际为 `roles/`、无根 handoffs）→ 更新为 `_legacy_projects/v2-intermediate/roles/` 或标注失效。
4. **`negotiation/` 内对 三.md 的引用**：移动至 `docs/negotiation/` 后，相对路径需批量重写为 `../root-design/三.md`。
5. **`.audit_workspace/` 移动后**：06 报告及本 08 中对 `.audit_workspace/findings-*` 的引用需同步更新为 `docs/audit/`（若采用该落点）。
6. **验证手段**：移动后执行 `grep -rn "ai_film_projects\|AI影视团队\\\\|三.md\|C:\\\\Users\\\\LZH" --include=*.md` 全根扫描，确认无悬空旧路径；对 `AGENTS.md` 关键路径人工复核。

### E.3 编号冲突二次确认（来自集群7/06 §4.2）
- `negotiation/04-one-size-fits-all-audit.md` 实为第三轮审计件，应重命名为 `03-one-size-fits-all-audit.md`（或归入审计归档），解除与真第四轮 `04-tools-mcp.md`（T1~T24）的编号冲突——**此改名属于文档区内部动作，归 07 文档方案协同执行**。
- 同理 `negotiation/05-*` 两文件（真第五轮 `05-contract-data-model.md` vs 反思 `05-global-review-reflection.md`）需对反思件改名，避免与下一代立项材料（三.md/C3）误关联。

### E.4 执行顺序建议（降低断链风险）
1. 先用本方案 + 07 方案建立新目录骨架（`_legacy_projects/`、`docs/`、`config/`、`env/`、`outputs/`、`runtime/`、`archive/`）。
2. 移动两个旧项目（`v1-prototype`、`v2-intermediate`）整体搬迁。
3. 迁移文档/决策/记忆/配置/环境到对应区。
4. 改名三份 config 并写 `config/REGISTRY.md`。
5. 批量 grep + 更新断链引用（E.2）。
6. 最后补 `.gitignore`（D 项），不删任何文件。

---

> 验收自检：新树最深 4 层（✓）；迁移表覆盖全部 15 项顶层内容（✓）；清理清单有明确判定标准且零删除（✓）；方案仅含移动/改名/忽略规则，未修改任何源文件（✓ 仅写入本 08 文件）。
