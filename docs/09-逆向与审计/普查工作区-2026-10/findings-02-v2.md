# 普查员 #2 发现清单 · AI影视团队v2（当前代）"当前"文档

> 普查员：#2（第二普查员）｜ 范围：`D:\aifilmteam\AI影视团队v2\` 下的"当前"文档
> 方法：仅阅读+记录，**未修改/删除/移动任何源文件**。所有结论仅本文件产出。
> 阅读日期：2026-10-03｜ 覆盖式写入：`D:\aifilmteam\.audit_workspace\findings-02-v2.md`

---

## §1 文件清单（按阅读顺序）

### 1.1 根入口
1. `PROJECT_STATE.md`（v0.3，R4 in-progress）—— 已读

### 1.2 docs/ 顶层当前文档（已逐篇读取；排除 `_archive/` `_legacy_handoff/` `_legacy_source/`）
2. `docs/R0-待老板拍板清单.md` —— 已读
3. `docs/R0-旧目录归档方案.md` —— 已读（§5 归档已完成）
4. `docs/R0-旧资产登记表.md` —— 已读
5. `docs/R0-盘点报告-两个旧目录.md` —— 已读
6. `docs/R0-规划书-v2.0-待拍板.md` —— 已读（§2.1 L1/L2/L3 档位；§7 推荐 Blender MCP）
7. `docs/R0-调研证据附录.md` —— 已读（A.5 真实 ls 回显证实 196MB `.part` 残片存在）
8. `docs/R1-未定稿清单-架构与调研与需求.md` —— 已读
9. `docs/R3-架构定稿.md` —— 已读（v1.0，19条修正；§3 #9 禁用 Blender MCP；§6/§11 称 duration_s 改为 8k+1 枚举）
10. `docs/R4-执行计划.md` —— 已读（v0.1；§0 断言"196MB 残片不存在"；§六 进度未完成）
11. `docs/需求定稿.md` —— 已读（v1.1；L1/L2/L3 作为阶段：L1=5-10s 验证镜）
12. `docs/调研计划.md` —— 已读（规划文件名与实际不符）
13. `docs/写实化管线-渲染前后校验清单.md` —— 已读（v1.0，47 项）
14. `docs/调研-板块①a-写实化引擎与Blender侧.md` —— 已读
15. `docs/调研-板块①b-质检链与音频链.md` —— 已读
16. `docs/调研-板块①-验收页.md` —— 已读
17. `docs/调研-板块①-补漏-IR与judder与响度字段.md` —— 已读
18. `docs/调研-板块①-补漏与更正.md` —— 已读（§7 确认 schema duration_s 仍为自由数）
19. `docs/调研-板块②-验收页.md` —— 已读（L82 "约18条修正"）
20. `docs/调研-板块②a-商业平台竞品10家.md` —— 已读
21. `docs/调研-板块②b-开源与引擎方与获奖团队.md` —— 已读（L109 待闭合项）
22. `docs/调研-板块②c-falAPISchema核验.md` —— 已读
23. `docs/调研-板块②d-待闭合项决议.md` —— 已读（4/4 已闭合）
24. `docs/调研-参考实现-fal3D白模管线.md` —— 已读
25. `docs/调研-成本对比-渲染后端.md` —— 已读（v5）

> 共 24 篇 docs 顶层当前文档，全部已读；目录中另有 `docs/_archive/`、`docs/_legacy_handoff/`、`docs/_legacy_source/` 三个排除目录（不计入）。

### 1.3 spec/ 三契约
26. `spec/delivery_spec.json` —— 已读（L1_review_720 / L2_publish_1080 / L3_commercial 档位）
27. `spec/qc_rubric.json` —— 已读（v1.1.0，五项硬指标）
28. `spec/shot_spec.schema.json` —— 已读（`duration_s` 仅 `integer, minimum:17, maximum:481`，**无 enum**）

