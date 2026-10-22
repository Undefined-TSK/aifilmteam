# 16 · 本地优先与 API Key 修订清单（2026-10-03 老板直接修订轮）

> **性质**：老板直接修订轮（非协商轮）。主理人在 API Key 清单问询中暴露四处与老板既有意图不符，老板当场裁定修正。按 ADR 纪律 **supersede-not-delete**：本文件声明修订，原决策行不改写。
> **修订触发原文（老板 2026-10-03）**：①"用 Kimi 太贵，想换廉价的 DeepSeek 或者智谱之类的"；②"飞书平台对我们项目实在不方便，为什么还出现？我不是说要建议换一个平台或自研一个平台吗？"；③"云端视频引擎先从本地开始，能本地跑的先本地跑，之后再云端跑"；④"LLM 可以用 Ollama（本地模型）先跑，之后 LLM 可能有 Kimi，但太贵可能会用 GLM 或 DeepSeek"。

---

## 一、修订声明（supersede 映射）

| 修订号 | 被修订决策 | 原内容 | 修订后 | 理由 |
|---|---|---|---|---|
| **K-REV-1** | A4:145（P0）/ A3:144 / T4:197 / DECISIONS:175 | 三档路由全 Kimi；Kimi-only + 0 元纪律；T4 实测对象=Kimi openai 兼容端点 | **本地优先 LLM 路由**：主力=Ollama 本地模型（零 API 成本）；云端廉价档候选=DeepSeek 或智谱 GLM（老板二选一，未定前不注册）；Kimi 降级为**保留项**（贵，非默认）。三档路由重映射（低/中/高档→Ollama 档位 + 云端兜底分工）**待 R0 实测定档**，定档前不伪装已路由 | 成本敏感（老板明示）；本地 RTX 5070 12GB 可承载中小档推理 |
| **K-REV-2** | K15:361 / PK6:399 / U8:435 / UK8:443 / R0-3 / R0-6 | 飞书主出口 + ntfy 兜底；R0-3 飞书回调测试、R0-6 飞书宕机转移测试 | **飞书移出必需清单**：主出口改 **ntfy**（免 Key、可自建）；自研轻量审批/告警工作台为既定方向（接 React 工作台 U8 路线，飞书卡审批由工作台内审批卡替代）。飞书 App ID/Secret **不再向老板索取**；R0-3/R0-6 飞书专项测试**挂起**，改测 ntfy 主出口链路 | 老板重申此前已表达飞书不便——本团队漏接该意图，登记为流程失误 |
| **K-REV-3** | T5（R0 计划）/ B9 四条件门 | 云端引擎 Key 注册 + 最小验证（每引擎账本 ≤2 行） | **渲染本地优先**：先本地跑通（`local_wan22_fallback` = ComfyUI wan2.2 本地链路、Blender 本地白模/渲染链路），云端引擎（即梦 Seedance / Higgsfield / fal.ai）全部降级 **reserved**，本地链路验证绿之前**不注册、不消费、不索取 Key**。T5 状态：待 Key → **挂起（等本地优先验收后重估）** | 老板明示"能本地跑的先本地跑" |
| **K-REV-4** | （新增资产） | — | 建立《API Key 修订清单》（本文件 §3）：必需 / 候选 / 保留三档落档，老板提出的扩展项（Ollama / DeepSeek / 智谱 GLM）全部登记 | 老板指令"先写在文档当中，记下来保留好" |

---

## 二、修订影响与诚实台账（pending 显影）

1. **T4 function calling 实测对象变更（R0 实测项改写）**：原"Pydantic→OpenAI function spec 在 Kimi 兼容端点字段兼容"→ 改为对**新路由目标**（Ollama 工具调用支持矩阵 / DeepSeek function calling / GLM 工具调用）实测。DeepSeek/GLM 均宣称 OpenAI 兼容，但 tool calling 字段兼容性**未实测，标 pending**；Ollama 仅部分模型支持 tools，**待选型实测**。
2. **A3 记忆机制口径**：原"禁默认 OpenAI embedder（Kimi-only 纪律）"→ 修订为"禁付费 embedder 默认；本地 embedder（Ollama/本地模型）优先"，0 元纪律精神保留、引用对象更新。
3. **engine_routing 枚举不动**：shot_spec.schema.json:225 四枚举值保留（契约向后兼容），本轮只改**使用优先级**（local_wan22_fallback 升为默认首选，三云引擎值保留待 reserved 激活），零 schema 变更。
4. **R0-accept 台账联动**：T5 从"待 Key"改"挂起（本地优先）"；前置台账其余项（16 镜 i2v、230 项回签、crew_bus pending 登记）不变。
5. **流程失误登记**：老板此前已表达"飞书不便、换平台/自研"，第八轮 K15 起草时未承接该意图 → 登记 R-PROC-1（意图承接缺口），后续协商轮起草前须回查老板历史表态。

