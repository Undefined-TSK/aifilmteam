# S6 · 装备矩阵扩展 A~J（老板逐条清单增补）

> 起草：装备矩阵扩展师（equip-v2）｜日期：2026-10-04｜性质：并入《LLM 团队构建系统调研》终稿的分节素材；**旧 320 格不推翻，只增补**（判定口径与 T1_T2 完全一致：必配/P1 试点/观察/不需要 + ★=试点已实证）。
> 输入实读：`_staging_llm_team/sections/T1_T2_定位与装备.md`（既有 64×5 矩阵与覆盖率断言全文）、`A智能体技术全景名词表-2026-10-04.md`（8 分类 64 条定义源）、`docs/02-决策/17d-全链路操作员架构-重构版.md`（§2 六要素/§3 五节点/§4 工具注册表/§5 A2A 轻量落地）、`数字员工培养与监控手册-2026-10-04.md`（岗位卡 subagent_policy/context_budget/培养五件套）、`AI影视团队v2/tools/llm_gateway.py` 与 `tools/crew_bus.py` docstring（H 类与 E 类已落地实证）。
> 纪律：只写本文件一个文件，不改任何决策文档；去国外化约束沿用（国外栈一律 `[不作装备]`）；未验证处如实标注。

---

## 〇、口径对账前置声明（一处必读差异）

旧矩阵实读覆盖率断言（T1_T2 §覆盖率断言原文）：**必配 124 格 / P1 43 格 / 观察 102 格 / 不需要 51 格 = 320 格**。任务简报中"必配 119/P1 45/观察 105/不需要 51"与文档实读不符——**本文一律以 T1_T2 文档实读数字（124/43/102/51）为对账基准**，建议终稿整合时统一口径。

---

## 一、求差集：A~J 全集 vs 既有 64 条

### 1.1 全集条数清点（按旧矩阵捆绑行口径计数）

| 类 | 条目 | 计数 |
|---|---|---|
| A Agent 核心架构 | 微软五组件捆绑（LLM 推理引擎/Tools/Planner-Controller/Memory-Context/Guardrails，计 1 捆绑行）；ReAct 循环；Tool Discovery；Error Recovery；Autonomy/Planning/Tool Use/Orchestration（计 1 捆绑行） | 5 |
| B 协议类 | MCP；A2A；AG-UI；Agent Card；AAIF；MCP Apps/Tasks（计 1 捆绑行，沿旧 #2 口径）；WebMCP；AP2；UCP；x402；ACP（IBM/BeeAI）；ANP | 12 |
| C 调用类 | Function Calling；Structured Output；Agent Skills(SKILL.md)；AGENTS.md；Tool Registry；Tool Poisoning | 6 |
| D 检索记忆类 | RAG；Agentic RAG；GraphRAG；Embedding 向量库；长期记忆（Mem0/Letta/Zep/LangMem）；Context Engineering；Context Rot；Progressive Disclosure | 8 |
| E 多智能体与子代理类 | Sub-agent；Supervisor-Handoff；Planner-Executor；Agent Orchestration；LangGraph；OpenAI Agents SDK；Claude Agent SDK；Microsoft Agent Framework；Durable Execution；HITL；Agent Sprawl；Wave 波次；Checkpoint；对话分叉 | 14 |
| F 执行类 | Computer Use；Browser Use；Code Interpreter；Sandbox；Agent Harness | 5 |
| G 质量治理类 | Guardrails；LLM-as-Judge；Agent Evaluation-Tracing；LLM Observability；OpenTelemetry GenAI；OWASP LLM/Agentic/MCP Top 10；Agent Control Plane | 7 |
| H 服务部署类 | LLMOps；模型网关 LiteLLM；vLLM；Ollama/llama.cpp；小模型路由；量化（GGUF/FP8/AWQ） | 6 |
| I 2025-2026 新名词 | Agentic Workflow；Agentic UI；Agentic Retrieval；Agentic Context Engineering(ACE)；Assist-to-execute line；智能体十大主题词（基础设施/互联协作/工程化/学习进化/记忆/技能/产品创新/支付协议，计 1 伞词行） | 6 |
| J A2A 核心机制 | Task 生命周期 8 状态；Agent Card 投毒风险 | 2 |
| **合计** | | **71** |