### 1.4 agents/ 七个当前 SKILL.md
29. `agents/director/SKILL.md` —— 已读
30. `agents/producer/SKILL.md` —— 已读
31. `agents/screenwriter/SKILL.md` —— 已读（L17：L1=30-45s / L2=60-90s）
32. `agents/previs/SKILL.md` —— 已读
33. `agents/blockout/SKILL.md` —— 已读（L34 可选 Blender MCP；L58 duration_s 一致性）
34. `agents/realizer/SKILL.md` —— 已读（L20：196,324,235 B 残片占 4.6%；L36 8k+1 帧规则）
35. `agents/script_supervisor/SKILL.md` —— 已读
> `agents/_legacy_roles/` 为排除项（旧岗，不计入）。

### 1.5 pipeline/ 当前数据（仅文档类）
36. `pipeline/audio_cues_v1.json` —— 已读（schema `cineast.audio_cues/1.0`，80s《雨夜寻猫》音频线索）
37. `pipeline/delivery_spec.json` —— 已读（**同名异 schema**：`cineast.delivery_spec/1.7`，web1080/review720 技术档）

> 排除项（按 brief）：`models/`、`wan_runtime/`、`web/`、`logs/`、`tools/`、`projects/`、`config/`（仅 `scalability_config.json` 被点名"仅记录"，未深审）、`tests/`、`assets/`、`blender/`、`_inbox/`、`_legacy/`。这些目录未纳入本次普查。

---

## §2 错误清单（12 类）

> 表头：`| 错误ID | 类型 | 所在文档(路径) | 具体位置(章节/行号) | 错误描述 | 建议处理方式 | 严重度 |`
> 严重度：P0=阻断性/需立即复核；P1=重要矛盾或一致性缺口；P2=轻微/卫生级。

### ① 内容截断
未发现明确截断实例（所有读取文档均完整收尾，无半句中断或"…"占位）。

### ② 前后矛盾
| 错误ID | 类型 | 所在文档(路径) | 具体位置 | 错误描述 | 建议处理方式 | 严重度 |
|---|---|---|---|---|---|---|
| E-C1 | 前后矛盾 | `docs/R4-执行计划.md` vs `docs/R0-调研证据附录.md` / `agents/realizer/SKILL.md` | R4 §0 L18/L28；R0-调研证据附录 A.5 L76-84；realizer/SKILL.md L20 | **"196MB VACE 残片是否存在"直接矛盾**：R4 §0 断言"三处均无…更无196MB残片""该残片不存在"；而 R0-调研证据附录 A.5 给出真实 `ls -la` 回显 `wan2.1_vace_1.3B_preview_fp16.safetensors.part`=196,324,235 B 存在，realizer SKILL 也写同一数值（4.6%）。双方均自称"实测"。 | 以一次统一 `find /d -iname '*vace*'` 全根复核为准，明确残片在/不在及所在路径，消除矛盾后再决定"补残片 vs 重新下载 4.31GB" | P0 |
| E-C2 | 前后矛盾 | `docs/R3-架构定稿.md` vs `docs/R0-规划书-v2.0-待拍板.md` / `docs/R0-调研证据附录.md` / `agents/blockout/SKILL.md` | R3 §3 第9条；R0-规划书 §7；R0-调研证据附录 B.1；blockout/SKILL.md L34 | **Blender MCP 禁用 vs 推荐矛盾**：R3 将 Blender MCP 列为禁用项；但 R0-规划书 §7 推荐 MCP（"fal 权威参考实现即 AI 通过 Blender MCP 驱动"），R0-调研证据附录 B.1 引 fal 博文逐字"driven entirely by the AI through the Blender MCP"，blockout SKILL L34 亦将 MCP 作可选参考。路线根基文献与 R3 结论相反。 | R3 需给出禁用 MCP 的具体理由（安全/可控性？），否则与权威参考实现冲突，建议改为"条件使用/默认关闭但允许" | P1 |
| E-C3 | 前后矛盾 | `PROJECT_STATE.md` | §4、§8、§6、L184 区域 | **归档状态自相矛盾**：§4/§8 将"旧目录归档"列为"⏳执行受阻/挂起项"，而 §6 写"✅归档已完成 2026-09-27 17:02"（且与 R0-旧目录归档方案 §5 确认已完成一致）。同一文件内状态冲突。 | 统一为"已完成"，将 §4/§8 的挂起标记移除或注明已闭环 | P1 |
| E-C4 | 前后矛盾 | `docs/R3-架构定稿.md` vs `spec/shot_spec.schema.json` / `docs/调研-板块①-补漏与更正.md` | R3 §6/§11；shot_spec.schema.json `duration_s`；补漏与更正 §7 | **"8k+1 枚举已落地"自述未兑现**：R3 称 `duration_s` 已改为 8k+1 枚举；但 schema 实际只有 `integer, minimum:17, maximum:481`，**无 enum 关键字**；补漏与更正 §7 也确认"schema duration_s 仍为自由数，须在 R3 改成枚举"——即 R3 自述与事实/另一文档相反。 | 在 shot_spec.schema.json 为 `duration_s` 补 `enum` 或改为 `multipleOf:8` 约束（帧数侧另建 8k+1 校验），使文档与契约一致 | P1 |