---

## 三、API Key 修订清单（唯一有效版本，取代主理人 2026-10-03 问询回复版）

### ✅ 必需（现在）——零商业 Key

| 项 | 说明 | Key 需求 |
|---|---|---|
| Ollama 本地 LLM | LLM 主力（K-REV-1）；具体模型档位待 R0 实测（12GB VRAM 约束下选型） | 无 |
| ntfy 告警主出口 | 免费公共服务直用或自建（K-REV-2 升主出口） | 无（自建则自管） |
| 本地渲染链路 | ComfyUI wan2.2 / Blender / whisper / acestep（K-REV-3 默认链路） | 无 |

### 🟡 候选（老板二选一，选定前不注册）

| 项 | 用途 | 说明 |
|---|---|---|
| DeepSeek API Key | 云端 LLM 廉价档（本地跑不动的任务兜底） | OpenAI 兼容；tool calling 兼容性待实测 |
| 智谱 GLM API Key | 同上，与 DeepSeek 互为替代 | 同上 |

### 🔵 保留（reserved，后置，不阻塞任何当前任务）

| 项 | 原用途 | 保留原因 / 激活条件 |
|---|---|---|
| Kimi (Moonshot) API Key | 原 A4 三档全档主力 | 降级原因=贵（老板明示）；激活条件=本地+廉价云端档实测不足且预算允许 |
| 即梦 Seedance API Key | 云端视频引擎 `jimeng_seedance25_blockout` | K-REV-3 本地优先；激活=本地链路验收绿后重估（含价目 valid_until 复核） |
| Higgsfield API Key | 云端视频引擎 `higgsfield_blender` | 同上 |
| fal.ai API Key | 写实化 `fal_ltx23_render_to_real`（M8） | 同上，M8 前重估 |
| ~~飞书开放平台凭证~~ | ~~告警主出口+审批卡~~ | **已移除**（K-REV-2）；如未来自研工作台不满足需求可再评估，届时须老板重新确认 |

### 纪律（不变项）

- Key 只落 `env/` 或 vault（O8/RC4 双路径），绝不入库；明文 CI 阻断（RC-NEW-2）。
- reserved 项激活时逐项过 B9 四条件门；账本纪律（idem_key/fx_rate）不变。

---

## 五、追加（2026-10-03 晚）：百炼测试期额度资产 + 本地 LLM 实测结果

### 5.1 本地 LLM 实测（qwen3:8b @ Ollama 0.33.1）——三连测全绿

| 测试项 | 结果 | 证据 |
|---|---|---|
| 基础对话 | ✅ PASS | 0.5s / 21 tok，正确自报身份 |
| 结构化输出（format JSON schema 约束） | ✅ PASS | 分镜字段抽取 `{"scene":3,...,"duration_s":4}` 精确命中 |
| 工具调用（T4 关键项） | ✅ PASS | 正确发起 `query_weather({"city":"上海","unit":"celsius"})` |
| GPU 确认 | ✅ 100% GPU | `ollama ps`：5.6GB 全显存，RTX 5070 Blackwell 兼容 |

**结论**：本地链路跑通，K-REV-1 本地优先成立，无需向老板求云端救场。测试脚本 `runtime/llm_local_test.py` 留档可复跑。

### 5.2 百炼（DashScope）测试期额度资产（老板 2026-10-03 提供 Key + 408 模型额度台账）

- **Key 位置**：`runtime/secrets/dashscope.env`（gitignored 双重覆盖）；额度台账：`runtime/bailian_models_408.md`（老板整理，408 模型）。
- **授权口径（老板原话）**：免费额度快过期，测试阶段拿来用；模型报错可能=额度用完，切下一个模型。
- **⚠️ 时间压力**：大量额度 **2026/10/27 到期（24 天）**，测试窗口有限。