### 1.2 已覆盖清单（63 条 → 映射旧矩阵行，判定沿用不动）

| A~J 条目 | 旧矩阵行 | 备注 |
|---|---|---|
| **A** 微软五组件捆绑 | LLM 推理引擎→#50/#52（网关+Ollama）；Tools→#16（Tool Registry）+17d §2.2 要素②工具箱；Planner-Controller→#32（Planner/Executor）；Memory-Context→#21+#22；Guardrails→#42 | 五组件无单行，全部散见既有行且判定已够 |
| **A** Autonomy/Planning/Tool Use/Orchestration 捆绑 | Planning→#32；Tool Use→#12；Orchestration→#24；Autonomy→岗位卡 tier_reading+escalation 自治边界（17d §2.6/培养手册 §1.1） | 自治边界已制度化为三介入门+escalation |
| **B** 全部 12 条 | MCP#1｜A2A#3｜AG-UI#6｜Agent Card#56｜AAIF#10｜MCP Apps/Tasks#2｜WebMCP#7｜AP2#8｜UCP#9｜x402#9｜ACP#4｜ANP#5 | 无一新增，判定全部沿用 |
| **C** 全部 6 条 | Function Calling#12｜Structured Output#13｜Agent Skills#14｜AGENTS.md#15｜Tool Registry#16｜Tool Poisoning#60 | 同上 |
| **D** 全部 8 条 | RAG#17｜Agentic RAG#19｜GraphRAG#20｜Embedding#18｜长期记忆#21｜Context Engineering#22｜Context Rot#23｜Progressive Disclosure#59 | 同上 |
| **E** 12 条 | Sub-agent→#33（Supervisor/Handoff/Sub-agent 行）；Supervisor-Handoff→#33；Planner-Executor→#32；Agent Orchestration→#24；LangGraph#25；OpenAI Agents SDK#26；Claude Agent SDK#27；Microsoft Agent Framework#28；Durable Execution→#34；HITL#35；Agent Sprawl#36；Checkpoint→#34（op_log+快照回退即自研简版检查点） | Sub-agent 的**递归深度/权限隔离/模型配置**三个维度为旧行未展开的新口径，本文专项 a 深挖补齐（不改 #33 判定） |
| **F** 全部 5 条 | #37/#38/#39/#40/#41 | 同上 |
| **G** 全部 7 条 | #42~#48 | 同上 |
| **H** 全部 6 条 | LLMOps#49｜模型网关/LiteLLM#50★｜vLLM#51｜Ollama#52★｜小模型路由#53★｜量化#54 | **H 类已落地实证**：llm_gateway.py docstring 实读——五档路由+额度链滑档（单模型重试 0 次防卡死）+ llm_switch_log 切换留痕 + 密钥只进进程，全部与旧 #50/#53 判定吻合 |
| **I** 5 条 | Agentic Workflow#57｜Agentic UI#58｜Agentic Retrieval→#19（与 Agentic RAG 同一范式两种表述，判定沿用 #19：仅 N1 P1）｜ACE#63｜智能体十大主题词伞词→逐词映射：基础设施→#10/#48、互联协作→#3/#5、工程化→#22/#49、学习进化→#63/培养手册 §1.5 回灌、记忆→#21、技能→#14、产品创新→#61、支付协议→#8/#9 | 伞词行不单独设格 |
| **J** 0 条 | —（两条均新增，见下） | |

### 1.3 新增清单（8 条，全部进第二节新矩阵）

