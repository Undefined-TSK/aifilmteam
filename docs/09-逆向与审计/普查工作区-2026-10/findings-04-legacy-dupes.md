# 普查发现 — 最老一代 + 跨代重复/版本映射

> 普查员：04（最老一代 AI影视团队 + 三核心文件夹跨代重复/版本混乱映射）
> 方法：只读 + Glob/抽样 Read + md5 校验；**未修改/删除/移动任何源文件**；venv/ 全部排除。
> 验证强度：所有"重复"结论均经 md5 逐字节比对确认（SAME=字节一致），非肉眼猜测。

---

## 1. A块：AI影视团队/ 文档清单与性质

`AI影视团队/` = **v1 原型**（CrewAI + FastAPI 纯文本流水线，Kimi API）。经 Glob 全量扫描，非 venv 的文档仅 4 个 + 2 个隐藏配置：

| 路径 | 性质 | 状态 | 说明 |
|---|---|---|---|
| `AI影视团队/README.md` | 项目说明 | 当前(v1原型) | 里程碑1 创意→剧本→分镜流水线说明；技术栈 Kimi API + FastAPI + SQLite + WebSocket |
| `AI影视团队/config.yaml` | 系统配置 | 孤立/陈旧 | **v1 专属格式**（kimi-k3、server、storage、SQLite），728B，与其余两代 config.yaml 格式完全不同（见集群4） |
| `AI影视团队/requirements.txt` | 依赖清单 | 当前(v1原型) | fastapi/uvicorn/openai/pydantic/PyYAML 等 8 项 |
| `AI影视团队/static/index.html` | 前端页面 | 当前(v1原型) | 原生 HTML 前端，里程碑1 工作台骨架（idea-input / project-list / script+storyboard+json tabs） |
| `AI影视团队/.env.example` | 环境样例 | 当前 | KIMI_API_KEY 样例（非文档，仅登记） |
| `AI影视团队/.gitignore` | 忽略规则 | 当前 | v1 原型忽略规则 |
| `AI影视团队/.pytest_cache/README.md` | 缓存产物 | 噪声 | pytest 自动生成，应忽略（非人工文档） |

> 注：`AI影视团队/` 下**无任何** MEMORY.md/USER.md/AGENTS.md/README 身份文件（与集群5对比，v1 不含身份文件，属代际差异）。
> `venv/` 已按禁令完全排除，未读任何文件。

---

## 2. B块：重复/版本混乱集群映射

错误分类代号：⑨重复文档 ⑦版本混乱 ⑥命名漂移 ⑧孤立文档 ⑩过时内容
严重度：高=易引发决策/编辑归属错误；中=内容等价但结构冗余；低=纯归档噪声。

### 集群1 — 雨夜寻猫项目三重复制
| 字段 | 内容 |
|---|---|
| 类型 | ⑨重复文档 + ⑦版本混乱 |
| 副本清单 | ① `ai_film_projects/projects/雨夜寻猫/`（中间代：screenplay/shots/storyboard/audio/director_intent.md/graph.json/budget.json/k13_locked/handoffs/timeline 等）<br>② `AI影视团队v2/projects/雨夜寻猫/` 含 `00_brief/`（梗概/剧本/场景描述/角色描述 md **+ 同名 json**）、`01_spec`~`07_deliver`、`assets`、`locks`、`ditmap`、`clearance`（当前代，结构最全）<br>③ `AI影视团队v2/_legacy/projects_雨夜寻猫/`（仅二进制资产：png/mp3/flac/json，无 md） |
| 哪份最新/权威 | **② `AI影视团队v2/projects/雨夜寻猫/`**（当前代，是①的超集：共享 md 字节一致，且新增 json 版本、handoffs、locks、完整 00~07 流水线目录） |
| 哪份陈旧/可归档 | ① `ai_film_projects/projects/雨夜寻猫/`（中间代，md 内容与②的 00_brief 字节一致，已被取代）；③ `_legacy/projects_雨夜寻猫/` 是资产冻结快照，已 legacy 标注 |
| 证据 | 7 个同名 md（梗概/剧本/场景描述/角色描述/镜头清单/分镜表/音轨清单）md5 全部 SAME；仅 audio 目录在②中改名 `05_audio/` |
| 建议处理方式 | ①整体移入归档区（仅移动不删）；②为当前唯一权威线保留；③已属 _legacy 归档，保持。注意：`director_intent.md` 仅存在于①，②未携带（见下方孤立项） |
| 严重度 | 中 |