### ③ 数据不一致
| 错误ID | 类型 | 所在文档(路径) | 具体位置 | 错误描述 | 建议处理方式 | 严重度 |
|---|---|---|---|---|---|---|
| E-D1 | 数据不一致 | `docs/R4-执行计划.md` vs `spec/shot_spec.schema.json` | R4 §二 分叉C（121帧@24fps=5.04s）；shot_spec.schema.json `duration_s.minimum:17` | **最小验证镜不满足契约下限**：R4 的"最小 L1 技术验证镜"为 121 帧 = 5.04 秒，但 shot_spec `duration_s` 最小值 17（秒）。该镜若走 shot_spec 校验将直接 FAIL，R4 与契约对不上。 | 调低 `duration_s.minimum`（如 4）或明确 R4 验证镜豁免 shot_spec，并在文档注明 | P1 |
| E-D2 | 数据不一致 | `PROJECT_STATE.md` vs `docs/R3-架构定稿.md` | PROJECT_STATE L184 "18条修正"；R3 §0/§11/§14 "19条修正" | 修正条数 18 vs 19 不一致（R3 内部三处一致为 19）。 | 以 R3 枚举的 19 条为准，修正 PROJECT_STATE 计数 | P2 |
| E-D3 | 数据不一致 | `docs/调研-板块②-验收页.md` vs `docs/R3-架构定稿.md` | 板块②-验收页 L82 "约18条修正"；R3=19 | 软不一致（"约18"非精确），但与 R3 的 19 口径偏窄。 | 统一引用 R3 的 19 条精确值 | P2 |

### ④ 引用失效
未发现指向**不存在文件**的明确失效引用。注：`docs/_READ_ME_FIRST.md` 被多文档暗示为入口但不存在（见 E-I1，归⑧）；所有外链 URL 均来自旧项目/外部调研，标注为引用源而非本地失效。

### ⑤ 格式错误
| 错误ID | 类型 | 所在文档(路径) | 具体位置 | 错误描述 | 建议处理方式 | 严重度 |
|---|---|---|---|---|---|---|
| E-F1 | 格式错误 | `docs/R4-执行计划.md` | §0 "环境探针回显"表（L11-22） | **违反铁律#5（报查必带回显）**：表头写"环境探针回显"，但仅列 D:/C: 剩余空间与"现有 Wan 权重"列表，**未附"全盘搜索 *.safetensors/*vace/*.part"的真实命令与输出**，却在同表断言"三处均无…更无196MB残片"。回显缺失导致结论不可复核，且被 R0 真实回显证伪。 | 补全 find/ls 原始回显；无回显的负面结论不得写入 | P1 |