| # | 新增条目 | 来源类 | 为什么旧矩阵没有 |
|---|---|---|---|
| 1 | **ReAct 循环** | A | 旧矩阵只有 Function Calling 行，17d §2.3"读简报→计划→逐工具调用→观察→迭代"的循环形态未作为独立名词设格 |
| 2 | **Tool Discovery** | A | 旧 #16 是静态 Tool Registry（配置文件即注册中心）；"运行时动态发现工具"是另一动作，未设格 |
| 3 | **Error Recovery** | A | 重试/降级/滑链/人审兜底散见 #50 滑链、专项③④、escalation 三条件，未作为统一名词设格 |
| 4 | **Wave 波次** | E | 批次分波派发（场→镜→候选）未设格；旧 #24 只管编排整体 |
| 5 | **对话分叉** | E | 同一简报分叉多候选的会话形态（白模 3~4 版/抽卡 N 版）未设格 |
| 6 | **Assist-to-execute line** | I | 辅助→执行分界线的治理概念未设格 |
| 7 | **A2A Task 生命周期 8 状态** | J | 旧 #3 与 17d §5.3 只用简化 4 状态（submitted/working/completed/failed）；老板清单给全 8 状态谱 |
| 8 | **Agent Card 投毒风险** | J | 旧 #56 只管 Agent Card 正面能力；投毒是其安全负维度（对齐 #60 同族但对象不同） |

**差集结论**：A~J 全集 71 条 = 已覆盖 63 条（沿用旧判定不动）+ **新增 8 条**。另注：旧 64 条中有 7 条未被老板 A~J 清单点名（#11 ACP-Zed、#29 CrewAI、#30 Google ADK、#31 CAMEL、#55 SGLang/TGI、#62 Agent Swarm、#64 长尾协议；#61 Agentic Commerce 可归入 I 类"支付协议"伞词）——**未点名≠删除，旧判定全部保留**。

---

## 二、新增 8 条 × 5 操作员判定矩阵（40 格）

| # | 名词 | N1 | N2 | N3 | N4 | N5 | 判定理由 |
|---|---|---|---|---|---|---|---|
| 1 | **ReAct 循环** | **必配** | **必配**★ | **必配** | **必配** | **必配** | 六要素③执行循环的学名（Reason→Act→Observe→迭代）。N2 已实证：mcp_pilot_agent ≤8 轮循环五断言全过（DECISIONS.md:851）。配了=五操作员循环范式统一，"每轮 Observe 必须结构化回填"成为硬纪律（防原始输出灌上下文），轮次上限写进岗位卡（各节点上限见专项 b） |
| 2 | **Tool Discovery** | 观察 | **必配**★ | 观察 | 观察 | 观察 | N2 随 MCP tools/list 免费获得运行时动态发现（试点真实使用，工具清单从 blender_mcp 动态取得）；其余节点工具 <10 件且静态——岗位卡 tools[] 声明即发现，动态机制属过度工程。触发条件：registry 超 20 工具或跨节点工具上架频繁再评估 |
| 3 | **Error Recovery** | **必配** | **必配**★ | **必配** | **必配** | **必配** | 重试/降级/滑链/人审兜底四件套收口成一个纪律：gateway 滑链+GatewayExhausted 已实证（llm_switch_log 多条 502 滑档实录）、快照回退已实证（N2 试点）。配了=每操作员"体面失败"有既定路径而非临场发挥，per-node 策略见专项 c |
| 4 | **Wave 波次** | 观察 | P1 | 观察 | P1 | 观察 | 按"场→镜→候选"分波派发，防 30 镜一次性灌顶总线；N2 渲染变体并行、N4 抽卡批量提交是分波主战场（试点雏形=crew_bus R8-C-1 按事件逐镜上报）。N1/N3/N5 串行流水线无波次需求 |
| 5 | **对话分叉** | 观察 | P1 | 不需要 | P1 | 观察 | 同一简报分叉出多候选=白模 N=3~4 版与抽卡 N 版的会话形态（快照 v01~v10 链即分叉树）；主会话保留、每候选一支独立上下文，胜者合流进简报。N3 确定性派生无分叉语义（同输入必同输出） |
| 6 | **Assist-to-execute line** | 观察 | 观察 | 观察 | 观察 | 观察 | 治理理念术语：AI 从辅助人到代替人执行的权力边界。本项目已用 R17-8b 三介入门（三档位指令/锚点签收/人审卡片）把这条线**显式落成制度**——知情即可，价值在对外表述与评审话术，不产生新装备 |
| 7 | **A2A Task 生命周期 8 状态** | **必配** | **必配** | **必配** | **必配** | **必配** | crew_bus task 状态机从现有 4 值扩全 8 值，**纯枚举扩展零成本**且交接语义从此无歧义：input_required=N4 人审卡片等待导演（R17-9-1）、auth_required=quota_gate 预算扩权上报、canceled=导演中止、rejected=A21 交接校验拒绝打回。原 4 值语义不变（向前兼容） |
| 8 | **Agent Card 投毒风险** | **必配** | **必配** | **必配** | **必配** | **必配** | operator_card 是工具白名单与交接信任的根：卡片被篡改=权限矩阵被绕过、下游误信伪造契约。轻量落地=卡片 SHA256 校验和入卡+A19 只读权限矩阵+卡片变更必须走 signoff 留痕；纪律与 #60 Tool Poisoning 同一防注入族（自研卡片为主、外部卡片先审） |

