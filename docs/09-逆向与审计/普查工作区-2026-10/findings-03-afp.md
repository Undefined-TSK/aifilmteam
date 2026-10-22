# 普查发现 — ai_film_projects（中间代）

> 普查员：第三名普查员（只读）
> 范围：`D:\aifilmteam\ai_film_projects\` 下文档（严格排除 venv/、node_modules/、tests 证据 json、projects 运行 json、comfyui json、web/、logs 运行时产物，仅 logs/_handoff_A_20260927/ 下 .md 与 logs/_mem_mirror/ 纳入）
> 约束：严禁修改/删除/移动任何源文件；所有发现仅记录于此文件。
> 阅读日期：2026-10-03

---

## 1. 文件清单（按阅读顺序；roles/ 与 projects/ 用"已精读/仅登记"标注）

### 1.1 根目录 4 配置文件（已精读）
| 顺序 | 路径 | 状态 | 备注 |
|---|---|---|---|
| 1 | `AGENTS.md` | 已精读 | 08-22；称"9 个 Profile / 6 个专业岗"却列 7 岗名；资产路径写 `C:\Users\LZH\ai_film_projects\`；引用 `vram_scheduler.py` 插件（tools 内 0 引用） |
| 2 | `MEMORY.md` | 已精读 | 08-17；停"剧本阶段"；写"角色设计师出小雪三视图"（实际角色为"小白"） |
| 3 | `USER.md` | 已精读 | 08-17；老板偏好冷蓝灰/王家卫/新海诚（与项目一致）；内存写 16GB（实测约 15GB） |
| 4 | `README.md` | 已精读 | 08-22；描述旧结构（roles 仅 9 岗、course 标"归档"），与现状不符 |
| — | `config.yaml` | 已精读 | 08-22；Hermes 配置，Kimi K2.6，9 Profile 共用；`plugins.enabled: []` 与实际不符 |

### 1.2 docs/ 当前 8 篇（全部已精读）
| 顺序 | 路径 | 备注 |
|---|---|---|
| 5 | `docs/复刻OiiOii-技术选型与功能对标规划.md` | v1.1；提"9 角色与 OiiOii 7 Agent 同构"（后文档升级 18/19 岗） |
| 6 | `docs/团队架构v4.0-18岗位定稿与Agent技术栈升级方案.md` | 14→18 岗；标题"18 岗位"实为 19 |
| 7 | `docs/现实剧组对标v3.0总体规划.md` | 13→14 岗再引 v4.0 的 18 岗（混排） |
| 8 | `docs/好莱坞大片级对标与全阶段零返工执行手册.md` | v5.0；新增导演岗→19 岗，称"零返工冻结"；§6.1 交付六档与 delivery_spec 冲突 |
| 9 | `docs/AI交接全息文档.md` | 中枢交接件；自陈"19 岗中 15 个已建文件夹+SOUL.md（缺 composer/costume/props/colorist）" |
| 10 | `docs/v3.0技术附录-部署与接入手册.md` | 提 Wan3.0 等（后被 v6.0 纠正）；硬件行写 ComfyUI 0.33.1（实为 0.37.2） |
| 11 | `docs/阶段0-账号注册交接指引.md` | 老板手动注册云 API 指引 |
| 12 | `docs/阶段0体检审计报告与规划修订v6.0.md` | **关键纠偏件**；明确"现在做不出好莱坞级成片"，列 15 条假设纠正（A1-A18）+ 实测证据 E1-E15 |

### 1.3 docs/_archive/ 5 篇（仅登记路径，未读正文；判定为归档过时）
| 顺序 | 路径 | 判定 |
|---|---|---|
| 13 | `docs/_archive/AI影视团队工作平台方案.md` | 08-22 旧平台方案；写"ComfyUI 本体未装"、飞书 9 bot（已过时） |
| 14 | `docs/_archive/AI影视团队工作平台方案-优化意见.md` | 08-22；指向飞书版 MVP（已过时） |
| 15 | `docs/_archive/使用说明书.md` | 08-22；"AI 生成引擎：ComfyUI + SDXL"（旧路线） |
| 16 | `docs/_archive/project_memory.md` | 08-22 旧记忆（"模型 SDXL 1.0"、"9 Agent"） |
| 17 | `docs/_archive/团队架构重组v2.0与全岗位技术配置方案.md` | 09-26 被 v4.0 取代（9→13 岗口径） |

### 1.4 course/（全部已精读）
| 顺序 | 路径 | 备注 |
|---|---|---|
| 18 | `course/methodology/SKILL.md` | 6 模块 A-F 封装方法论 |
| 19 | `course/methodology/README.md` | 引用 `profiles/`、`handoffs/` 根目录（实际为 `roles/`，无根 handoffs——路径失效） |
| 20 | `course/modules/A~F` | Agent 设计/工具集成/多Agent/商业化/架构/路线图，基于 9-Agent 旧架构 |
| 21 | `course/checklists/*` | new-agent / handoff / tool-launch / service-proposal 检查清单 |
| 22 | `course/关卡6-交付自检清单.md` | 引用 `tests/case1_single_character/` 与 `run_case*.py`（实际不存在——引用失效） |
| 23 | `course/关卡7-上下游分析与连接判断.md` | 已读 |
| 24 | `course/关卡8-Agent接力验证报告.md` | 已读 |
| 25 | `course/关卡9-企业AI服务方案.md` | 概念图快产服务方案，完整 |

### 1.5 skills/k13-version-tree/（全部已精读）
| 顺序 | 路径 | 备注 |
|---|---|---|
| 26 | `skills/k13-version-tree/SKILL.md` + `README.md` + `examples/sample_tree.json` | 版本树工具；示例用"林月"角色（仅示例，非本代项目人物） |

### 1.6 tests/（仅样本，证据 json 排除）
| 顺序 | 路径 | 备注 |
|---|---|---|
| 27 | `tests/00-测试计划.md` | 制片人闭环测试 3 样例，引用 `tests/case*` 证据目录（已缺失） |
| 28 | `tests/验收与优化报告.md` | 读取返回空内容（空文件或仅元数据） |

### 1.7 pipeline/（2 json 已精读，代码仅登记）
| 顺序 | 路径 | 备注 |
|---|---|---|
| 29 | `pipeline/audio_cues_v1.json` | 雨夜寻猫音轨清单；edge-tts 标 🟡需替换；混音 -14 LUFS/48kHz（与 v6.0 一致） |
| 30 | `pipeline/delivery_spec.json` | schema cineast.delivery_spec/1.7；-14 LUFS、24fps、AI 标识；仍提"19 轨/19 岗"（与实际 15 岗不符） |
| — | `pipeline/*.py`（timeline_build/tech_cut/audio_mix 等） | 仅登记，未读代码（按禁忌） |

### 1.8 roles/（15 岗目录；3 代表岗已精读，其余仅登记）
| 顺序 | 路径 | 状态 |
|---|---|---|
| 31 | `roles/producer/` | **已精读**（全套 6 文件）；01-岗位卡/02-工作流/04-Profile 描述 MVP 单 Agent 制片人，SOUL.md 描述 v5.0 九 Agent 协调制片人 → **同岗前后矛盾** |
| 32 | `roles/director/` | **已精读**（01-岗位卡 + SOUL.md）；v0.1 最小映射空骨架（A8 已补 01-岗位卡） |
| 33 | `roles/sound_engineer/` | **已精读**（全套 6 文件）；01-岗位卡等描述 edge-tts/CC0，SOUL.md 写 ChatTTS/Suno/MusicGen+字幕 Whisper → **工具链描述不一致** |
| 34-45 | `roles/animator`、`art_director`、`character_designer`、`cinematographer`、`editor`、`gaffer`、`scene_designer`、`screenwriter`、`script_supervisor`、`storyboard_artist`、`vfx_artist`、`production_coordinator` | **仅登记**（Glob 已知目录结构；animator 等 9 岗满编，cinematographer/gaffer/vfx/script_supervisor/production_coordinator 仅 SOUL.md 空骨架，A8 已补最小映射） |

### 1.9 projects/雨夜寻猫/（每类读 1 代表；整体完成度高、内部一致）
| 顺序 | 路径 | 状态 | 备注 |
|---|---|---|---|
| 46 | `projects/雨夜寻猫/director_intent.md` | 仅登记（读取被系统敏感暂扣） | 路径已知 |
| 47 | `projects/雨夜寻猫/screenplay/雨夜寻猫_剧本_v1.md` | **已精读** | v1；角色林小雨/小白；引用 scene_lock/分镜02 已锁；与分镜表、镜头清单一致 |
| 48 | `projects/雨夜寻猫/storyboard/雨夜寻猫_分镜表_v1.md` | **已精读** | 18 镜 / 80s；铁律自查通过；lock 注入统计完整；引用 assets/storyboards/*.png（已生成） |
| 49 | `projects/雨夜寻猫/shots/雨夜寻猫_镜头清单_v1.md` | **已精读** | 18 镜；✅动态 2（Wan2.2 TI2V 5B 替换进粗剪 v4）；⚠️降级 16；自检记录完整；引用 handoff ANIM-20260925-8310、k13 uuid |
| 50 | `projects/雨夜寻猫/audio/音轨清单_v1.md` | **已精读** | 四轨；edge-tts 候选 A 音色；混音粗剪 v3；与 pipeline/audio_cues_v1.json 口径一致 |
| — | `projects/雨夜寻猫/screenplay/{场景描述,梗概,角色描述}.md`、`assets/`、`k13_locked/`、`timeline/`、`ditmap/`、`output/` 等 | 仅登记 | 运行数据/锁文件/输出按禁忌仅登记路径 |

### 1.10 logs/_handoff_A_20260927/（已精读，本轮核心交接证据）
| 顺序 | 路径 | 备注 |
|---|---|---|
| 51 | `A0_探索报告.md` | 两目录盘底 + 陈旧清单 + 服务/记忆探针（8188 离线、git 196 未提交、19 轨 0 签核） |
| 52 | `A1_合并方案.md` | 合并 `D:\AI影视团队\` → `_archive/legacy_20260727/`（方案 A，待拍板） |
| 53 | `A2_三张对照表.md` | 对照 A（22 条）/B（20 条）/C（量级差 7 成+审美差 3 成） |
| 54 | `A3_目录结构方案.md` | 当前树 + 建议树 + 24 项调整清单 |
| 55 | `A4_清理清单_待替换词.md` | "公牛效果"误用词 4 处（已 A6 归一为"实拍感"） |
| 56 | `A5_接手准备报告.md` | 状态总览 + R1 未达标声明 |
| 57 | `A6_执行报告.md` | 老板拍板后执行：checkpoint commit / 合并 / 目录整理 / 改词（全程可回滚、只新增不删） |
| 58 | `A7_审计件§13十项落地清单.md` | 改哪个文件/哪几行/改成什么（未执行，待拍板） |
| 59 | `A8_第三轮执行报告.md` | 删除 4 项残留 / web 不动 / C 盘记忆待回写 / R2 达标 / 免请示 7 项全执行（含 Blender 白模首跑通） |
| 60 | `research_R1_blockout_pipeline.md` | 白模→写实化路线调研（R1 未达标，9 项未验证） |
| 61 | `research_R2_verified.md` | R1 遗留 9 项收口（R2 达标） |

### 1.11 logs/_mem_mirror/（仅登记，工作区外记忆快照）
| 顺序 | 路径 | 备注 |
|---|---|---|
| 62 | `HANDOFF_FROM_MCP_20260926.md`、`PENDING_MEMORY_APPENDS.md`、`project_memory.snapshot.md`、`user_profile.snapshot.md` | 记忆镜像轨；A8 记 C 盘真记忆 15 条待回写未执行 |

---

## 2. 错误清单（12 类表格，无问题写"无"）

| 错误ID | 类型 | 所在文档(路径) | 具体位置 | 错误描述 | 建议处理方式 | 严重度 |
|---|---|---|---|---|---|---|
| E-01 | ②前后矛盾 | `AGENTS.md` | 全文 | 称"9 个 Profile / 6 个专业岗"但列出 7 个岗名（编剧/角色/场景/分镜/动画/音效/剪辑），数量与枚举自相矛盾 | 按实际 9 bot（hermes/profiles）重写口径，老板授权后刷新 | P1 |
| E-02 | ②前后矛盾 | `roles/producer/SOUL.md` vs `01-岗位卡`/`02-工作流`/`04-Profile` | SOUL.md 描述 v5.0 九 Agent 协调制片人（@艺术总监/飞书群聊/kanban）；另三件描述 MVP 单 Agent 制片人（只调 ComfyUI 生成） | 同岗内部描述代际分裂，读者无法判断制片人实际形态 | 以 SOUL.md 为现行口径，另三件标注"历史 MVP 方案"或重写 | P1 |
| E-03 | ②前后矛盾 | `roles/sound_engineer/SOUL.md` vs `01-岗位卡`等 | SOUL.md 写 ChatTTS/Suno/MusicGen 且提"字幕生成 Whisper"；01-岗位卡描述 edge-tts/CC0 四轨 | 工具链描述不一致；与 pipeline 实际 edge-tts 口径冲突 | 统一到 edge-tts（黄灯待替换）口径，删 Suno/MusicGen/Whisper 字幕表述 | P1 |
| E-04 | ②前后矛盾 | `docs/好莱坞大片级对标…执行手册.md` §6.1 | 交付六档写 -18~-24 LUFS / 1080p 30fps 8-15Mbps | 与 `pipeline/delivery_spec.json` v1.7（-14 LUFS±0.5 / 24fps / 48kHz）两套口径并存，pipeline 只认后者 | 表上方加注"执行数值以 delivery_spec.json 为准"（A7 #8 已列，待执行） | P0 |
| E-05 | ②前后矛盾 | `docs/好莱坞大片级对标…执行手册.md` 标题 | "全阶段零返工" | 审计件 v6.0 已指正"零返工"不实现；对外承诺与实测矛盾 | 对外措辞改"废片率可测+不降级交付"（A7 #4 已列，待执行） | P1 |
| E-06 | ③数据不一致 | `MEMORY.md` | "角色设计师出小雪三视图" | 雨夜寻猫项目实际角色为"小白"（白猫），非"小雪" | 改为"小白"；同步 C 盘记忆（待回写） | P1 |
| E-07 | ③数据不一致 | `docs/*` 多文档 + `pipeline/delivery_spec.json` | 岗位数 9→13→14→18→19 演进 | docs 标 19 岗/19 轨，roles 实际 15 目录，运行层仅 9 bot（hermes/profiles），delivery_spec 仍写"19 轨/19 岗" | 全仓统一口径：文档 19、运行 9、roles 15；标注"对外产能按 9 bot" | P0 |
| E-08 | ④引用失效 | `course/methodology/README.md` | 引用 `profiles/`、`handoffs/` | 实际目录为 `roles/`，根无 `handoffs/`（A6 已迁 `_archive/root_legacy/`） | 改为 `roles/`；或补说明 | P2 |
| E-09 | ④引用失效 | `course/关卡6-交付自检清单.md` | 引用 `tests/case1_single_character/`、`run_case*.py` | 实际 `tests/` 仅剩 `00-测试计划.md`+`验收与优化报告.md`，case 目录已缺失 | 更新路径或标注"样例已移除" | P2 |
| E-10 | ④引用失效 | `AGENTS.md` | 资产目录 `C:\Users\LZH\ai_film_projects\` | 实际主目录为 `D:\aifilmteam\ai_film_projects\` | 路径改为 D 盘（老板授权后刷新） | P1 |
| E-11 | ⑥命名漂移 | `docs/*`（历史） | "公牛效果"用词 | 输入法打错词，非项目术语；全息文档 2 处 + 记忆快照 1 处（C 盘 1 处） | A6 已归一为"实拍感"，grep 归零；C 盘 1 处待老板回写 | P2 |
| E-12 | ⑦版本混乱 | `docs/团队架构v4.0…md` 标题 | "18 岗位定稿" | 正文已含导演岗实为 19；复刻OiiOii 仍写"9 角色"旧口径 | 标题改"19 岗位（18+导演）"（A7 #6 已列） | P2 |
| E-13 | ⑧孤立文档 | `docs/_archive/` 5 篇 + 根 `AGENTS/MEMORY/USER/config.yaml` + `course/` | — | 旧路线/旧平台/旧记忆，与现役 8 份 docs 并存，易被接手 AI 误读为现行前提 | 已归档的保持；根 4 配置 A3 标记[残留]，待老板授权刷新 | P1 |
| E-14 | ⑨重复文档 | `docs/AI交接全息文档.md` §8 vs `roles/*/SOUL.md` | 岗位描述 | 全息文档岗位表与 15 份 SOUL.md 重复描述，易漂移 | 全息文档改为"索引+链接"，不重复正文 | P2 |
| E-15 | ⑨重复文档 | `docs/*`（本代）vs `v2/docs/_legacy_source/` | — | 本代 docs 被镜像进 AI影视团队v2 的 _legacy_source（用户已知）；两处并存若各自修改会分歧 | 以本代为主源，v2 仅作只读镜像 | P2 |
| E-16 | ⑩过时内容 | 根 `AGENTS/MEMORY/USER/config.yaml` + `README.md` | 08-17~08-22 | 停留在 Hermes+飞书+9 岗+SDXL 时代；与 09-26 新路线全面冲突 | 老板授权后一次性刷新（A6/A7 已备方案） | P0 |
| E-17 | ⑩过时内容 | `docs/v3.0技术附录-部署与接入手册.md` | 硬件行 | 写 ComfyUI 0.33.1（实测 0.37.2）；提 Wan3.0（实际 wan2.6/2.7） | 同步实测版本（A7 #2 已列） | P1 |
| E-18 | ⑪AI幻觉 | `docs/*`（旧文档，含手册/技术附录） | 模型与参数 | Wan3.0（实为 wan2.6/2.7，无 Wan3.0）；H3 33B 非 138B；Seedance 开源为假；响度 -18~-24 LUFS（实为 -14）；FLUX dev 非商用红灯——v6.0 已指正，但手册等未同步修正 | 按 v6.0 实测 + A7 #2/#7/#8 落地修正（清单已出，待拍板执行） | P0 |
| E-19 | ⑫未完成项 | `roles/director/` 等 6 空骨架岗 | 仅 SOUL.md | A0 记 6 份空骨架；A8 已补 `01-岗位卡` 最小映射，但 02-05 工作流/流程图/Profile/工具配置仍缺 | 按 A8 模板补齐各岗 02-05 | P1 |
| E-20 | ⑫未完成项 | `pipeline/timeline/master_v2.json` | gaps_by_owner.json | 19 轨契约已建，但 0 条 owner 签核，647 条 blocking_errs，时间轴为空壳 | 启动逐轨签核流程（A5 §3.4） | P0 |
| E-21 | ⑫未完成项 | 全仓（云引擎接入） | `.env` 不存在 | 两 Key 未到，dashscope/minimax/kling 真实调用 0 处；全片仍 88.9% 静图 | 老板注册两 Key 后写 .env 并最小验证 | P0 |
| E-22 | ⑫未完成项 | `logs/_mem_mirror/PENDING_MEMORY_APPENDS.md` + C 盘真记忆 | — | 15 条待回写记忆 + 1 处待替换词未回写，记忆双轨已分歧 | 老板或有权限助手一次性回写（A8 裁决三） | P1 |

> 说明：①内容截断、⑤格式错误 在本代文档中**未发现**（本代文档完整；截断问题见于 v2 镜像件，不在本范围）。

---

## 3. 引用关系

### 3.1 是否引用 三.md / negotiation / AI影视团队v2
- Grep 全范围搜 `三.md | negotiation | AI影视团队v2`：**无命中**（仅 handoff 日志提及 `venv/` 等无关词）。
- 结论：**本代文档未直接引用 AI影视团队v2（7-agent 版）**。与 v2 的重复面为"docs 被镜像进 v2/docs/_legacy_source/"（用户前置提示已知），属单向复制，非本代主动交叉引用。

### 3.2 本范围内部关键交叉引用（路径准确性）
| 引用方 | 被引用方 | 路径准确性 | 结论 |
|---|---|---|---|
| `docs/AI交接全息文档.md` | 各子文档（v6.0/手册/v4.0 等） | 准确（同 docs/ 内） | ✅ |
| `docs/AI交接全息文档.md` §9.3 | `pipeline/delivery_spec.json` | 准确（已加"唯一定义处"注） | ✅ |
| `course/methodology/README.md` | `profiles/`、`handoffs/`（根） | **失效**：实际为 `roles/`；根无 `handoffs/` | ❌ E-08 |
| `course/关卡6-交付自检清单.md` | `tests/case1_single_character/`、`run_case*.py` | **失效**：case 目录已缺失 | ❌ E-09 |
| `projects/雨夜寻猫/storyboard/*` | `assets/storyboards/*.png`、`screenplay/雨夜寻猫_剧本_v1.json` | 分镜表正文引 json 版，实际读到的为 .md 版（json 未列入本普查但属同项目，路径主体有效） | ⚠️ 命名差（md/json 并存） |
| `projects/雨夜寻猫/shots/*` | `handoff ANIM-20260925-8310`、`k13_locked` uuid | 内部 handoff/lock 引用，属同项目运行数据 | ✅ |
| `AGENTS.md` | `C:\Users\LZH\ai_film_projects\` 资产目录 | **失效**：实际 D 盘 | ❌ E-10 |
| `logs/_handoff_A_20260927/*` | `pipeline/delivery_spec.json`、`roles/*`、`projects/雨夜寻猫/*` | 引用均指向现役路径，准确 | ✅ |

### 3.3 本代↔更早代（D:\AI影视团队\）关系
- A1 已将该旧原型归档至 `_archive/legacy_20260727/`（FastAPI+Kimi 旧技术栈，与主目录无接续）；本代不引用它。

---

## 4. 范围小结

### 4.1 性质 / 状态 / 来源 / 日期分布
- **性质**：AI 影视团队"中间代"**当前主目录**（`D:\aifilmteam\ai_film_projects\`），含运行必需 docs/roles/pipeline/projects/tools/blender/comfyui，加学习归档 course/、记忆镜像 logs/_mem_mirror/、本轮交接日志 logs/_handoff_A_20260927/。
- **状态**：高度活跃但**文档层与实存系统性分歧**。docs 13 份中 8 现役 5 归档；根 4 配置全陈旧（[残留]）；roles 15 岗但 6 空骨架（A8 已补最小映射）；项目雨夜寻猫基本完成（18 镜/80s，16 静图+2 动态 Wan2.2）；新路线 Blender 白模已首跑通（A8）。
- **来源**：全部为团队自产文档 + 调研一手引用（R1/R2 含 GitHub/官方 API/官方博客 URL 照抄）；无外部注入。
- **日期分布**：
  - 08-17~08-22：旧路线（AGENTS/MEMORY/USER/config/README + _archive 5 篇）
  - 09-24~09-26 下午：第四批（docs 9 篇新 + 粗剪 v4 + 审计 v6.0）
  - 09-26 22:00~09-27 10:54：夜间新路线（blender/pipeline/tools 落地，文档未跟）
  - 09-27：handoff A0-A8 + R1/R2 交接日志

### 4.2 已知 矛盾/重复/截断/幻觉 汇总
- **矛盾（②）**：E-01~E-05（根配置岗数自相矛盾、producer 岗内代际分裂、sound_engineer 工具链冲突、手册§6.1 vs delivery_spec 双口径、手册"零返工" vs 实测）。
- **重复（⑨）**：E-14（全息文档 vs SOUL 重复）、E-15（本代 docs 镜像进 v2）。
- **截断（①）**：本代**无**（截断见于 v2 镜像件，不在本范围）。
- **幻觉（⑪）**：E-18（Wan3.0/H3 33B/Seedance 开源/-18~-24 LUFS/FLUX dev 红灯等，v6.0 已指正但手册未同步）。
- **数据不一致（③）**：E-06（小雪/小白）、E-07（岗位数 9/13/14/18/19 vs 15 目录 vs 9 bot）。
- **过时（⑩）**：E-16（根 4 配置）、E-17（技术附录版本号）。
- **孤立（⑧）/引用失效（④）/命名漂移（⑥）/未完成（⑫）**：见上表 E-08~E-13、E-19~E-22。

### 4.3 本代独有内容 vs 与 v2 重复内容
- **本代独有**（v2 无或不同）：
  - `course/` 整套方法论（A-F 模块 + 关卡 6-9 检查清单）
  - `projects/雨夜寻猫/` 全量项目数据（剧本/分镜/镜头/音轨/k13 锁/ditmap/timeline）
  - `logs/_handoff_A_20260927/`（A0-A8 + R1/R2）交接与调研日志
  - 15 岗位卡（v2 仅 7 当前 agent）
  - `docs/阶段0体检审计报告与规划修订v6.0.md`（纠偏件）、`docs/AI交接全息文档.md`（中枢件）
  - `pipeline/delivery_spec.json` v1.7（交付规格唯一定义处）
- **与 v2 重复**（单向镜像，非本代主动引用）：
  - 本代 `docs/` 8 篇被镜像进 `AI影视团队v2/docs/_legacy_source/`（用户已知）
  - 概念上"复刻 OiiOii / 对标好莱坞"目标与 v2 同源

### 4.4 roles 15 岗 vs v2 7 agent 差异说明
- **本代 roles（15 目录）**：animator / art_director / character_designer / cinematographer / director / editor / gaffer / producer / production_coordinator / scene_designer / screenwriter / script_supervisor / sound_engineer / storyboard_artist / vfx_artist。其中 9 岗满编（含 director 经 A8 补卡），cinematographer/gaffer/vfx_artist/script_supervisor/production_coordinator 原为空骨架（A8 补 01-岗位卡最小映射）。docs 演进曾标 18→19 岗（含 composer/costume/props/colorist 四岗，实际未建目录，由审计件建议合并进"美术资产岗/虚拟 DP"）。
- **v2 当前 7 agent**：编剧 / 角色设计师 / 场景设计师 / 分镜师 / 动画师 / 音效师 / 剪辑师 —— 与 OiiOii 7 Agent 同构（见复刻OiiOii 文档）。
- **运行层实存**：本代 `hermes/profiles` 仅 **9 个 bot**（animator/art_director/character_designer/editor/producer/scene_designer/screenwriter/sound_engineer/storyboard_artist）；docs 的 19 岗为文档层口径，pipeline 的 19 轨 contract_owners 已用合并后新命名（virtualdp/set_props/script_super/coordinator/color 等），但**文档未记录这次合并**，导致"两套组织架构并存"（A2 B20）。
- **关键差异本质**：本代岗位粒度更细（拆分导演/摄影/灯光/视效/场记/统筹），v2 仅 7 个核心 Agent；本代文档岗数（19）> roles 目录（15）> 运行 bot（9），三层口径未对齐，是接手最大风险点。

### 4.5 普查员结论
本代文档**信息密度高、调研扎实（R1/R2 一手引用规范）**，核心价值在 v6.0 审计件与 A0-A8 交接链。但**文档债严重**：根 4 配置与 5 份 _archive 文档全过时；手册等多处残留 AI 幻觉（Wan3.0 等）与双交付口径；岗位数三层口径分裂；15 条记忆与 §13 十项落地待老板拍板执行。建议优先处理 P0 项（E-04/E-07/E-16/E-18/E-20/E-21），其余按 A7 清单逐项落地。
