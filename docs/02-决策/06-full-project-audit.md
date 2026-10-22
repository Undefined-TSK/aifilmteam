# 06 · 全项目文档普查报告

> 主理人整合 · 普查执行：4 名普查员并行（只读）+ md5 字节级核验
> 普查日期：2026-10-03
> 配套详细证据：`D:\aifilmteam\docs\09-逆向与审计\普查工作区-2026-10\findings-01-neg-root.md`（根+谈判）、`findings-02-v2.md`（v2 当前代）、`findings-03-afp.md`（中间代）、`findings-04-legacy-dupes.md`（旧代+跨代映射）
> 本文件为**总览与去重合并的错误总表**；逐文档全表与原始证据见上述 4 份 findings。

---

## 0. 摘要（一眼结论）

1. **项目实际是"三代累加"而非一个项目**：`AI影视团队/`（v1 原型）→ `ai_film_projects/`（中间代，15 岗 Agent 体系）→ `AI影视团队v2/`（当前代，7 Agent + 完整流水线）。`三.md` 与 `negotiation/` 属于**下一代 C3/v3 立项材料**，不在当前三代之内。
2. **重复/版本混乱严重但"已部分有意归档"**：当前代 v2 的 `docs/_legacy_source/`、`agents/_legacy_roles/`、`docs/_legacy_handoff/`、`_legacy/projects_雨夜寻猫/` 是对中间代文档/岗位/交接/资产的**逐字冻结留档**（md5 SAME 核验）。雨夜寻猫项目在三处成"三重复制"。
3. **P0 级实质矛盾集中在"文档已拍板/已写 vs 现实未落地/已过时"**：196MB VACE 残片 R4 断言"不存在"被 R0 真实回显证伪；好莱坞手册交付数值与 `delivery_spec.json` 双口径；中间代根 4 配置（Hermes+飞书+9 岗+SDXL）全过时；雨夜寻猫时间轴 0 签核/647 阻断错；云引擎 Key 从未注册。
4. **命名/编号碰撞会误导决策归属**：两个"04"（真第四轮=`04-tools-mcp.md`；审计件应改名 `03-one-size-fits-all-audit.md`）、两个"05"、P1 报告前缀。
5. **AI 幻觉已发现并已纠正**：`05-global-review-reflection.md` 前版编造 A10/A12/D1/D2 等不存在决策点（已逐行纠正为真实 27 项）；中间代旧手册残留 Wan3.0/H3 33B/Seedance 开源等，已被 v6.0 审计指正但手册未同步。
6. **核心纪律红线**：三个核心文件夹**只能整体移动归档、绝不删除**；v2 `_legacy_*` 是有意留档，亦不删。

---

## 1. 普查范围与方法