**40 格分布**：必配 21 / P1 试点 4 / 观察 14 / 不需要 1。

---

## 三、重点深挖四题（老板特别强调）

### 专项 a · Sub-agent：谁派、派多深、怎么隔离（扩展旧专项①，不改其判定）

**谁派**：沿 T1_T2 专项①结论不变——N2 派（自检子代理 vision 档 + 渲染变体并行子代理，试点已实证雏形）、N4 派（本地抽卡子代理 + 云端轮询子代理，P1）；N1/N3/N5 不派（单会话结构化任务/确定性工具链/轻音频流水线，无长等待与并行收益）。本专项补齐旧行未展开的三个新维度：

**a-1 递归深度上限 ≤2 层（主操作员→子代理，子代理不得再派）**，理由四条：
1. **上下文预算**：12GB 卡 4K~8K 上下文硬约束，主简报+子简报+回传三层嵌套起聚合冗余指数涨——Context Rot 实证（同文档不同组织方式准确率 98%→64%，名词表 §三）在嵌套场景会加倍恶化；
2. **可复现性**：op_log 树深 ≤2 层人工可重放排障；3 层起 crew_bus 事件链阅读成本超过收益；
3. **业界先例皆浅层**：Claude Agent SDK subagents 一层深、OpenAI Agents SDK handoffs 亦浅（名词表 §四），无深递归生产先例；
4. **收益递减**：本项目子任务（渲染/轮询/VL 判读）单层委派即隔离充分，不存在需要孙代理的场景。
落法：岗位卡 subagent_policy 明文写"子代理禁止再派子代理"（培养手册 §1.1 模板加一行）。

**a-2 权限隔离（工具白名单 + 目录边界）**：
- **工具白名单=主操作员 tools[] 的真子集**：如 VL 自检子代理只领 `vl_scorer + render_frame`，**无** execute_code/snapshot_rollback/导演门工具；白名单在 subagent_policy 逐个声明（认领即授权机制 A12 沿用）；
- **目录边界**：子代理只写 `tasks/{subtask_id}/` 临时工作目录；snapshots/、layer manifest、op_log 主线的写入权归主会话独占——子代理产物经主会话落盘，防止并行写坏契约文件；
- bpy 禁区沿用（Agent 进程不 import bpy，V27/T5 精神）；子代理**无导演门权限**：不能签收锚点、不能扩预算、不能改 tier。

**a-3 上下文隔离（Checkpoint 简洁回传，禁原始输出回流）**：
- **下发=子简报**：从 task_brief 切片（本子任务使命+所需锚点段+done 定义），不是全量简报；
- **过程=事件上报**：子代理经 crew_bus R8-C-1 事件逐段上报进度（试点已实证此通道），主会话只读事件摘要、不被阻塞——这就是 Checkpoint 思想：进度可断点续接，主会话不持有子代理中间态；
- **回传=schema 化小结**：Structured Output 强制（result 结论/逐项 PASS-FAIL/教训行三段句），**禁止原始 VL 判读全文、渲染日志、轮询报文回流主会话**——原文落盘 self_check_report 等文件留档，主上下文只进结论；
- 收益：主会话 token 省下来留给判断，且长等待/并行任务失败不污染主会话（Context Rot 双防）。