**项目需求 → 额度模型映射（测试期优先级）：**

| 项目用途 | 首选（额度/到期） | 备选 |
|---|---|---|
| 云端 LLM 廉价档候选（K-REV-1 二选一的**实测素材**） | deepseek-v4.1-flash（1M，**12/13 效期最长**）· glm-5.3（1M，11/23） | deepseek-v4-flash（10/27）· glm-4.7（10/27） |
| 低/中档 LLM（结构化/标准推理） | qwen3.8-flash（999K，11/25）· qwen-flash（1M，10/27） | qwen-plus（1M，10/27）· qwen3.7-flash（999K，10/27） |
| 高档推理（导演仲裁/终审档） | qwen3.8-max（1M，**11/01 最先到期，优先用**）· kimi-k3（1M，11/18） | deepseek-r1（1M）· qwq-plus（1M）· qwen3-max（1M） |
| 视觉理解（分镜画面审阅） | qwen3-vl-flash（1M，10/27） | qwen-vl-max（1M）· qvq-max（1M） |
| 视频生成（K-REV-3 本地优先不变；**T5 云端最小验证可借额度零成本完成**，不需即梦/Higgsfield Key） | wanx2.1-t2v-turbo（200 次）· wanx2.1-i2v-turbo（200 次） | wan2.7-t2v / i2v（各 50）· wan3.0-video（30，11/05）· wan2.6-t2v / i2v（各 50） |
| 图像生成（概念图/海报） | wanx2.1-t2i-turbo（500 张） | z-image-turbo（100）· qwen-image-2.0（100） |
| 语音 ASR（对白转录） | qwen3-asr-flash（36K，**2027/01/25 效期最长**）· paraformer-v2（36K，月重置长期） | fun-asr（36K） |
| 语音 TTS（配音） | qwen3-tts-flash（10K）· cosyvoice-v2（10K） | sambert 系（30K，月重置长期） |
| 向量（若 A3 需云端 embedder 对照） | text-embedding-v4（1M）· qwen3.7-text-embedding-flash（1M，11/30） | text-embedding-v3（500K） |
| **Kimi 免费通道**（老板嫌贵问题在百炼渠道不存在） | kimi-k3（1M，11/18）· Moonshot-Kimi-K2-Instruct（1M） | kimi-k2.5 / k2.6 / k2.7-code（各 1M） |

**测试期切换纪律（老板指令）**：调用报额度类错误 → 按上表切同档备选；切换事件记入测试日志（模型名+错误码+时间）。

### 5.3 对原三档清单的修订说明

- 原「🟡 候选：DeepSeek 或 GLM 二选一」→ **决策可推迟**：额度期内两条路线都免费，先双路实测再让老板选型（实测数据代替猜）。
- 原「🔵 保留：三云引擎（即梦/Higgsfield/fal）」→ **保持 reserved 不变**；但 T5「云端视频最小验证」的能力验证改由百炼 wan 系免费额度承接（零成本、不需新 Key），即梦/Higgsfield Key 依然不索取。
- 本地 Ollama 主力不变；百炼额度定位=**测试期加速器 + 到期后回退本地**。

### 5.4 云端实测第一波结果（2026-10-03 21:15，三连测口径与本地一致）

| 模型 | chat | structured | tools | 备注 |
|---|---|---|---|---|
| **deepseek-v4.1-flash** | ✅ 2.6s | ✅ 2.8s | ✅ 1.1s | **3/3 全绿，全场最快**，廉价档 DeepSeek 路线成立 |
| **glm-5.3** | ✅ | ✅（需适配） | ✅ 1.5s | 推理型模型（reasoning_content 469 字）+ markdown 围栏——须给足 max_tokens≥1000 并剥围栏；适配后 JSON 精确命中 |
| **qwen3.8-flash** | ✅ 2.1s | ✅ 5.0s | ✅ 1.9s | 3/3 全绿，低档结构化可用 |
| **qwen3.8-max** | ✅ 2.2s | ✅ 4.4s | ✅ 1.7s | 3/3 全绿，高档可用（额度 11/01 到期，优先消耗） |
| **text-embedding-v4** | — | 1024 维 ✅ | — | 向量链路通 |
| **wanx2.1-t2v-turbo** | — | 提交成功 ✅ | — | 720p/5s 异步任务 `cad8b519`（T5 云端视频链路零成本验证，结果待回查） |