- **纳入**：`三.md`、`AI影视项目-三版本逆向分析报告.html`、`negotiation/*`（23）、`AI影视团队v2/` 当前文档（排除 `_legacy_*`/venv/models/wan_runtime/web/projects 运行数据）、`ai_film_projects/` 文档（排除 venv/测试证据 json/项目运行 json/comfyui json/web/logs 运行时）、`AI影视团队/` 文档（**完全排除 venv/**）。
- **排除（第三方噪声，绝不读）**：`venv/`、`node_modules/`、`models/`、`wan_runtime/pylibs/`、`*.dist-info/`、`sboms/`、`dist/`、`.pytest_cache/`。
- **方法**：4 名普查员按预置清单并行只读；跨代重复结论**全部经 md5 逐字节比对**（SAME=字节一致），非肉眼猜测。
- **分层读法**：岗位卡/项目数据等大量同构文件采用"全登记 + 代表样本精读"，避免 270 份近重复模板的无效重读，同时不漏重复/截断/幻觉类错误。

---

## 2. 项目文档总览（代际 + 数量）

| 代际 | 文件夹 | 定位 | 实质性文档量（普查口径） |
|---|---|---|---|
| v1 原型 | `AI影视团队/` | CrewAI+FastAPI 纯文本 MVP（Kimi API） | 4（README/config.yaml/requirements.txt/static/index.html）+ 2 隐藏配置；**无身份文件** |
| 中间代 | `ai_film_projects/` | Hermes Profile Agent 体系（15 岗）+ 雨夜寻猫项目 | docs 13、roles 15 岗、course 全套、skills 1、pipeline 2、根配置 4、handoff 11、projects 雨夜寻猫全套 |
| **当前代（权威线）** | `AI影视团队v2/` | 当前活跃系统：PROJECT_STATE + spec + agents(7) + projects/雨夜寻猫(00~07) + docs/R0~R4 | docs 24 当前、spec 3、agents 7、pipeline 2、PROJECT_STATE 1 |
| 共享主设计 | 根 `三.md` + `一/二.md` | 跨代总体设计（老板主设计） | 1（124KB）+ 逆向报告 1（html） |
| 决策系统 | `negotiation/` | 轮次谈判稿 01~15 + DECISIONS 事实源 | 23 |
| 根级杂项 | `config/`、`project_memory.md`、`user_profile.md` | 顶层配置/平行记忆 | 与身份文件集群相关 |

**代际链路**：v1 → 中间代 → 当前代（v2）。当前代 `_legacy_*` = 对中间代（及部分 v1 资产）的有意逐字归档，非运行依赖。

---

## 3. 跨代重复 / 版本混乱诊断（7 大集群，md5 核验）

| 集群 | 类型 | 副本 | 权威/最新 | 可归档/陈旧 | 严重度 |
|---|---|---|---|---|---|
| 1 雨夜寻猫三重复制 | 重复+版本 | `ai_film_projects/projects/雨夜寻猫/` ↔ `AI影视团队v2/projects/雨夜寻猫/`（含 00_brief） ↔ `AI影视团队v2/_legacy/projects_雨夜寻猫/` | **v2 当前代**（①的超集，共享 md 字节一致，新增 json/handoffs/locks/00~07） | ①整体移归档；③已 legacy | 中 |
| 2 岗位卡镜像 | 重复+版本 | `ai_film_projects/roles/`(15) ↔ `AI影视团队v2/agents/_legacy_roles/`(15, SAME) ↔ `AI影视团队v2/agents/`(7 当前) | **v2 当前 7 Agent** | ②保持唯一归档；①整体移归档 | 中（15→7 代际收缩混淆） |
| 3 docs 镜像 | 重复 | `ai_film_projects/docs/`(13) ↔ `AI影视团队v2/docs/_legacy_source/`(13, SAME) | ①为源；v2 事实源是 PROJECT_STATE/spec/R0-* | ②已正确归档；①移归档 | 高（13×全重复，但有意为留档） |
| 4 config 四份 | 版本+命名 | 3 份同名 `config.yaml`（v1 应用配置 / 中间代 Hermes Profile / v2 镜像）+ `gitignore.txt` vs `.gitignore` | v1 独属；②③同格式（②③ SAME） | ③随 legacy；①可归档 | 中（同名不同义易误配） |
| 5 身份文件多份 | 重复+孤立 | `ai_film_projects/` 根 MEMORY/USER/AGENTS/README ↔ `AI影视团队v2/docs/_legacy_source/根配置/`（SAME）；根 `project_memory.md`/`user_profile.md` 平行独立 | ①为源；③平行独立 | ②随 legacy；③需对齐 | 中 |
| 6 handoff 镜像 | 重复 | `ai_film_projects/logs/_handoff_A_20260927/`(11) ↔ `AI影视团队v2/docs/_legacy_handoff/`(11, SAME) | ①为源 | ②已归档；①随 ai_film_projects 移归档 | 中 |
| 7 negotiation "04" 冲突 | 版本+命名 | `04-one-size-fits-all-audit.md`(实为第三轮审计件) ↔ `04-tools-mcp.md`(真第四轮 T1~T24) | **`04-tools-mcp.md`=真第四轮** | 审计件应改名 `03-one-size-fits-all-audit.md` | 高（轮次归属混乱） |

> 集群 1~6 的全部"重复"均经 md5 逐字节 SAME 确认；v2 `_legacy_*` 已覆盖中间代文档/岗位/交接，故把 `ai_film_projects` 整体移归档**不会丢失文档内容**（但其 `tools/` 代码 v2 未镜像，须确认 v2 自有 tools 已承接）。

---

## 4. 错误总表（12 类 · 去重合并 · 含严重度）

> 严重度：🔴P0 阻断/易致决策错误  🟠P1 重要矛盾/一致性缺口  🟡P2 轻微/卫生
> 完整逐文档证据与位置见 4 份 findings 文件；此处为合并索引。

### 4.1 🔴 P0（优先处置）
| ID | 类别 | 位置 | 描述 |
|---|---|---|---|
| AU-C3 | ②矛盾 | `AI影视团队v2/docs/R4-执行计划.md` vs `R0-调研证据附录.md` | 196MB VACE `.part` 残片：R4 断言"不存在"，R0 真实 `ls` 回显证明存在（双方均称实测）→ 须一次全根 `find` 复核定夺 |
| AU-C10 | ②矛盾 | `ai_film_projects/docs/好莱坞大片级对标…执行手册.md` §6.1 vs `pipeline/delivery_spec.json` | 交付数值双口径（-18~24 LUFS/1080p30fps/8-15Mbps vs -14 LUFS/24fps/48kHz）→ 手册加注"以 delivery_spec.json 为准" |
| AU-D4 | ③不一致 | `ai_film_projects/docs/*` + `pipeline/delivery_spec.json` | 岗位数三层口径分裂：文档 19 / roles 目录 15 / 运行 bot 9 → 全仓统一口径 |
| AU-H3 | ⑪幻觉 | `ai_film_projects/docs/旧文档`（手册/技术附录） | Wan3.0（实为 wan2.6/2.7）、H3 33B（非 138B）、Seedance 开源（假）、-18~24 LUFS（实为 -14）、FLUX dev 非商用红灯 → v6.0 已指正但手册未同步 |
| AU-U2 | ⑩过时 | `ai_film_projects/` 根 AGENTS/MEMORY/USER/config.yaml/README | 停留在 Hermes+飞书+9 岗+SDXL 时代，与 09-26 新路线全面冲突 |
| AU-U5 | ⑫未完成 | `ai_film_projects/projects/雨夜寻猫/timeline` | 19 轨契约 0 条 owner 签核、647 条 blocking_errs，时间轴空壳 → 启动逐轨签核 |
| AU-U6 | ⑫未完成 | `ai_film_projects/` 全仓 | 两云引擎 Key 未到，真实调用 0 处，全片仍 88.9% 静图 → 注册后写 .env 最小验证 |

### 4.2 🟠 P1
| ID | 类别 | 位置 | 描述 |
|---|---|---|---|
| AU-C4 | ②矛盾 | `R3-架构定稿.md` vs `R0-规划书`/`R0-调研证据附录`/`blockout/SKILL` | Blender MCP：R3 禁用，但 R0 规划书推荐（引 fal 博文"driven by Blender MCP"）→ 须给禁用理由或改"条件使用" |
| AU-C5 | ②矛盾 | `AI影视团队v2/PROJECT_STATE.md` | 归档状态自相矛盾（§4/§8 挂起 vs §6 "✅已完成 09-27"） |
| AU-C6 | ②矛盾 | `R3-架构定稿.md` vs `spec/shot_spec.schema.json` | 声称 `duration_s` 已改 8k+1 枚举，但 schema 仅 `integer 17~481` 无 enum → 补 enum/multipleOf |
| AU-C7 | ②矛盾 | `ai_film_projects/AGENTS.md` | 称"9 Profile/6 专业岗"却列 7 个岗名（数量自相矛盾） |
| AU-C8 | ②矛盾 | `ai_film_projects/roles/producer/` SOUL vs 01-岗位卡/02-工作流/04-Profile | 同岗代际分裂（SOUL 写 v5.0 九 Agent 协调；另三件写 MVP 单 Agent） |
| AU-C9 | ②矛盾 | `ai_film_projects/roles/sound_engineer/` SOUL vs 01-岗位卡 | 工具链冲突（SOUL 写 ChatTTS/Suno/MusicGen+Whisper 字幕；岗位卡写 edge-tts/CC0） |
| AU-C11 | ②矛盾 | `好莱坞大片级…执行手册.md` 标题 | "全阶段零返工" 与 v6.0 审计"零返工不实现"矛盾 → 对外措辞改"废片率可测+不降级交付" |
| AU-C12 | ②矛盾 | `negotiation/08/09/10-*.md` §1.5 | 系统性"v2 代码未落地 vs 文档已拍板"：各 9 项代码↔文档冲突 |
| AU-D1 | ③不一致 | `R4-执行计划.md` vs `spec/shot_spec.schema.json` | 最小 L1 验证镜 5.04s 但 `duration_s.minimum:17` → 调低下限或豁免 |
| AU-D3 | ③不一致 | `ai_film_projects/MEMORY.md` | "小雪三视图" 实为项目角色"小白"（白猫） |
| AU-D5 | ③不一致 | `ai_film_projects/AGENTS.md` | 资产路径写 `C:\Users\LZH\ai_film_projects\`，实为 `D:\aifilmteam\ai_film_projects\` |
| AU-F1 | ⑤格式 | `R4-执行计划.md` §0 | 违铁律#5：标"环境探针回显"却无 `find` 原始回显，仅列空间+权重列表即断言"无残片" |
| AU-H2 | ⑪幻觉 | `R4-执行计划.md` §0 | 无回显负面断言（疑似幻觉），被 R0 真实回显证伪 |
| AU-N1 | ⑥命名 | 多文档共用 `L1/L2/L3` | 两义混用：交付档位（时长/分辨率）vs 项目阶段（验证镜/样片/平台） |
| AU-R3 | ④失效 | `negotiation/DECISIONS.md` 多轮 | 回链行号 off-by-one（G1:317→284、U7:451→432、PK5:397→396、O1:478→477、A25:168→167）→ **已 grep 核准纠正并登记** |
| AU-U3 | ⑩过时 | `ai_film_projects/docs/v3.0技术附录` | ComfyUI 写 0.33.1（实测 0.37.2）；提 Wan3.0（实际 2.6/2.7） |
| AU-U4 | ⑫未完成 | `ai_film_projects/roles/` 6 空骨架岗 | director 等原空骨架，A8 仅补 01-岗位卡，02-05 仍缺 |
| AU-U7 | ⑫未完成 | `ai_film_projects/logs/_mem_mirror/` + C 盘真记忆 | 15 条待回写记忆 + 1 处待替换词未回写，记忆双轨已分歧 |
| AU-G1 | ⑦版本 | `negotiation/`+`三.md` vs `AI影视团队v2/` | 误将下一代 C3/v3 立项材料当 v2 交叉引用对象（见 §3 更正） |
| AU-NAM1 | ⑥命名 | `negotiation/04-*` 两文件 | 两"04"前缀碰撞（集群 7）→ 审计件改名 `03-one-size-fits-all-audit.md` |
| AU-NAM2 | ⑥命名 | `negotiation/05-*` 两文件 | 两"05"前缀（真第五轮 `05-contract-data-model.md` vs 反思 `05-global-review-reflection.md`）→ 反思件改名 |

### 4.3 🟡 P2 / 低 / 已纠正（不阻塞，登记备查）
| ID | 类别 | 位置 | 描述 |
|---|---|---|---|
| AU-C1/C2 | ②矛盾 | `negotiation/06/07` 文档头 | 状态滞后（"待老板拍板"/"第一阶段起草中"）— 随 2026-10-03 采纳新规更新 |
| AU-D2 | ③不一致 | `PROJECT_STATE.md` vs `R3` | 修正条数 18 vs 19（以 R3 的 19 为准） |
| AU-N2 | ⑥命名 | `spec/delivery_spec.json` vs `pipeline/delivery_spec.json` | 同名异 schema（交付档位 vs 技术交付参数）→ 改名其一 |
| AU-R1 | ④失效 | `course/methodology/README.md` | 引 `profiles/`、`handoffs/`，实为 `roles/`、根无 handoffs |
| AU-R2 | ④失效 | `course/关卡6-交付自检清单.md` | 引 `tests/case1_*`、`run_case*.py`，case 目录已缺失 |
| AU-U8 | ⑫未完成 | `AI影视团队v2/docs/R0-待拍板清单`/`R0-规划书`/`板块②b L109` | 多项仍待拍板/未闭合（LTX-2.3 许可、fal LoRA 商用、12GB 锁 VACE） |
| AU-T1 | ①截断 | `negotiation/DECISIONS.md` 末节 | "收官·占位"残留文本（第十五轮已填后未清除） |
| AU-H1 | ⑪幻觉(已纠正) | `negotiation/05-global-review-reflection.md` | 前版编造 A10/A12/D1/D2 等 → 已逐行纠正为真实 27 项，作反面案例留存 |
| AU-NAM3 | ⑥命名 | `negotiation/P1-five-point-upgrade-report.md` | "P1"前缀与第八轮 PK/P 系列易混 → 明确为升级报告性质 |
| AU-DUP3/5/6 | ⑨重复 | 集群 3/5/6 | docs/身份/handoff 中间代 ↔ v2 `_legacy_*` 全重复（已正确归档） |
| AU-V2 | ⑦版本 | `AI影视团队v2` 多 R0/R3/R4 文档 | 无统一版本矩阵（v0.1/v1.0/v1.1/v5 并存） |
| AU-I1 | ⑧孤立 | `AI影视团队v2/docs/` | 缺统一入口 `_READ_ME_FIRST.md`（多文档假定其存在却无） |
| AU-O1 | ⑩过时 | `R4-执行计划.md` | "残片不存在"断言已过时/错误（见 AU-C3） |
| AU-13/14/15 | ⑨重复 | 中间代 | 全息文档 vs SOUL 重复；中间代 docs 镜像进 v2（单向） |
| AU-12 | ⑫未完成 | `negotiation/DECISIONS.md` 12~15 轮 R0 前置 | A15/A13/A24/A26/A5/crew_bus 未落地，阻塞 R0 项（诚实标 pending） |
| AU-30/34 | ⑪/⑫ | `negotiation/13/14/15-*.md` | 13/14/15 轮主理人代笔，未经独立 worker 交叉验证；R0 复核时补查 |

---

## 5. 各范围关键发现（指向详细 findings）

- **根+谈判（findings-01）**：三.md 引用总体成立有效；15 轮全 ✅ 收敛；两个"04/05"归属已定；唯一高危幻觉已自我纠正；系统性风险是"代码未落地 vs 文档已拍板"（诚实标 pending）。
- **v2 当前代（findings-02）**：24 docs + 3 spec + 7 SKILL + 2 pipeline 全读；P0 矛盾 AU-C3（VACE 残片）；spec 三契约内部自洽但 R3 声称已落地的约束未在 schema 兑现；**关键更正**：negotiation/三.md 属 v3，不与 v2 spec 直接对账。
- **中间代（findings-03）**：信息密度高、调研扎实（R1/R2 一手引用规范）；但文档债严重——根 4 配置与 5 份 _archive 全过时；手册残留幻觉与双交付口径；岗位数三层口径分裂；15 条记忆与 §13 十项落地待拍板。
- **旧代+跨代（findings-04）**：v1→中间代→v2 链路确认；7 大重复集群全部 md5 核验；v2 `_legacy_*` 为有意逐字归档（只移不删）；建议 04 审计件改名归入第三轮。

---

## 6. 结论与下一步

- **文档系统现状（任务二诊断）**：三代累加 + 大量已归档镜像 + 命名碰撞；当前权威线 = `AI影视团队v2/`（PROJECT_STATE/spec/R0~R4/agents/projects），中间代文档已被 v2 `_legacy_*` 覆盖。
- **项目结构现状（任务三诊断）**：三个核心文件夹只能移动归档不能删；v2 为当前活动根；中间代代码（tools/）v2 未完整镜像，移归档前须确认承接。
- **决策现状（任务四诊断）**：15 轮决策已全部收敛采纳，但存在 P0 级"文档↔现实"落差（AU-C3/AU-C10/AU-D4/AU-H3/AU-U2/AU-U5/AU-U6）与命名碰撞（AU-NAM1/2），需团队复核裁定。
- **下一步（按用户既定顺序）**：
  1. **任务二** → `07-document-reorganization-plan.md`（新文档树 + 旧→新映射 + 管理方案）
  2. **任务三** → `08-project-restructure-plan.md`（新项目树 + 迁移映射 + 清理清单）
  3. **任务四** → `09-decision-review-report.md`（六维度 + 反一刀切复审）
  4. **任务五** → `10-team-collaboration-log.md`（团队协商/投票/定论记录）
  5. **任务六** → `11-development-readiness-report.md`（准备度检查 ✅/⚠️/❌）

> 本普查**零删除、零移动**：所有源文件保持原状，仅新增 4 份 findings + 本 06 报告于 `negotiation/` 与 `.audit_workspace/`。实际重组动作待 07/08 方案经团队裁定后执行。