**a-4 子代理模型配置（结合 llm_gateway 五档链）**：
| 子任务性质 | 取档 | 模型 | 成本 |
|---|---|---|---|
| 机械型（云端轮询/批量提交/格式转换） | low_structured | 本地 qwen3:4b/qwen3:8b（Ollama） | 0 元 |
| 判读型（VL 自检/评分） | vision | 云端 qwen3-vl-flash 主档 → 本地 Qwen3-VL-4B 回退（量化 P1 到位后切本地常驻） | 厘级/0 元 |
| 主判断（工艺/配对/裁决） | mid_reasoning | 本地 qwen3:8b（主操作员本体，不外包） | 0 元 |
- **原则：子代理承担"手与眼"（机械执行+客观判读），主会话保留"脑"（创作判断与裁决）**——云端大模型只花在主判断与 vision 判读两个不可替代处，滑链兜底由 gateway 自动（已实证）；
- 子代理档位写进岗位卡 subagent_policy 字段（培养手册 §1.1 已预留该字段，本文补齐其取值口径）。

### 专项 b · ReAct 循环 per 操作员（N2 已实证，其余四个给设计）

统一骨架（=六要素③学名化）：`读简报/task_brief → Reason（判断什么）→ Act（调什么工具）→ Observe（结构化结果回填）→ 迭代`，每轮 Observe **必须 schema 化**，轮次上限与停机条件写进岗位卡。

| 操作员 | Reason（判断什么） | Act（工具序列） | Observe（结构化回填） | 轮次上限 | 停机条件 |
|---|---|---|---|---|---|
| **N2**★ 已实证 | 工艺判断：先搭哪层/机位怎么走/灯怎么打/偏差怎么修 | blender_mcp 三起步工具 → snapshot/export_layer_manifest → vl_scorer | get_scene_info 回显 + VL 判读**结论**（原文只进 self_check_report 不回流） | ≤8 轮（mcp_pilot_agent docstring 既定） | 自检 PASS 或到限 escalation |
| N1 | 判档（locked/proposed/free）与措辞（prompt_hint 语义句） | read_intent → rag_kb（同 SET 历史与风格段）→ validate_intent | 校验 PASS/FAIL+RAG 命中摘要（JSON） | ≤4 轮（纯文本任务、工具三件、无长等待） | intent_graph 四字段齐+导演签收单出；简报矛盾→停工上报 |
| N3 | 条件三策择优（depth-only 主力/depth+ref/scribble fallback）+ prompt 语义词挑选 | derive_control → pngseq_to_mp4 → prompt_builder | 帧数对账（8k+1）与产物存在性——**机器门结果，不需要 LLM 判断** | ≤4 轮 | 五件套齐+对账 PASS；确定性工具失败**不进 LLM 循环**，直接 A21 打回 |
| N4 | ref 配对/strength 分档/评分裁决 | local_lvace → vl_scorer → quota_gate → cloud_repaint | 三维评分卡（0.45/0.30/0.15+崩坏否决） | 主会话 ≤6 轮/镜（提交-轮询长等待**外包子代理**，主会话不被阻塞） | top-3 人审卡片出（task→input_required）；或 auth_required 上报 |
| N5 | BGM 风格/音色选择/cue 点微调/节奏变体 | tts/bgm/sfx/acestep → transcribe（whisper 对轴）→ mix → cut | qc_media 对账项 + whisper 对轴偏差数值 | ≤6 轮 | tech_delivery_spec 全 PASS；机检过仍待人签 |

设计差异一句话：N2 循环轮次最多（工艺迭代重）、N3 最少（LLM 只做两次判断其余是脚本）、N4/N5 居中且**长等待必须出主循环**（子代理/jobs 异步承接）。

### 专项 c · Error Recovery per 操作员："体面失败"策略

**全员共享底座（已实证 ★）**：gateway 额度滑链（额度错/5xx/超时/解析失败全滑链，单模型重试 0 次防卡死）→ 链尽抛 GatewayExhausted → 上层 job.failed 事件 + escalation 报导演；Structured Output schema 校验失败→带错误字段重生成 1 次→仍败进人审；escalation 三条件（locked 重试 2 次 FAIL/工具连败 ≥3/将超预算——培养手册 §1.1）。