**老板候选二选一的实测数据**：DeepSeek 路线（v4.1-flash）3/3 零适配全绿；GLM 路线（5.3）功能全通但需适配层（围栏剥离+配额放宽）。**倾向 DeepSeek，待第二波长文本/批量任务实测后交老板定型。**

### 5.5 防断粮机制与资产处置（老板指令 2026-10-03 落档）

1. **路由表**：`runtime/llm_router.json`——本地优先 + 云端按档位有序备选链；链序按额度到期日优化（快到期的先用）。
2. **额度报错处理**：自动滑向链内下一个模型，切换事件记日志（模型名+错误码+时间）。
3. **防任务中途断粮**：长任务先落 checkpoint 再调云端；切换模型后从 checkpoint 续跑，不从头重来。
4. **台账处置**：`bailian_models_408.md` 为**临时资产**——额度全部用尽后向老板汇报并删除该台账记录；**百炼平台本身保留**为未来选项（老板明示平台内有好模型可继续用）。

### 5.6 第二波实测：文→图→审→视频全链路 + 音乐受阻（2026-10-03 21:25）

| 链路 | 模型 | 结果 | 证据 |
|---|---|---|---|
| 文生图 | wanx2.1-t2i-turbo（1024²） | ✅ SUCCEEDED | 雨夜白猫概念图，成片 `outputs/dashscope_wanx21_t2i_concept.png`（1.1MB） |
| **视觉审阅（VL）** | qwen3-vl-flash | ✅ PASS | 对概念图输出专业级分镜分析（三分法构图/冷暖光碰撞/低机位调度建议），1345 tokens——**QC 分镜审阅环节可直接用** |
| 图生视频（i2v） | wanx2.1-i2v-turbo（720p/5s） | ✅ SUCCEEDED（约100s） | 以概念图为首帧生成动态视频，`outputs/dashscope_wanx21_i2v_test.mp4`（2.2MB） |
| 音乐生成 | fun-music-v1 | ❌ 403 AccessDenied | **邀测制**（官方文档确认须在模型广场申请开通），非额度问题；配乐环节暂维持本地 acestep 方案，或由老板去控制台申请开通后解锁 |

**结论**：`文本→图像→VL审阅→视频` 四环全通，百炼侧已具备**分镜概念图→动态预览（animatic）**的完整云端替代管线（与本地 ComfyUI wan2.2 互为备份，正合 K-REV-3 本地优先+云端备选的双轨制）。音乐是当前唯一缺口（邀测墙），已如实上报。

### 5.7 百炼平台长期保留的架构落地（2026-10-03 21:40）

1. **llm_gateway.py 落地 v2**（`AI影视团队v2/tools/llm_gateway.py` + `test_llm_gateway.py`）：五档路由（low_structured/mid_reasoning/high_deep/vision/embedding）——low/mid 档本地 Ollama qwen3:8b 优先、云端按链滑档；high_deep/vision/embedding 直走云端链；额度错自动滑链+切换日志（`runtime/llm_switch_log.jsonl`，只记模型名+错误码）；json 解析带围栏剥离与容错。工程师自测 4/4 PASS（本地 chat/structured、云端 embedding、伪造额度错滑链+日志零密钥泄漏）。**三线收官**：QA 独立复核「可签」（8/8 边界实测含本地不可达滑链、密钥反查零泄漏）→ P2-1/P2-2 修复（死代码清除+额度码 case-insensitive）→ 复跑 4/4 PASS。**已转正**。遗留运维项：生产首次真实滑链后复查日志（P2-3）。
2. **调研报告落档**：`docs/03-规划与调研/百炼模型调研-2026-10-03.md`——408 模型→项目模块映射；三类清单（立即测试期用/到期后值得付费/不适用）；关键发现：wan2.7-i2v 唯一支持首尾帧+口型驱动（M8 控制粒度）、fun-music-v1 付费 0.002 元/秒为最低价候选（邀测制需老板控制台申请）、qwen3-asr-flash 热词注入角色名为转录刚需。
3. **产物 URL 24h 失效纪律**：生成即下载+登记，禁止只留 URL。
4. **额度调度**：快到期优先（qwen-image-3.0 11/03 → wan3.0-video 11/05 → qwen3.8-max 11/01 批次先行冒烟）。