### ⑥ 命名漂移
| 错误ID | 类型 | 所在文档(路径) | 具体位置 | 错误描述 | 建议处理方式 | 严重度 |
|---|---|---|---|---|---|---|
| E-N1 | 命名漂移 | `spec/delivery_spec.json` vs `pipeline/delivery_spec.json` | 两份同名文件 | 同名不同 schema/语义：`spec/delivery_spec.json`（档位 L1_review_720/L2_publish_1080/L3_commercial）与 `pipeline/delivery_spec.json`（`cineast.delivery_spec/1.7`，web1080/review720 技术交付档：码率/响度/声道）。读者易混淆"交付档位"与"技术交付参数"两份交付规范。 | 改名其一（如 `pipeline/tech_delivery_spec.json`）或在两文件互相引用说明差异 | P2 |
| E-N2 | 命名漂移 | 多文档共用 "L1/L2/L3" | 需求定稿 / 三.md（阶段）vs delivery_spec.json / screenwriter/SKILL.md（档位） | "L1/L2/L3"两义混用（亦属②）：在交付契约与 screenwriter 中表示"交付档位（时长/分辨率）"，在需求定稿与三.md 中表示"项目阶段（验证镜/样片/平台）"。 | 统一术语：建议阶段用"阶段一/二/三"或"R4/R5/R6"，档位用"档位L1/L2/L3"，避免同符异号 | P1 |