| 操作员 | 故障类 | 第一响应 | 降级 | 人审兜底 |
|---|---|---|---|---|
| N1 | 校验 FAIL | 带错误字段重读重试 1 次 | 判档拿不准→升 high_deep 仲裁档（不硬判） | 导演签收 intent_graph 本身就是 N1 的人审门；简报矛盾→停工上报不猜 |
| N2 | MCP 断连/渲染崩溃 | 切 batch_render subprocess 主干（**不依赖 MCP 存活**，已投产 #32/#36） | 工艺类 VL FAIL→不阻塞（R17-9-1），意见进人审卡片 | locked 违规→快照回退 v{n} 重做（不删历史）；工具连败 ≥3→挂起+job.failed |
| N3 | EXR 损坏/帧数不符 | **不重试派生**（根因在上游） | — | 无 HITL——机器门自动 A21 路由回 N2 重渲；参数错靠 skill 口诀防呆+对账拦截 |
| N4 | 额度错/云端失败 | quota_gate 拦截+滑链；失败先归因（**引擎问题才重试，白模问题打回 N2**——realizer 旧卡铁律） | 云端断供→本地 LVACE 全档 0 元兜底（降级为纯本地交付） | auth_required=扩预算上报导演，不自行扩大；top-3 卡片=常设人审门 |
| N5 | TTS 失败/对轴漂移 | TTS 滑档：edge_tts→sambert（月重置 30K 长期免费兜底）；漂移超阈值→重混音重切 | 音频生成失败→程序合成兜底（0 元） | 机检（-14 LUFS/ch=2/帧数）过后**仍需人签**——ch=1 漏网教训：机器门之外保留人签最后防线 |

### 专项 d · Context Engineering per 操作员：防 Context Rot 的具体手段

**全员通用三件（旧 #22/#23/#59 必配的落法）**：①**任务简报而非全量契约**——task_brief ≤2000 tokens 五段式（brief_max_tokens，岗位卡 context_budget）；②**Progressive Disclosure**——skills 索引薄载（name+description），命中才载全文；③**交接包 20 字纪律**——路径引用不内嵌二进制、op_log 摘要必带、anchor_status 必填。

| 操作员 | 防 rot 手段（本节点特有） |
|---|---|
| N1 | 输入面最大（全片意图+分镜+36 提案）：按镜切片处理；director_intent 用 read_intent **分节取**不整文塞；intent_graph 只存四字段（tier/anchor/prompt_hint/source_span）不存原文；RAG top-5 拉历史 |
| N2 | 多轮 MCP 循环重灾区：①**分层白模契约折叠视图**——manifest 按 11 元素类型层细记契约、按 4 视图组（G1 几何/G2 运动/G3 光照/G4 配置）折叠呈现，"细在契约、少在呈现"（17d §1.4 拍板）；②≤8 轮上限；③VL 判读原文落盘不回流，上下文只进结论；④用快照版本号指代场景状态，不重复文字描述 |
| N3 | 输入是路径引用包：manifest **按需取层**（派深度图只读 LY_GEO/LY_CAM/LY_PROXY 三层）；prompt 模板派生用 prompt_hint 字段而非全量 description |
| N4 | 评分上下文结构化：三维评分卡固定 schema；候选图给 VL 档传路径引用/缩略而非原图批量内嵌；历史抽卡教训走 RAG 教训行（每日回灌 §1.5），不走全量评分记录 |
| N5 | cue 表即简报范例（audio_cues_v1.json）：按 cue 逐条处理不载全片时间轴；whisper 只回词级时间戳 JSON，不回转写叙述全文 |

---

## 四、统计段