### 集群2 — 岗位卡镜像（15 岗 vs 7 当前 SKILL）
| 字段 | 内容 |
|---|---|
| 类型 | ⑨重复文档 + ⑦版本混乱 |
| 副本清单 | ① `ai_film_projects/roles/`（15 岗：animator/art_director/character_designer/cinematographer/director/editor/gaffer/producer/production_coordinator/scene_designer/screenwriter/script_supervisor/sound_engineer/storyboard_artist/vfx_artist，每岗含 01-岗位卡.md+SOUL.md 等）<br>② `AI影视团队v2/agents/_legacy_roles/`（15 岗，**字节一致**的 01-岗位卡.md 镜像）<br>③ `AI影视团队v2/agents/`（7 个当前 SKILL.md：blockout/director/previs/producer/realizer/screenwriter/script_supervisor） |
| 哪份最新/权威 | **③ `AI影视团队v2/agents/`**（当前代 7 Agent，SKILL.md 形态） |
| 哪份陈旧/可归档 | ② `_legacy_roles/` = ①的逐字镜像（已 legacy 标注）；① `ai_film_projects/roles/` 为中间代来源，被取代 |
| 证据 | 15 个岗目录整体 md5 逐一 SAME（animator 抽样 2542B 一致，全 15 岗一致） |
| 版本混乱点 | 当前代仅 7 Agent：与旧 15 岗相比，**4 岗重叠**（director/producer/screenwriter/script_supervisor，旧岗位卡 vs 新 SKILL.md 两种形态并存）；**3 岗为新增**（blockout/previs/realizer）；**8 旧岗已无当前等价**（animator/art_director/character_designer/cinematographer/editor/gaffer/production_coordinator/scene_designer/sound_engineer/storyboard_artist/vfx_artist——其中 11 个仅存于 _legacy_roles） |
| 建议处理方式 | ②保持为唯一归档镜像；①可整体移入归档；③为权威线。需明确"11 个退役岗"是否彻底退出（避免误以为仍活跃） |
| 严重度 | 中（角色体系从 15→7 的代际收缩，存在"哪套岗位卡是活的定义"混淆风险） |

### 集群3 — docs 镜像
| 字段 | 内容 |
|---|---|
| 类型 | ⑨重复文档 |
| 副本清单 | ① `ai_film_projects/docs/`（13 个 md：AI交接全息文档/_archive×5/团队架构v4.0/复刻OiiOii/好莱坞大片级/现实剧组对标v3.0/v3.0技术附录/阶段0-账号注册交接指引/阶段0体检审计v6.0）<br>② `AI影视团队v2/docs/_legacy_source/`（13 个同名 md **字节一致** + 额外 `根配置/` 子目录 + `启动脚本/`4 个 bat + `_READ_ME_FIRST.md`） |
| 哪份最新/权威 | ① `ai_film_projects/docs/` 为被复制的源；但按 `_READ_ME_FIRST.md` 明示，v2 的**唯一事实来源是 `PROJECT_STATE.md` + `spec/` + `docs/R0-*.md`**，本集群文档在 v2 中已"降级为素材" |
| 哪份陈旧/可归档 | ② `_legacy_source/` 是 R1 对①的**逐字留档**（老板硬约束：旧资产全部登记不删），已 legacy 标注，保持为单份归档 |
| 证据 | 13 个公共 md 逐一 md5 SAME（AI交接全息文档 40363B、团队架构v4.0 18608B 等均一致）；②仅多出 根配置/、启动脚本/、_READ_ME_FIRST.md |
| 建议处理方式 | ②已正确归档，勿删；①（中间代 docs）可整体移入归档。`_READ_ME_FIRST.md` 已声明"勿作 v2 事实依据"，建议保留该声明 |
| 严重度 | 高（13× 完全重复 + v3.0/v4.0 等规划已被证伪降级，编辑错副本风险大；但系老板明示的有意留档） |