---

## 四、签核

- 裁定人：老板（直接修订，四条全裁定）
- 记录人：主理人代笔（齐活林岗）
- 修订状态：K-REV-1/2/3/4 全部落档；连带 pending 见 §2
- 关联：`DECISIONS.md` 第十六轮索引 · R0-执行计划 T5 状态 · 执行日志 2026-10-03

---

## 五、附录 · 本地 LLM 验收结果与百炼测试 Key 登记（2026-10-03 晚补录）

### 5.1 本地 LLM 验收（K-REV-1 实测闭合）——全绿

| 测试项 | 结果 | 证据 |
|---|---|---|
| 模型 | qwen3:8b（q4，5.2GB），Ollama 0.33.1 | `ollama list` |
| GPU 真实参与 | ✅ **100% GPU**（非 CPU 兜底） | `ollama ps` PROCESSOR 列 |
| 基础对话 | ✅ PASS | 冷启动 22.1s（一次性加载 5.6GB 进显存） |
| 结构化输出（format JSON schema 约束） | ✅ PASS | 分镜字段抽取精确命中（scene=3, duration_s=4） |
| **工具调用（T4 关键项，原定 Kimi 实测）** | ✅ **PASS** | query_weather 参数精确（city=上海, unit=celsius） |
| 热启动吞吐 | **28.1 tok/s** | 46 tok / 1.6s |
| 三档路由映射（pending 定档） | 低/中档=qwen3:8b 本地；高档=待定（本地 qwen3 更大档 or 云端免费额度模型） | 见 §5.3 |
| 测试脚本 | `runtime/llm_local_test.py`（可复跑） | — |

**结论：本地优先路线跑通，不逞能条款未触发**——无需老板考虑云端补位（测试阶段）。

### 5.2 阿里云百炼（DashScope）测试 Key 登记（老板 2026-10-03 晚提供）

- **性质**：测试期免费额度 Key，已落 `runtime/secrets/dashscope.env`（.gitignore 双重覆盖，绝不入库、绝不写入文档）
- **老板指令**：免费额度快过期，测试阶段拿去用；模型报额度错误就切下一个模型
- **额度清单权威来源**：老板提供的控制台导出表（LLM 每模型 1M token，多数 2026-10-27 到期；视觉/语音/向量另计）
- **实测抽查（2026-10-03）**：qwen3.8-flash / qwen3.7-flash / deepseek-v4.1-flash / kimi-k3 / glm-5.3 / qwen3-vl-flash **6/7 直通**（qwq-plus 参数错非额度错，不关键）
- **重大发现（待老板裁决，不擅自动用）**：免费额度含 **wan2.x 视频生成模型**（wan2.2/2.6/2.7 t2v、i2v 各 50 次）与 qwen-image 系（100 次）——**wan2.2-t2v-flash / wan2.2-i2v-flash 与本项目 local_wan22 链路同源**，50 次免费调用足以做云端管线对照测试。K-REV-3 本地优先纪律下，是否动用这批"即将过期"的视频生成额度测云端管线，**留老板拍板**（过期作废，不花一分钱）
- **纪律**：免费额度仅限测试阶段消费；生产链路仍按 K-REV-3 本地优先；调用计账沿用 idem_key/fx_rate 账本纪律

### 5.3 连带 pending 更新

1. ~~T4 function calling 实测~~ → **本地侧已闭合**（qwen3:8b 工具调用 PASS）；云端侧 tool calling 兼容性仍待测（qwen3.8-flash/deepseek-v4.1-flash 各 1 次带 tools 的实测，消耗极小）
2. A4 三档重映射：低/中档=qwen3:8b 本地（已实测）；高档待定——候选：本地更大参数档（qwen3:14b q4，显存临界）/ 云端免费额度高档模型（qwen3.8-max 等，1M token）——待老板选向
3. T5（云引擎验证）：继续挂起，除非老板拍板动用 §5.2 的 wan 免费额度