| 项 | 数值 | 说明 |
|---|---|---|
| A~J 全集条数 | **71** | A5/B12/C6/D8/E14/F5/G7/H6/I6/J2（捆绑行口径见 §1.1） |
| 已覆盖 | **63** | 映射旧矩阵 56 行（多条对一行，见 §1.2），判定沿用不动 |
| 新增 | **8** | §1.3 清单 |
| 新增格数 | 8×5 = **40 格** | 必配 21 / P1 4 / 观察 14 / 不需要 1 |
| 条目分布（按最强判定） | 含必配格 **5 条**（ReAct/Tool Discovery/Error Recovery/8 状态/Agent Card 投毒）；纯 P1 **2 条**（Wave 波次/对话分叉）；纯观察 **1 条**（Assist-to-execute line） | 口径沿旧矩阵"按条目最强判定计" |
| 与旧 320 格合并总格数 | 320+40 = **360 格** | 条目 64+8=**72 条** |
| 合并后格分布 | 必配 124+21=**145** / P1 43+4=**47** / 观察 102+14=**116** / 不需要 51+1=**52**（合计 360 ✓） | 旧分布以 T1_T2 实读 124/43/102/51 为基准（见 §〇口径声明） |
| 新增已实证 ★ | ReAct（N2 ≤8 轮）、Tool Discovery（N2 MCP tools/list 随试点工作）、Error Recovery（N2 滑链+快照回退面） | 与旧矩阵 ★ 同口径：有真实运行证据才标 |

---

## 五、"本项目当前不需要"名词与理由（沿旧判定 + 新增说明）

| 名词 | 判定 | 理由 |
|---|---|---|
| AP2 / UCP / x402 / MPP / TAP（支付协议族） | 不需要（旧 #8/#9） | 无 Agent 支付环节，预算控制走 budget_manager 内部记账；老板清单 B/I 类点到只为调研完整性 |
| ANP（去中心化协议） | 不需要（旧 #5） | 单团队内部管线，无跨组织去中心化协作需求 |
| WebMCP | 不需要（旧 #7） | 影视制作无"Agent 访问网页"场景 |
| ACP-Zed / Microsoft Agent Framework / Google ADK / Agentic Commerce / 长尾协议 | 不需要（旧 #11/#28/#30/#61/#64） | 编辑器协议/无 .NET/无 GCP/无代理商务/未过生态验证 |
| Agent Swarm | 观察（旧 #62） | 影视管线是确定性流程不需要涌现，并行用普通并发调度 |
| **robotics 类** | 不需要（天然缺位） | 老板 A~J 清单未含具身智能/机器人类名词；本项目全链为数字内容生产（Blender/生成模型/音视频），无物理世界执行面——如未来清单扩入此类，按"无执行器硬件"直接判不需要 |
| 新增 40 格中唯一"不需要"：对话分叉 ×N3 | 不需要 | 确定性派生同输入必同输出，无多候选会话语义 |

---

## 六、未验证项与本卡诚实显影

1. **A2A Task 8 状态尚未改 crew_bus.py**——本文件只判"必配"与扩枚举方案，实施属后续工程任务（原 4 值语义向前兼容，改动零破坏）；
2. **Agent Card SHA256 校验和**为建议机制，未实现未实测；
3. Wave 波次/对话分叉为设计推断（N2/N4 有并行雏形但未按"分叉"范式整理），N1/N3/N5 无节点级试点；
4. 子代理递归 ≤2 层为建议值，依赖 #40 后续试点标定（含 subagent_policy 模板补行）；
5. 旧矩阵 320 格分布数字以 T1_T2 文档实读为准（124/43/102/51），与任务简报所引 119/45/105/51 存在口径差，建议终稿勘误轮统一；
6. 专项 b 中 N1/N3/N4/N5 轮次上限（≤4/≤4/≤6/≤6）为设计初值，未经各节点首跑校准。

*实盘依据汇总：T1_T2 矩阵逐行实读（64 条 320 格）；名词表 8 分类逐行；17d §2.3 执行循环/§3 N2 行 ≤8 轮/§5.3 交接包 4 状态；培养手册 §1.1 subagent_policy+context_budget 模板字段；llm_gateway.py docstring（五档路由/滑链条件/switch_log 字段/GatewayExhausted）；crew_bus.py docstring（R8-C-1 五要素/WAL 幂等/水位重放）。*