### 集群4 — 根配置四份 / config.yaml 命名碰撞
| 字段 | 内容 |
|---|---|
| 类型 | ⑦版本混乱 + ⑥命名漂移 |
| 副本清单 | ① `AI影视团队/config.yaml`（728B，v1 CrewAI/FastAPI 应用配置：kimi-k3、server.host/port、storage.sqlite）<br>② `ai_film_projects/config.yaml`（814B，Hermes Profile 配置：kimi-k2.6、custom_providers、agent、plugins）<br>③ `AI影视团队v2/docs/_legacy_source/根配置/config.yaml`（814B，**与②字节一致**）<br>④ `根配置/` 子目录附带的 `MEMORY.md/USER.md/AGENTS.md/README.md/gitignore.txt`（见集群5） |
| 哪份最新/权威 | ①为 v1 专属（无同代副本）；②③同属"Hermes Profile"格式，②为源、③为镜像 |
| 哪份陈旧/可归档 | ③是②的冻结镜像；①为孤立 v1 配置，与其余格式不同 |
| 命名漂移点 | 三份**同名 `config.yaml` 但格式/用途完全不同**：①是应用服务配置，②③是 Hermes Agent Profile 配置。此外 ④中 `gitignore.txt` 与①/②根的 `.gitignore`（点前缀）命名不一致 |
| 证据 | ① md5 `60dde32…` ≠ ②③ `3d643b9…`（②③一致） |
| 建议处理方式 | 明确三份 config.yaml 的代际归属与用途差异；③随 _legacy_source 归档；①若 v1 原型不再运行可归档；避免未来再新增同名 config.yaml 造成碰撞 |
| 严重度 | 中（同名不同义，易误配；但内容已锁定无运行风险） |