### ⑦ 版本混乱
| 错误ID | 类型 | 所在文档(路径) | 具体位置 | 错误描述 | 建议处理方式 | 严重度 |
|---|---|---|---|---|---|---|
| E-V1 | 版本混乱 | `D:\aifilmteam\negotiation\` + `D:\aifilmteam\三.md`（交叉引用目标） | 三.md 头部"推荐目录名：AI影视团队v3"；negotiation/DECISIONS.md"# C3 立项未定细节" | **交叉引用目标实为下一代 C3/v3 立项材料**：三.md 自述"项目代号 C3（第三代）""推荐目录名 AI影视团队v3"，negotiation/DECISIONS.md 是 C3 软件系统决策（crew_bus/dispatcher/C2PA 等）。二者均非 v2 当前文档，却被 brief 指为 v2 的"negotiation C 系列决策"比对对象——把下一代决策误挂为当前代，版本归属混乱。（详见 §3/§4） | 在 audit 与 brief 层面澄清：v2 当前代的交叉引用应指向 v2 内部（调研-板块②d 的闭合项），negotiation/三.md 属独立 v3 项目，不宜直接比对 v2 spec | P1 |
| E-V2 | 版本混乱 | 多 R0/R3/R4/调研 文档 | 各自版本号 v0.1/v1.0/v1.1/v5 并存 | 跨文档无统一版本矩阵；同一"R3 架构"在 R3-架构定稿(v1.0) 与 R4 引用中版本语义不一。 | 建一份 `VERSION`/状态矩阵，标注每份文档版本与"是否已签字" | P2 |

### ⑧ 孤立文档
| 错误ID | 类型 | 所在文档(路径) | 具体位置 | 错误描述 | 建议处理方式 | 严重度 |
|---|---|---|---|---|---|---|
| E-I1 | 孤立文档 | `docs/_READ_ME_FIRST.md`（缺失） | 全库无此文件 | 无统一入口索引：多文档假定"先读入口说明"，但 `docs/_READ_ME_FIRST.md` 不存在，新接手者无阅读顺序锚点（本次阅读顺序靠 brief 指定）。 | 补 `docs/_READ_ME_FIRST.md` 作索引，列阅读顺序与范围边界 | P2 |
| E-I2 | 孤立文档 | `pipeline/delivery_spec.json`、`pipeline/audio_cues_v1.json` | pipeline/ 目录 | spec 单一事实源之外存在影子副本：`pipeline/delivery_spec.json`（同名异 schema，见 E-N1）与 `pipeline/audio_cues_v1.json`（与旧 `ai_film_projects/pipeline/audio_cues_v1.json` 重复，brief 已提示）。游离于 `spec/` 管辖。 | 明确 spec/ 为唯一契约源，pipeline/ 内副本改为引用或删除，避免漂移 | P2 |
| E-I3 | 孤立文档 | `negotiation/` + `三.md`（相对 v2） | 见 E-V1 | 作为 v2 交叉引用目标构成"伪关联"：其 C 系列决策属 v3 系统层，与 v2 影视管线 spec 不可直接对账（详见 §3）。 | 同上，隔离 v3 材料 | P2 |

### ⑨ 重复文档
| 错误ID | 类型 | 所在文档(路径) | 具体位置 | 错误描述 | 建议处理方式 | 严重度 |
|---|---|---|---|---|---|---|
| E-R1 | 重复文档 | `pipeline/audio_cues_v1.json` vs `D:\aifilmteam\ai_film_projects\pipeline\audio_cues_v1.json` | 两份同名同 schema 文件 | audio_cues_v1.json 在 v2/pipeline/ 与旧 ai_film_projects/pipeline/ 双份（brief 已点名）。需确认哪份为权威，另一份应归档或软链。 | 指定 v2/pipeline/ 为权威，旧份移入归档并标注来源 | P2 |

### ⑩ 过时内容
| 错误ID | 类型 | 所在文档(路径) | 具体位置 | 错误描述 | 建议处理方式 | 严重度 |
|---|---|---|---|---|---|---|
| E-O1 | 过时内容 | `docs/R4-执行计划.md` | §0 L18/L28 | **"残片不存在"断言已过时/错误**（以 R0-调研证据附录 A.5 真实回显为准）：R4 基于"全盘搜索无痕迹"判定残片不存在并据此决定"须下全量 4.31GB 而非补残片"；但 R0 的真实 ls 证明 `.part` 残片存在。若 R0 回显为真，则 R4 的"重新下载"决策前提失效。 | 复核真实磁盘状态后修正 R4 结论；若残片确在，改为续传 `.part` 以省 4.31GB 下载 | P1 |

### ⑪ AI 幻觉
| 错误ID | 类型 | 所在文档(路径) | 具体位置 | 错误描述 | 建议处理方式 | 严重度 |
|---|---|---|---|---|---|---|
| E-H1 | AI幻觉 | `docs/R4-执行计划.md` | §0 "环境探针回显"表 + L28 纠正段 | **无证据断言/疑似幻觉式结论**：在"环境探针回显"标题下断言"全盘搜索 *.safetensors/*vace/*.part 均无 Wan2.1-VACE 任何痕迹"，但**未提供该搜索的真实回显**（仅列 D:/C: 空间与现有 Wan 权重列表），且该负面结论被 R0-调研证据附录 的真实 ls 回显直接证伪。属"声称已查实则无回显"的疑似幻觉，且自评违反铁律#5。 | 删除无回显的负面断言，补真实 find 输出；以实际磁盘为准重写 §0 | P1 |

### ⑫ 未完成项
| 错误ID | 类型 | 所在文档(路径) | 具体位置 | 错误描述 | 建议处理方式 | 严重度 |
|---|---|---|---|---|---|---|
| E-U1 | 未完成 | `docs/R0-待老板拍板清单.md`、`docs/R0-规划书-v2.0-待拍板.md` | 全文标"待拍板" | 仍有多项待老板拍板未决（规划书与清单本身即"待拍板"状态）。 | 跟踪至拍板后转 R 文档 | P2 |
| E-U2 | 未完成 | `docs/调研-板块②b-开源与引擎方与获奖团队.md` | L109 待老板拍/待闭合 | 三项未闭合：① LTX-2.3 许可原文确认；② fal 3DREAL LoRA 商用条款（E-08）；③ 本机 12GB 下本地路径锁定 Wan2.1-VACE-1.3B。 | 向 Lightricks 取许可原文、闭合 E-08 LoRA 条款 | P2 |
| E-U3 | 未完成 | `PROJECT_STATE.md` + `docs/R4-执行计划.md` | PROJECT_STATE 标 R4 in-progress；R4 §六 进度 [~] | R4 技术验证镜本身未完成：权重下载/代码克隆/白模渲染仍进行中，VACE loader 与写实化+QC 未做。 | 续跑 R4 并出验证报告 | P2 |
| E-U4 | 未完成（正面/已闭合） | `docs/调研-板块②d-待闭合项决议.md` | 全文 | 4/4 已闭合：fal Commercial 可用 / LTX-2 Community License / 锁定 Wan VACE / 音频独立链。属已决，非错误，仅作汇总标注。 | 维持闭合状态 | P2 |

---

## §3 引用关系

### 3.1 文档间交叉引用
- **R 系列主线**：R0（规划书/归档/资产/盘点/拍板清单/调研证据附录）→ R1（未定稿清单）→ R3（架构定稿，19条修正）→ R4（执行计划）。R3 是被 R4 引用的签字基线；R4 §五 三个分叉（A1/B1/C）已由老板 18:25 拍板，故 R4 的"待拍板分叉"已闭环（但 R4 验证镜执行未完，见 E-U3）。
- **调研板块**：板块①（a 引擎/b 质检音频/验收页/补漏IR/补漏更正）+ 板块②（验收页/a 竞品/b 开源引擎获奖/c fal Schema/d 闭合项）+ 参考实现 + 成本对比。板块②d 是板块①/② 调研的"决策收口"，4/4 闭合。
- **spec 契约被引用处**：`shot_spec.schema.json` 被 previs/blockout/screenwriter/realizer 的 SKILL 显式引用为"只读校验"；`delivery_spec.json` 被 producer/script_supervisor 引用为验收依据；`qc_rubric.json` 被 script_supervisor 引用为五项硬指标唯一判据。引用关系自洽（SKILL→spec 单向）。
- **audio_cues_v1.json**：仅 `pipeline/` 内被剧本/音频链消费；与旧 `ai_film_projects/pipeline/` 副本重复（E-R1）。

### 3.2 spec 三契约一致性
- `delivery_spec.json`（档位 L1/L2/L3）、`qc_rubric.json`（五项硬指标）、`shot_spec.schema.json`（镜头契约）三者**内部各自自洽**，且 SKILL 引用方向一致。
- **契约内部缺口（一致性缺口，非彼此矛盾）**：
  - `shot_spec.schema.json.duration_s` 缺 8k+1 枚举（E-C4），与 R3 自述不符；
  - `shot_spec.schema.json.duration_s.minimum:17` 与 R4 的 5 秒验证镜冲突（E-D1）；
  - 两处 `delivery_spec.json` 同名异义（E-N1）。
- 三项缺口均指向"R3 架构定稿中声称已落地的契约约束，未在实际 schema 中兑现"，建议作为 R3→spec 的闭环补漏。

### 3.3 "negotiation C 系列"与本 spec 的比对（重要更正）
- **brief 预设**：spec 三契约应与 `negotiation/` 的"C 系列决策"一致。
- **实际核查**：`negotiation/DECISIONS.md` 为 **C3（三代）软件系统立项决策**（标题"# C3 立项未定细节·决策记录"），其 C-1~C-5 冲突是关于 crew_bus 并发/崩溃契约、dispatcher 单实例、C2PA 等**系统层**议题，**与 v2 影视管线 spec（8k+1/L1-L3 档位/五项硬指标）无对应关系**。`三.md` 同为 C3/v3 立项方案（自述"推荐目录名 AI影视团队v3"）。
- **结论**：v2 当前代的"影视管线 C 系列决策"实际位于 `docs/调研-板块②d-待闭合项决议.md`（fal Commercial / LTX-2 Community / 锁定 Wan VACE / 音频独立链，4/4 闭合）。该闭合项与 v2 spec **一致**：fal 3DREAL 选为云主力 ↔ realizer SKILL R1；Wan VACE-1.3B 锁本地零成本 ↔ realizer SKILL 暂缓项；音频独立链 ↔ audio_cues_v1.json + qc_rubric 声音硬指标。
- **因此 brief 要求的"spec 与 negotiation C 系列一致性"在字面目标上无法成立**——二者分属不同项目（v2 影视 vs v3 系统），应在 audit 层面修正比对对象。详见 §4。

---

## §4 范围小结

### 4.1 性质 / 状态 / 来源 / 日期分布
- **性质**：v2 为"当前代"AI 影视制片厂文档集，含 1 份根状态 + 24 份 docs + 3 份 spec 契约 + 7 份 agent SKILL + 2 份 pipeline 文档（audio_cues_v1.json、delivery_spec.json）。全部为 Markdown / JSON，无代码审计。
- **状态**：R0~R3 多为已签字/已归档；R4 执行中（in-progress）；调研板块②d 已闭合；仍有 R0-待拍板清单、R0-规划书、板块②b L109 三项待闭合未决。
- **来源**：多数文档由 team-lead 编制（2026-09-27），调研板块由 comp-* 调研员编制，agent SKILL 为岗位卡。
- **日期分布**：docs/PROJECT_STATE 标注 2026-09-27；R0-调研证据附录 A.5 实测 2026-09-26；三.md（v3）2026-09-29/10-02；negotiation/ 2026-10-02~03。v2 当前文档集中于 2026-09-26~27，晚于其的交叉引用目标（negotiation/三.md）属 v3 时间线。

### 4.2 矛盾 / 重复 / 截断 / 幻觉 汇总
- **矛盾（②）4 项**：E-C1（196MB 残片存在与否，P0）、E-C2（Blender MCP 禁用vs推荐，P1）、E-C3（归档状态自相矛盾，P1）、E-C4（8k+1 枚举自述未兑现，P1）。
- **数据不一致（③）3 项**：E-D1（5秒验证镜 vs schema 下限17s，P1）、E-D2（18 vs 19 修正，P2）、E-D3（约18 vs 19，P2）。
- **格式错误（⑤）1 项**：E-F1（R4 §0 缺 find 回显却断言，P1）。
- **命名漂移（⑥）2 项**：E-N1（两份 delivery_spec.json 同名异 schema，P2）、E-N2（L1/L2/L3 两义，P1）。
- **版本混乱（⑦）2 项**：E-V1（negotiation/三.md 实为 v3，P1）、E-V2（无统一版本矩阵，P2）。
- **孤立文档（⑧）3 项**：E-I1（缺入口，P2）、E-I2（pipeline 影子副本，P2）、E-I3（v3 伪关联，P2）。
- **重复文档（⑨）1 项**：E-R1（audio_cues_v1.json 双份，P2）。
- **过时内容（⑩）1 项**：E-O1（R4"残片不存在"断言，P1）。
- **AI 幻觉（⑪）1 项**：E-H1（R4 无回显负面断言，P1）。
- **未完成（⑫）4 项**：E-U1~E-U4（含 1 项正面已闭合）。
- **截断（①）**：未发现明确截断实例。
- **引用失效（④）**：未发现指向不存在文件的失效引用。

### 4.3 spec 三契约与 negotiation C 系列是否一致
- **字面比对不成立**：`negotiation/` + `三.md` 属 **C3/v3 下一代立项项目**，其 C 系列（C-1~C-5）为系统层决策，与 v2 spec 无对应关系；故"v2 spec 与 negotiation C 系列一致"这一命题在对象层面错位（详见 §3.3、E-V1）。
- **实际可比对象**：v2 影视管线决策收口在 `调研-板块②d`（4/4 闭合），其结论与 v2 spec **一致**（fal 云主力、Wan VACE 本地、音频独立链均被 spec/SKILL 采纳）。
- **spec 内部一致性缺口**（需 R3→spec 闭环）：`duration_s` 缺 8k+1 枚举（E-C4）、`duration_s.minimum:17` 与 R4 5秒镜冲突（E-D1）、两份 `delivery_spec.json` 同名异义（E-N1）。这些是被 R3 声称已落地但未在契约中兑现的缺口，建议在下一轮 R 文档中补丁。

---

## §5 摘要给主理人（≤150 字）

范围内 24 篇 docs + 3 spec + 7 SKILL + 2 pipeline 文档已全部读取，未改任何源文件。

**待拍板未决**：有——R0-待拍板清单/规划书仍挂起；板块②b L109 三项（LTX-2.3 许可原文、fal LoRA 商用 E-08、12GB 锁 VACE）未闭合；R4 验证镜执行未完。

**spec 与 negotiation C 系列一致性**：对象错位——negotiation/与三.md 实为下一代 C3/v3 立项材料，其 C 系列是系统层决策，与 v2 影视 spec 不可直接对账；v2 真实管线决策（板块②d 4/4 闭合）与 spec 一致。

**截断/幻觉**：无明确截断；但 R4 §0 在无 find 回显下断言"196MB VACE 残片不存在"，被 R0-调研证据附录 真实 ls 回显证伪（疑似幻觉/P0 矛盾），需一次统一全根复核定夺。