### 集群5 — 知识/身份文件多份（MEMORY/USER/AGENTS/README）
| 字段 | 内容 |
|---|---|
| 类型 | ⑨重复文档 + ⑧孤立文档 |
| 副本清单 | ① `ai_film_projects/` 根：`MEMORY.md`(383B)/`USER.md`(330B)/`AGENTS.md`(4617B)/`README.md`(3897B)<br>② `AI影视团队v2/docs/_legacy_source/根配置/`：`MEMORY.md`/`USER.md`/`AGENTS.md`/`README.md`/**`gitignore.txt`**（均字节一致，仅多出 gitignore.txt）<br>③ 根目录 `D:/aifilmteam/`：`project_memory.md`(7541B)/`user_profile.md`(25B)（**独立**身份文件，不与①②同名）<br>④ `AI影视团队/` v1：**无**任何身份文件 |
| 哪份最新/权威 | ①为被复制的源（与②字节一致）；③为项目顶层独立记忆，不重复 |
| 哪份陈旧/可归档 | ② `_legacy_source/根配置/` 是①的镜像，随 _legacy 归档 |
| 孤立点 | ③ `project_memory.md`/`user_profile.md` 与①②的 `MEMORY.md`/`USER.md` 内容不同、命名不同，属**平行重复身份文件**，易混淆"哪份是活记忆" |
| 证据 | ① vs ②：MEMORY `31adcd2…`、USER `1327954…`、AGENTS `879afe6…`、README `9aa1df9…` 均 SAME |
| 建议处理方式 | ②随 _legacy 归档；①为中间代源；③需与②/①对齐或明确主从，避免双份记忆漂移 |
| 严重度 | 中 |

### 集群6 — handoff 交接文档镜像
| 字段 | 内容 |
|---|---|
| 类型 | ⑨重复文档 |
| 副本清单 | ① `ai_film_projects/logs/_handoff_A_20260927/`（11 md：A0~A8 + research_R1/R2）<br>② `AI影视团队v2/docs/_legacy_handoff/`（11 md，**字节一致**） |
| 哪份最新/权威 | ①为被复制的源 |
| 哪份陈旧/可归档 | ② `_legacy_handoff/` 是 R1 逐字留档，已 legacy 标注，保持为单份归档 |
| 证据 | 11 个文件逐一 md5 SAME（A0_探索报告 11004B 一致） |
| 建议处理方式 | ②已正确归档；①（中间代 logs）可随 ai_film_projects 整体移入归档。注意：v2 当前交接应落地于其自身 logs/，而非此 _legacy 副本 |
| 严重度 | 中 |

### 集群7 — negotiation 内 "04" 前缀冲突（与 C1 交叉）
| 字段 | 内容 |
|---|---|
| 类型 | ⑦版本混乱 + ⑥命名漂移 |
| 副本清单 | ① `negotiation/04-one-size-fits-all-audit.md`（16577B）<br>② `negotiation/04-tools-mcp.md`（35037B） |
| 哪份最新/权威（初步判断） | **② `04-tools-mcp.md` 才是真正的第四轮谈判稿**：标题明确"第四轮协商·工具与 MCP/Function Calling"，日期 2026-10-02，状态"进行中（待老板拍板）"，含 T1~T24 共 24 个决策点 |
| 哪份是误标 | ① `04-one-size-fits-all-audit.md` **实为第三轮审计产物**：正文引用"第三轮27项决策点挂起""全项目文档审计"，属 R3 审计交付物，却冠以"04"前缀 |
| 建议处理方式 | ①应重命名为 `03-one-size-fits-all-audit.md` 并归入第三轮审计件（或移入审计归档），消除"04"前缀与真第四轮稿的编号冲突；本项 C1 已专项核查，此处仅标注+初步判断 |
| 严重度 | 高（编号冲突会直接导致决策轮次归属混乱，影响 DECISIONS.md 落点） |

---

## 3. 三核心文件夹"代际"结论

| 文件夹 | 代际 | 定位 | 与本文档相关的关键事实 |
|---|---|---|---|
| `AI影视团队/` | **v1 原型** | CrewAI+FastAPI 纯文本流水线 MVP | 独立 v1 配置（config.yaml 格式独有）；无身份文件；无 projects；是三核心中最"老"的一代 |
| `ai_film_projects/` | **中间代** | Hermes Profile Agent 体系（15 岗）+ 雨夜寻猫示例项目 | 持有 docs/roles/handoffs/身份文件/MEMORY 等；其文档被 v2 的 `_legacy_source/_legacy_roles/_legacy_handoff` **逐字复制**为归档 |
| `AI影视团队v2/` | **当前代（权威线）** | 当前活跃系统：PROJECT_STATE.md 入口 + spec/ + agents/7 + projects/雨夜寻猫(00~07) + docs/R0-* | 事实来源为 `PROJECT_STATE.md`/`spec/`/`docs/R0-*`；`_legacy_*` 子目录是 R1 对中间代的冻结留档（有意、不删） |
| 根目录三.md（一.md/二.md/三.md） | 共享主设计 | 跨代共享的总体设计文档（老板主设计） | 不在三核心文件夹内，是代际之上的"主设计"，各代均引用 |
| `negotiation/` | 决策系统 | 轮次谈判稿（01~0n） | 与三核心文件夹正交的独立决策知识库；含集群7 的"04"冲突 |
| `config/`、`project_memory.md`、`user_profile.md` | 根级杂项 | 顶层配置/记忆 | 与集群5 平行身份文件相关 |

**代际链路**：v1（AI影视团队，原型）→ 中间代（ai_film_projects，15岗 Agent 体系）→ 当前代（AI影视团队v2，7 Agent + 完整流水线）。当前代的 `_legacy_*` 是对中间代（及部分 v1 资产）的**有意逐字归档**，并非运行依赖。

---

## 4. 对"文档系统重组(任务二)"与"项目结构重组(任务三)"的初步建议输入

> 仅"建议"，实际移动由后续阶段执行；**核心三文件夹只能移动不能删**，且 `_legacy_*` 已是有意留档（老板硬约束），不得删。

**A. 当前权威线（必须保留，不可动）：**
- `AI影视团队v2/` 整体为唯一活动根：`PROJECT_STATE.md`、`spec/`、`agents/`（7 SKILL.md）、`projects/雨夜寻猫/`（00~07）、`docs/R0-*.md`、`logs/`（当前交接）。
- `negotiation/04-tools-mcp.md` 为第四轮真稿，保留。

**B. 已正确归档、保持即可（勿重复造副本）：**
- `AI影视团队v2/docs/_legacy_source/`、`_legacy_roles/`、`_legacy_handoff/`、`_legacy/projects_雨夜寻猫/` 已是中间代文档/岗位/交接/资产的逐字归档，**无需再复制**。注意：因其已覆盖 ai_film_projects 的 docs/roles/handoffs 与雨夜寻猫资产，后续若把 ai_film_projects 整体移走，**不会丢失文档内容**（但代码 tools/ 未被 v2 镜像，见 C）。

**C. 可整体移入归档区（仅移动不删）：**
- `ai_film_projects/`（中间代）：其文档/岗位/交接已被 v2 `_legacy_*` 覆盖；但 `tools/`（~30 个脚本）、`roles/`、`projects/雨夜寻猫` 的**代码与运行数据 v2 未完整镜像**，移归档前需确认 v2 自有 `tools/` 已承接（04-tools-mcp.md 显示 v2 确有 tools/ 但为另一套），否则中间代 tools 仍有参考/运行价值，建议整体原样移归档而非拆分。
- `AI影视团队/`（v1 原型）：仅 v1 专用 config.yaml + 原型前端/后端，已无继承者，建议移归档；其 `static/index.html` 等可作 MVP 历史参考。

**D. 重复可合并/重命名（消除混淆）：**
- 集群7：`04-one-size-fits-all-audit.md` → 重命名为 `03-one-size-fits-all-audit.md`（归入第三轮），解除与第四轮真稿的编号冲突（高优先）。
- 集群4：三份 `config.yaml` 用途不同，建议在文件头或目录层明确标注代际/用途，避免同名误配；`gitignore.txt`(根配置) 与 `.gitignore`(根) 命名统一。
- 集群5：根目录 `project_memory.md`/`user_profile.md` 与 `MEMORY.md`/`USER.md` 内容不同，需明确"主记忆"归属，避免双份漂移。
- 集群1：`director_intent.md` 仅存于中间代，未随雨夜寻猫迁入 v2，需确认是已并入 `00_brief` 还是应补录到当前代项目。

**E. 重组时的硬约束提醒：**
- 老板 2026-09-27 硬约束"旧资产全部登记，不删"——所有 `_legacy_*` 及拟归档内容**只移不删**。
- 因 v2 的 `_legacy_*` 已逐字复制 ai_film_projects 文档，若同时把 ai_film_projects 也移入归档，会出现"两份归档"，应明确 v2 `_legacy_*` 为唯一归档副本，ai_film_projects 移走后不再另存文档副本（代码除外）。

---

### 附：校验记录（md5 SAME 清单，证明非主观判断）
- 雨夜寻猫 7 个共享 md（梗概/剧本/场景描述/角色描述/镜头清单/分镜表/音轨清单）：v1 ↔ v2 00_brief 全部 SAME
- roles 15 岗：ai_film_projects/roles ↔ v2/agents/_legacy_roles 全部 SAME
- docs 13 md：ai_film_projects/docs ↔ v2/docs/_legacy_source 全部 SAME
- 身份文件 MEMORY/USER/AGENTS/README：ai_film_projects 根 ↔ v2/根配置 全部 SAME
- handoff 11 md：ai_film_projects/logs/_handoff_A_20260927 ↔ v2/docs/_legacy_handoff 全部 SAME
- config.yaml：ai_film_projects ↔ v2/根配置 SAME（3d643b9…）；AI影视团队 v1 不同（60dde32…）
- 启动脚本 4 bat：ai_film_projects 根 ↔ v2/启动脚本 SAME
