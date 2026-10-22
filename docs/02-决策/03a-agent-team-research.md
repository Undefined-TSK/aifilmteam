# 03a 调研报告 · 第三轮 Agent 团队组成 —— 四层深度调研

> 日期：2026-10-02 ｜ 状态：✅ **全四层定稿**——层一/层二（8 系统先例+9 岗+音效双链终核）、层三/层四（组织机制+协作实证）补调研完成，层五映射收口：**22 项维持/强化、0 项推翻、2 项新增（A25 评分校准/A26 预算信封）**
> 口径：证据等级分**一手**（论文原文/官方文档/仓库 README）/ **二手**（博客/汇总页）/ **未验证**；模型许可三态 🟢可商用 / 🟡有条件 / 🔴非商用，代码许可与权重许可分开标；零花费（纯公开资料，未调用任何付费 API）
> 配套文件：`03-agent-team.md`（27 决策点 A1~A24+A6b+A25/A26）——本报告是其证据底座；层五映射见第五节

---

## 〇 调研设计（老板四问 → 四层结构）

老板口径（2026-10-02）：「再做全面深度调研（**团队本身 + 每个成员本身 + 团队与成员的关系 + 成员与成员的关系**），产出调研报告并据此修订/扩充第三轮决策点」。

| 层 | 调研问题 | 方法 | 状态 |
|---|---|---|---|
| **层一 团队本身** | 这种 AI 剧组业界有没有？岗位怎么分？治理什么模式？成本多少？怎么失败？ | 8 个影视多 Agent 系统逐项核实 + 治理/成本/失败模式横向对比 | ✅ 定稿 |
| **层二 每个成员本身** | 9 岗逐个：三.md 怎么定义、v2 家底现状、外部有没有同型先例、缺口在哪；**音效师双链候选池逐项终核**（老板点名重点） | 三.md 5.2/5.3 + v2 音频链实读 + 业界岗位粒度对照 + 模型许可/显存/能力逐项核实 | ✅ 定稿 |
| **层三 团队↔成员** | 授权（谁有权花钱）/考核（怎么评单个 Agent）/资源（token 配额）/上报（何时找人类）/约束（护栏熔断）/反馈（复盘沉淀）的外部证据 | 通用多 Agent 框架（MetaGPT/ChatDev/AutoGen/CAMEL/AgentVerse/CrewAI）组织机制调研 | ✅ 定稿 |
| **层四 成员↔成员** | 协作拓扑/信息传递/冲突类型与解决/信任链/人格设计/失败模式的实证研究 | 协作机制实证论文 + 从众动力学（已有结论） | ✅ 定稿 |

---

## 一、层一 · 团队本身（业界先例全景）

### 1.1 八系统逐项核实

| 系统 | 机构 | 岗位划分 | 架构 | 治理 | 开源/Star | 与 C3 距离 |
|---|---|---|---|---|---|---|
| **FilmAgent**（arXiv:2501.12909，2025-01） | 哈工大深圳+清华 | 导演+编剧+演员+摄影 = **4 岗** | LLM 多 Agent，3D 沙盒，迭代反馈修订 | 集中式：导演管 idea/脚本/分镜/拍摄计划 | 项目页称开源（本次未核到独立 repo）；星数仅二手口径 | 岗位粗、偏虚拟 3D 空间 |
| **Kubrick**（arXiv:2408.10453，2024） | 普渡+百度美研+罗切斯特 | LLM-Director + LLM-Programmer + VLM-Reviewer = **3 岗** | 文本→Director 分解→Programmer 生成 Blender Python 脚本→VLM-Reviewer 截图评审→反馈闭环 | 集中式闭环 | 引用 BlenderGPT（★4,987，GitHub API 一手） | Blender 确定性管线同源，但渲染闭环止于 Blender，无「白模→视频引擎写实化」两阶段 |
| **DreamFactory**（arXiv:2408.11788，2024-08） | 清华+卢森堡大学+北理工 | 多 Agent 框架（正文未展开角色清单——未验证） | 多场景长视频，关键帧迭代对齐风格/角色/场景 | 未验证 | 未验证 | 仅确认「多场景一致性+关键帧迭代」思路 |
| **CineCrew**（arXiv:2609.07720，ECCV 2026） | UMass Amherst+MIT | 故事分析/电影规划/角色场景记忆/表演指导/声音控制/执行/后期等职能 | **FilmDSL 共享协议**贯穿剧本到长片 | 结构化编排 | Apache-2.0，★11（GitHub API 一手），2026-09-29 更新 | 同属「多 Agent 剧组」，但职能未拆到 7+2 细粒度 |
| **MovieAgent**（arXiv:2503.07314，2025） | — | Director + Scene Plan + Shot Plan + 视频/音频生成 ≥**4 岗** | 多 Agent CoT 规划，脚本+角色库→多场景多镜头长视频 | 集中式流水线 | 未验证 | 预演/分镜/生成最接近 C3，但无白模写实化、无音效/剪辑工具岗 |
| **Mind-of-Director**（arXiv:2603.14790，2026-03） | — | 脚本开发/场景设计/角色行为/镜头规划 | 多模态多 Agent 预可视化 | 分布式协作+集中式推理 | 未验证 | 与 C3「导演/编剧/预演/白模」高度重叠，但止于预可视化 |
| **VideoCoCo**（arXiv:2607.27380，2026） | — | Coding Agent（Blender 代码）+ 生成式视频引擎 | **双引擎**：可执行 Blender 代码=过程级 CoT → 确定性时空草稿 → 写实视频 | 双引擎流水线 | 未验证 | **与 C3 技术路线最接近**：Blender 确定性草稿→生成式引擎写实化；但未拆 7+2 岗位 |
| **MAViS**（arXiv:2508.08487，2025） | — | 脚本/镜头/角色建模/关键帧/视频动画/音频 | 长序列叙事，Explore-Examine-Enhance 3E 原则 | 多阶段流水线，无导演中枢 | 未验证 | 覆盖脚本到音频，非白模两阶段管线 |

### 1.2 岗位粒度对比：C3 7+2 是业界最细

| C3 岗位 | 外部先例 | 判定 |
|---|---|---|
| 导演 | Kubrick/MovieAgent/Mind-of-Director 有导演/规划岗 | ✅ 业界标配 |
| 制片 | **多数系统未显式拆分**（CineCrew 有电影规划职能但未成岗位） | 🌟 C3 差异化 |
| 编剧 | FilmAgent 有编剧；MovieAgent 以脚本为输入 | ✅ 业界标配 |
| 预演 | Mind-of-Director 镜头规划最近似；MovieAgent Scene/Shot Plan | ✅ 有同型 |
| 白模 | VideoCoCo Coding Agent、Kubrick LLM-Programmer（均 Blender 向） | ✅ 有同型 |
| 写实化 | VideoCoCo 生成式引擎段、MAViS 视频 | ✅ 有同型 |
| 场记 | **未见任何系统显式拆分**（Kubrick VLM-Reviewer 评审职能最近似） | 🌟 C3 差异化 |
| 音效师 | MovieAgent/MAViS 有音频生成**阶段**，未独立成岗 | 🌟 C3 差异化 |
| 剪辑师 | **未见系统显式拆分** | 🌟 C3 差异化 |

**结论**：现有系统普遍按「导演/编剧/分镜/角色/镜头/生成/音频」粗粒度设计；C3 把**制片、场记、音效、剪辑**从生成流程中独立拆岗是业界空白，正好承载「一人剧组剧场式呈现」的差异化资产（与三.md 8.5「过程可观赏=业界空白」判断互证）。

### 1.3 治理模式对比

| 系统 | 模式 | 对 C3 的含义 |
|---|---|---|
| FilmAgent | 集中式（导演中心） | 同构 |
| Kubrick | 集中式闭环（Director→Programmer→Reviewer 反馈环） | 同构 + Reviewer 职能≈C3 场记+QC |
| CineCrew | 结构化集中式（FilmDSL 统一协议） | 同构：契约协议即 FilmDSL 的 C3 版 |
| MovieAgent | 集中式流水线 | 同构 |
| Mind-of-Director | 分布式协作+集中式推理 | 分布式部分 C3 仅用于平级争执 |
| VideoCoCo | 双引擎流水线 | C3 白模→写实化同源 |

**结论**：导演集中式是业界主流，C3 的「导演管艺术/制片管流程/老板终裁」三层结构有充分先例支撑；差异化在于把治理规则**数值化代码化**（争执 2 轮计数升级、开拍单 409、铁律三档）——业界系统均停在论文描述层。

### 1.4 失败模式与教训（业界踩过的坑）

1. **串联错误传递**：多阶段系统任一环节（脚本/分镜/角色一致/镜头/音频/生成）出错都会向后传递——C3 对策=每阶段契约校验+场记 QC 硬闸（A8）。
2. **导演单点故障**：规划 Agent 不稳定则错误全链累积；从众动力学研究（arXiv:2601.05606）证明**集中式决策快但中心节点错误会迅速扩散**（同模型对齐偏差+「错误但高置信」级联）——C3 对策=导演决策走探针回显+终审建议制（老板保留拍板权），QC 不由导演自检。
3. **长视频一致性瓶颈**：CineCrew/MovieAgent/MAViS 全部围绕角色/场景一致性展开——C3 对策=semantic_map 四层语义映射（三.md 3.9 已定稿）。
4. **多轮迭代反馈延迟**：Kubrick 的 Reviewer→Programmer 多轮闭环瓶颈在迭代质量与延迟——C3 对策=Retake 预算制+打回路由表（A21）。
5. **成本失控无度量**：现有材料**没有找到任何系统公布可复用的逐视频成本表**（二手口径差异极大：$0.103~$318/条）——C3 对策=cost_ledger 自建度量（M11），token 只是维度之一。

### 1.5 成本结构（二手参考，仅定性）

| 来源 | 口径 | 数字 |
|---|---|---|
| VGTeam（arXiv:2509.01277） | 2025-03~05 平均 | ~$0.103/条（一手论文口径） |
| Claude Fable 5 案例（博客） | 脚本到成品 | ~38 万 token / ~$0.40 |
| GPT-5.6 Sol 多 Agent 案例（博客） | 多 Agent 完整视频 | ~4.58 亿 token / ~$318 |

**结论**：成本跨 3 个数量级，完全取决于模型、重试、迭代轮数与引擎调用——印证 C3「Kimi-only+推理分档+重试上限+cost_ledger 实测调档」路线的必要性，且**业界没有可抄的答案，C3 必须自建度量**。

### 1.6 剧场式可观赏协作：定位复核

本轮复核结论：**可核验材料未发现任何新产品已替代 AutoGen Studio / AgentScope / LangGraph Studio 的「可观赏协作」定位**——AutoGen Studio 偏调试/开发侧（中间输出、运行统计、成本观测），AgentScope 偏监控，LangGraph Studio 绑定付费平台。C3 的「剧组群聊剧场+工作台剧组视图」仍是空白区（三.md 8.5 判断维持），且无需新建平台——CrewAI Flows 的执行事件+crew_bus 六类事件+工作台节点图天然构成剧场数据源。

### 1.7 层一结论（六条）

1. **岗位拆分是差异点**：7+2 比业界最细的 FilmAgent（4 岗）还细一倍多，制片/场记/音效/剪辑四岗是 C3 独有。
2. **白模→写实化路线有同型**：VideoCoCo 证明该技术路线学术上成立，C3 不孤独。
3. **导演集中式合理**：六个系统五个集中式；但从众动力学警示中心节点错误扩散——C3 的探针回显+场记独立 QC 是必要保险而非过度设计。
4. **剧场式可视化仍是创新点**：复核未发现竞争产品。
5. **成本必须内部度量**：业界无可复用成本表，cost_ledger 是唯一路径。
6. **失败对策均已内建**：串联错误→契约校验；单点故障→QC 独立+终审制；一致性→semantic_map；迭代延迟→Retake 预算。

---

## 二、层二 · 每个成员本身（9 岗逐个）

### 2.0 方法

每岗四列：**三.md 定义**（已定口径）→ **v2 家底现状**（实读代码）→ **外部先例**（层一 1.2 对照+音频链专项核实）→ **缺口与定性**（A6b 三分法定性+待办）。v2 实读文件清单：`gen_bgm.py`/`gen_sfx.py`/`gen_ambient.py`/`tts_generator.py`/`acestep_client.py`/`build_mix.py`/`audio_cues_v1.json`/`musetalk 相关`。

### 2.1 九岗总览

| 岗位 | A6b 定性 | LLM 用法 | v2 家底现状 | 外部先例 | 层二缺口/待办 |
|---|---|---|---|---|---|
| 导演 | LLM 决策岗 | 高档（意图/仲裁/终审） | v1 有导演岗（飞书 9 岗时代）；v2 无独立实现 | Kubrick LLM-Director / MovieAgent Director | 无缺口；从众动力学警示已对策（1.4-②） |
| 制片 | LLM 决策岗 | 低档（拆解理解） | v1 有；v2 无 | **业界空白**（CineCrew 规划职能最近似） | C3 原创——开拍单/预算路由职责全靠 M4/M11 落地，无先例可抄，R2 实测压力大 |
| 编剧 | LLM 决策岗 | 低档+Instructor | v1 雨夜寻猫剧本人工+LLM 混合 | FilmAgent 编剧岗 | 无缺口 |
| 预演 | LLM 决策岗 | 低档（镜头设计判断） | v2 无对应 | MovieAgent Scene/Shot Plan | shot_spec 15 字段组装是全新契约，R2 首验 |
| 白模 | 混合岗 | 低档（bpy 参数组装） | `make_r4_l1_blockout.py` 已产出 121 帧+EXR 蒙版 | Kubrick LLM-Programmer / VideoCoCo Coding Agent | v2 是**脚本直调**非 Agent 参数组装——A1 岗位卡+组装器是新建 |
| 写实化 | 混合岗 | 低档（路由+引擎参数） | `r4_vace_runner.py` 待建；VACE 权重残缺 | VideoCoCo 生成式引擎段 | 同上，引擎客户端×3 是 P1 主建 |
| 场记 | 混合岗 | 低档（QC 报告生成） | v2 有 qc 零散脚本（freezedetect/ebur128 命令已实测） | **业界空白**（Kubrick VLM-Reviewer 最近似） | C3 原创——QC 阈值体系（光流/IoU/响度）需 R2 标定 |
| **音效师** | 纯工具链岗 | **0**（链内 AI 模型=工具） | **双链雏形已备**：ACE-Step 客户端+smoke 通过 ✅；TTS 用 edge-tts 🔴 违规待换；BGM/SFX 主力仍是程序合成（MVP 档） | MovieAgent/MAViS 有音频阶段无独立岗 | **候选池已终核（2.2）**；双链客户端+组装器映射表是 M15 主建 |
| 剪辑师 | 纯工具链岗 | 0（RIFE/超分=AI 工具） | `pngseq_to_mp4.py`/`build_mix.py`/FFmpeg 打包已有 | **业界空白** | C3 原创；P1 尾段上岗（A11） |

### 2.2 音效师双链候选池终核（老板点名重点）

老板口径（2026-10-02）：「目前开源本地/API 可生成 BGM 音乐音效的模型 + 高级 TTS（像真人配音一样）」。

#### 2.2.1 BGM/音乐链

| 候选 | 代码许可 | 权重许可 | 显存 | 定位 | 核实等级 |
|---|---|---|---|---|---|
| **ACE-Step 1.5 XL Turbo**（turbo AIO） | 🟢 Apache-2.0 | 🟢 **MIT**（①b 遗留的「Apache vs MIT」口径不一致已终核解决：权重卡 MIT+文本编码器 Apache-2.0，商用风险低） | DiT-only ≥4GB；LLM+DiT ≥6GB；12GB 需 offload+INT8 | **本地首选（零成本主力）** | 一手（HF 权重卡+代码仓库） |
| DiffRhythm 2 | 🟢 Apache-2.0 | 🟢 Apache-2.0 | 最低 8GB/推荐 12–16GB | 本地备选（4–5 分钟长曲/编曲向） | 一手 |
| Suno / Udio | 闭源 | 闭源 | 云端 | 云端升级档（人声歌曲需求时，~$10–30/月档） | 二手 |

v2 现状对照：`acestep_client.py` 已就位（CHECKPOINT=`ace_step_1.5_turbo_aio.safetensors`，ComfyUI 原生节点 TextEncodeAceStepAudio1.5，turbo 推荐 steps=8/cfg=1.5，输出 44.1kHz 立体声 flac），smoke 已通过（`05_audio/bgm/acestep_smoke.flac`）——**BGM 链本地首选与 v2 家底完全对齐，零新建成本**。`gen_bgm.py`（泛音钢琴程序合成）降级为兜底链。

#### 2.2.2 SFX 链

| 候选 | 许可 | 定位 | 核实等级 |
|---|---|---|---|
| **Stable Audio 3.0 Small SFX** | 开放权重+Stability 社区许可（**年营收 < $100 万免费商用**——C3 适用） | **SFX 本地首选**（SFX/环境声专用，消费级硬件可跑；注意 Open 1.0 不支持真实人声，人声归 TTS 链） | 一手 |
| CC0 素材库（Freesound/Mixkit/99Sounds） | Freesound 是 CC0/CC-BY/CC-BY-NC **混合需逐文件核验**；Mixkit/99Sounds 免费商用 | **素材底库**（猫叫/门声等具象音效优先走素材而非生成） | 一手（①b 已核） |
| v2 程序合成（`gen_sfx.py` 白噪声滤波） | 自有 | 兜底链（质量 MVP 档） | 本地实读 |

#### 2.2.3 TTS 配音链（「像真人配音一样」的可达性评估）

| 候选 | 代码许可 | 权重许可 | 显存 | 中文情感能力 | 定位 | 核实等级 |
|---|---|---|---|---|---|---|
| **CosyVoice 3**（Fun-CosyVoice3-0.5B-2512） | 🟢 Apache-2.0 | 🟡 **两轮口径不一**（①b 09-27 核得「Apache-2.0 含权重」，10-02 未抓到原文——**R0 下载后读 LICENSE 文件终核**） | 4GB+ 可跑 / 8GB+ 推荐 | **instruct 指令控情绪（哭腔/惊喜/哽咽）+18 方言**——指令级情感控制证据最全；论文口径：中文仍落后真人（英文 1.5B 超真人但 1.5B 未公开） | **本地共首选** | 一手（论文+代码库）/权重待终核 |
| **Qwen3-TTS**（0.6B/1.7B，2026-01 开源） | 🟢 Apache-2.0 | 🟢 Apache-2.0（**明确可商用，许可最干净**） | 0.6B 约 4GB / 1.7B 约 8GB | instruct 控制+声音克隆+声音设计；API 0.115 USD/万字符（≈0.8 元）为云端最低价 | **本地共首选**（与 LLM 栈同厂） | 一手 |
| GPT-SoVITS v4 | 🟢 MIT（官网口径） | 🟢 MIT | — | 原生 48kHz+5s 零样本克隆 | 本地备选（**克隆需求优先**） | 一手 |
| Chatterbox | 🟢 MIT | 🟢 MIT | 0.5B | 多语言中文+情感夸张控制 | 本地备选 | 一手 |
| MiniMax speech-2.8-hd（云端） | 商用 API | — | 云端 | 中文 CER 0.83%（Seed-TTS 榜单口径）云端质量标杆 | 成片级配音升级档（3.5 元/万字符，按镜计费可控） | 一手（①b 核价） |
| Qwen3-TTS API（云端） | 商用 API | — | 云端 | 同本地模型 | 云端最低价档（≈0.8 元/万字符） | 一手 |
| 豆包 TTS（云端） | 商用 API（**商用需书面许可**） | — | 云端 | — | 不进默认池 | 一手（①b） |

**「像真人配音」可达性判断**：① 开源 0.5B 档（CosyVoice 3/Qwen3-TTS 0.6B）已具备**指令级情绪控制**（「用温柔哽咽的语气说」），对白短句场景可达「相当自然」；② 论文自认中文整体仍落后真人配音员——**成片级天花板靠云端升级档**（MiniMax CER 0.83%）；③ 正确预期=本地档做工作样片全片配音、终版关键镜可选云端升级，成本按镜计费可控。A6 推荐架构（组装器从剧本契约映射情绪指令）两条链通用。

#### 2.2.4 排除名单（许可一票否决——商用成片纪律）

| 排除项 | 理由 |
|---|---|
| ~~edge-tts~~（v2 现用！） | 🔴 违反微软自动化条款（①b 09-27 已核）——**M15 开工前必须换掉** |
| ~~IndexTTS-2~~ | Bilibili Model Use License 有条件限制 |
| ~~F5-TTS 官方权重~~ | CC-BY-NC（社区 OpenF5 Apache 版可关注但不进默认池） |
| ~~Spark-TTS 权重~~ | CC-BY-NC-SA |
| ~~Fish Speech~~ | 商用需书面授权 |
| ~~MusicGen / YuE / MMAudio / JASCO~~ | 权重全 CC-BY-NC |

#### 2.2.5 显存治理（双链与写实化并发的挤压）

CosyVoice 3 需 6–8GB、ACE-Step <4GB，与写实化引擎调用（VACE 12GB 级）并发会挤显存。处置（进 A6 决策）：音频 GPU 工序走 **vram_lock 排队**（v2 已有工具）与写实化**错峰**；whisper 转写维持 CPU（铁律不变）；CosyVoice 备 CPU 档（慢但零显存）。音效师铁律从「CPU 跑 whisper 不占显存」扩为「音频 GPU 工序走 vram_lock 错峰；响度 -14 LUFS ±0.5」。

#### 2.2.6 后处理链（R3 已定稿，非 AI，零新建）

afir 卷积真 IR 混响 + ebur128 两遍 loudnorm -14 LUFS + alimiter（level=disabled）+ 强制 -ar 48000 + 四轨混音（`build_mix.py` 已有，audio_cues_v1.json 四轨事件模型直接继承为音效岗输入契约）。

### 2.3 非音频岗逐个补充说明

1. **导演**：唯一高档岗。层一警示（从众动力学：中心节点错误扩散快）要求导演的终审意见**必须带探针回显**且 QC 独立于导演（场记岗执行）——这条已在 A8/A15 承接。
2. **制片**：影视域无同型岗（层一），但**通用框架侧有职能先例**（补调研）：CrewAI hierarchical process 的 manager（协调/委派/验证结果，须显式 `Process.hierarchical`+`manager_llm` 或自定义 `manager_agent`）就是「协调岗」的框架原生形态——C3 主管线走 Flows 不用层级 Crew，manager 语义由 Flow 节点+导演岗承载；但 A2 的**争执仲裁小 Crew 可直接用 hierarchical+manager_agent=导演岗 Agent**（官方机制现成）。其「无开拍单不花钱」铁律在业界多 Agent 系统中**找不到先例**（没有任何系统公布预算审批机制——层三 3.1）——M4 API 层 409 闸门是原创设计，R2 实测是唯一验证途径。
3. **编剧/预演**：先例充分（FilmAgent/MovieAgent），差异仅在 C3 用 Instructor 结构化输出强约束（业界多为自由文本+后解析）。MetaGPT 佐证结构化路线：角色输出 PRD/设计文档等 schema 定义的结构化文档入共享消息池（一手），与 C3「契约产物」同构。
4. **白模/写实化**：v2 现状是**脚本直调**（`make_r4_l1_blockout.py` 手工参数）而非 Agent 参数组装——A6b 混合岗定性下，两岗的 LLM 只做「契约→工具参数」组装（低档+Instructor），组装器是 M5 主建件。
5. **场记**：影视域无独立岗（Kubrick VLM-Reviewer 最近似），**通用框架侧职能先例**（补调研）：AutoGen Reflection 模式（primary 生成→critic 评审→迭代至 approved，二手）+AgentVerse 垂直结构（reviewer 持续反馈 solver 迭代，一手）——「评审反馈闭环」先例充分，缺的是 C3 的 QC 阈值体系（光流≥2px/帧需自建标定、ArcFace 0.75 需自证、IoU 0.65 初值）全部要 R2 实测校准——**没有业界现成数字可抄**（①b 已核实这些阈值无行业基准）。
6. **剪辑师**：业界完全空白。v2 已有 pngseq_to_mp4/build_mix/FFmpeg 打包件，P1 上岗主要是组装而非新建。
7. **角色定义的框架先例汇总**（补调研，MetaGPT/ChatDev/CAMEL）：MetaGPT Role 基类=name/profile/goal/constraints/description+Primary Action（一手）——与 C3 SKILL.md frontmatter+正文（A1/A10）同构；ChatDev 角色嵌入 instructor/assistant system prompt 覆盖子任务/工具/通信协议/终止条件/约束（一手）——C3 把这些拆到岗位卡+契约+校验器更干净；CAMEL 角色扮演双人对话（一手）——适合仲裁小 Crew 的对话形态而非主管线。

### 2.4 层二结论

1. **音效师双链全链路可行**：BGM 本地首选（ACE-Step，v2 已 smoke 通过）+ SFX 双保险（Stable Audio Small SFX+CC0 素材库）+ TTS 双本地共首选（CosyVoice 3 情绪证据最全/Qwen3-TTS 许可最干净）+ 云端升级档（MiniMax 质量标杆/按镜计费）+ 排除名单已封口——**老板要的「开源本地可生成 BGM/音效模型+高级 TTS」市场上全部存在且许可干净，唯一 🔴 是 v2 现用 edge-tts 必须换**。
2. **九岗中四岗（制片/场记/音效/剪辑）为业界空白**——是 C3 的差异化资产，也是「无先例可抄、R2 实测压力大」的风险源，两层含义都要向老板讲清。
3. **「像真人配音」可达性分两档**：本地档=工作样片级（指令控情绪，短对白自然）；成片级天花板=云端升级档（CER 0.83%）。建议口径：「本地为主、关键镜云端升级、按镜计费」。
4. **显存错峰是双链落地的真约束**：vram_lock 排队+写实化错峰已定，进 A6。

---

## 三、层三 · 团队与成员关系（授权/考核/资源/上报/约束/反馈）

> 调研对象：通用多 Agent 框架（MetaGPT/ChatDev/AutoGen/CAMEL/AgentVerse/CrewAI hierarchical）+ 组织化 Agent 工程实践。核心问题：业界有没有「谁有权花钱/怎么考核/怎么限额/何时上报/怎么熔断/怎么复盘」的现成答案。

### 3.1 授权机制（谁有权执行/花钱）

| 先例 | 机制 | 证据等级 |
|---|---|---|
| CrewAI hierarchical process | manager 负责协调/委派/验证结果；**工具可 agent 级或 task 级指定**（权限边界的框架原生能力）；须显式 `Process.hierarchical`+配置 `manager_llm`（或自定义 `manager_agent`） | 一手（官方文档） |
| ATXP 支付授权链 | `hard_cap=True` 余额耗尽抛 `InsufficientCreditsError`→tool function 捕获后返回清理结果；**per-task envelope 防重试循环无限消耗**；识别 tool call escalation / retry loop amplification 两类风险 | 工程先例 |
| 「只读/可写/可花钱」三级权限模型 | **未检索到论文级先例**（未验证） | — |

**对 C3**：制片「开拍单」+M4 API 层 409=预算授权的 C3 原创工程化，方向与 CrewAI task 级工具指定一致但无完整先例可抄——A19 权限矩阵与开拍单的 R2 实测是唯一验证途径。ATXP 的 per-task envelope 恰好补开拍单未覆盖的「任务内循环烧钱」漏洞→本轮新增 A26。

### 3.2 考核评估（怎么评单个 Agent 产出）

| 先例 | 机制 | 证据等级 |
|---|---|---|
| Microsoft Learn LLM-as-judge 指南 | LLM judge 三系统偏差：**length preference（偏好长回复不论质量）/ position bias（偏给前面高分）/ verbosity preference（偏好冗长解释）**；官方建议 50–100 条人工标注校准样本+计算 judge 与人类评分相关性 | 一手（官方培训文档） |
| 评分卡实践 | 评分维度**独立输出 score+pass/fail**（准确率/完整性/来源质量/逻辑一致性分列），避免总分掩盖失败模式；不显式定义维度则 judge 用自身隐含标准、结果不稳定 | 二手 |
| MAST（arXiv:2503.13657） | 单模型回答质量不是多 Agent 失败主因——**系统设计与验证机制才是**（详见层四 4.3） | 一手（论文） |

**对 C3**：场记岗 QC 必然含 LLM 判断成分（构图/叙事/审美类），未校准的 LLM 评分自带三偏差→**新增 A25：QC 评分校准制度**（机器可验证项全代码化不走 LLM；判断型评分先建人工校准集）。

### 3.3 资源分配（token/预算配额）

| 先例 | 机制 | 证据等级 |
|---|---|---|
| OpenLegion 限流指南 | **per-agent quota**：10-agent fleet 共 500 RPM→每 agent 50 RPM，失控 agent 只耗尽自己那份（其余 450 RPM 不受影响），代价=闲置配额不共享；与 circuit breakers+budget caps 并称控制三件套 | 工程先例 |
| ATXP | budget caps：预算耗尽抛异常让上层停止消费而非继续执行 | 工程先例 |
| CrewAI hierarchical | **未检索到 manager_llm 有独立预算/熔断参数的官方证据**——CrewAI 只证明支持委派/工具配置/结果验证，预算熔断须项目自建 | 未验证 |

**对 C3**：cost_ledger（M11）+推理分档（A4）是自建路径；「CrewAI 不自带预算熔断」证实 A26 信封与 M4 开拍单闸必须代码化自建（与 A8「纪律在代码不在 prompt」同构）。

### 3.4 上报机制（何时必须找人类）

| 先例 | 触发条件 | 证据等级 |
|---|---|---|
| Budgeted Act-or-Defer（arXiv:2606.29654） | **置信度**：local k-NN 可靠性下界达标→自主执行；不达标→defer 人类（依赖 bias envelope/representation gap 两可审计假设） | 一手（论文） |
| CascadeDebate（arXiv:2604.12262） | **级联路由**：高置信走单模型→不确定时轻量 agent ensemble→最终 fallback 人类专家；测试时算力按问题难度动态缩放 | 一手（论文） |
| ATXP | **成本超限**：budget cap 触发停止/返回错误/转人工 | 工程先例 |
| MAST FC2 Inter-Agent Misalignment | **规则冲突**：agent 基于错误假设继续执行/不澄清/任务脱轨——适合设为强制上报触发条件 | 一手（论文） |

**对 C3**：A7 路由层三分类=置信路由的 C3 形态；「老板终裁」=human fallback 的制度化。C3 上报三触发与先例三条件一一对应：成本超限→开拍单熔断（M4）、规则冲突→铁律硬闸 FAIL（A8）、争执 2 轮→强制升级导演（A14）。

### 3.5 约束与熔断（护栏/熔断/循环检测）

| 先例 | 机制 | 证据等级 |
|---|---|---|
| OpenLegion | per-agent quotas+circuit breakers+budget caps=Agent 控制三件套 | 工程先例 |
| MAST FC1 System Design Issues | agent 重复工作/不理解何时停止/任务继续执行等循环类失败 | 一手 |
| CrewAI | Max Iterations/Max Requests Per Minute 配置存在，**但不等同于独立循环检测器** | 一手（文档口径） |

**对 C3**：A13（重试 2 次退避→FAIL）+A14（三元组计数第 3 条强制升级）+A8（硬闸代码化）与工程三件套一一对应；A14 的计数器正是 MAST「不知何时停止」失败的解药。

### 3.6 反馈闭环（任务后复盘/经验沉淀）

| 先例 | 机制 | 证据等级 |
|---|---|---|
| AgentVerse 垂直结构 | reviewer 持续反馈→solver 迭代修正（过程反馈闭环） | 一手（论文） |
| S-Agents（arXiv:2402.04578） | tree of agents+hourglass 架构开放环境自组织 | 一手（论文） |
| 「success/failure memory」「lesson learned」标准实现 | **未检索到论文级先例**（未验证） | — |

**对 C3**：A6b「台账驱动岗位演化」（A15 日志→同类判断反复出现→固化进契约/组装器或升档）是 C3 原创闭环；业界无现成实现恰好与 A3「契约即记忆」同构——**C3 的经验沉淀走结构化台账而非 RAG 记忆，方向上避开了无先例区**。

### 3.7 层三结论

1. **授权**：三级权限无论文先例，C3 开拍单+权限矩阵是原创——方向有 CrewAI 工程支撑，数值无先例可抄（R2 实测唯一验证）。
2. **考核**：LLM-as-judge 三偏差实证，必须校准→新增 A25。
3. **资源**：per-agent quota/budget cap 有工程先例；**CrewAI 不自带预算熔断**→新增 A26（自建信封）。
4. **上报**：置信路由+成本超限+规则冲突三触发与 C3 设计一一对应——「老板终裁」有 human fallback 先例形态。
5. **约束**：重试上限/计数升级/硬闸三件套与业界工程一致，无需修改。
6. **反馈**：结构化台账沉淀业界也没做好（无标准实现）——C3 原创且与契约纪律自洽。

## 四、层四 · 成员与成员关系（协作拓扑/信息传递/冲突/信任链/人格/失败模式）

**从众动力学**（Conformity Dynamics in LLM Multi-Agent Systems，arXiv:2601.05606，2026，一手）：
- 集中式拓扑：决策更快，但依赖中心节点能力，存在同模型对齐偏差——**对 C3：导演仲裁降协商成本，但导演错误会快速扩散**（已在 1.4-② 对策）。
- 分布式拓扑：共识更稳健，但网络连通性增加会**加速错误收敛**，形成「错误但高置信」级联——对 C3：平级争执不设「全员辩论」模式，2 轮即升级的熔断设计有理论支撑。
- 实验范式为错误信息检测任务，外推到影视生产需 R2 验证（证据等级：理论方向性，非同域实证）。

### 4.1 协作拓扑实证（重点：辩论的负面证据）

| 拓扑 | 实证结论 | 证据等级 |
|---|---|---|
| **Pipeline 串行** | research→write→edit→publish 顺序链（AutoGen/AG2 常见模式）；适合 C3 主管线（剧本→预演→白模→写实化→剪辑） | 二手（概念汇总） |
| **Debate 辩论** | **负面证据为主**：① Voting or Consensus?（arXiv:2502.19130）：voting 推理任务 +13.2%/consensus 知识任务 +2.8%，但**讨论轮次过多降低性能**；② Debate or Vote（NeurIPS 2025）：majority voting 多基准强势，**T=2→5 轮某些设置性能下降**（算术类）；③ Should we be going MAD?（arXiv:2311.17371）：MAD 不一定可靠优于 self-consistency/多路径 ensembling；④ Debate Trap（36 场景×4 模型×9 基准）：MAD vs CoT 胜率未超 20% | 一手×3 + 二手×1 |
| **Group Chat 群聊** | AutoGen group chat 模式（多方观点碰撞，token/延迟↑） | 二手 |
| **Canvas 共享画布** | **未检索到实证论文**（未验证）——C3 等价物=共享结构化契约文件（shot_spec/semantic_map） | — |

**对 C3**：主管线 Flow 串行（A2）+争执限 2 轮（A14）获实证双支撑；**「全员长辩论」被证据明确反对**——剧场呈现的是「岗位播报」不是「岗位吵架」。

### 4.2 信息传递（共享内存 vs 消息传递 vs 文件交接）

| 方式 | 特点 | 证据等级 |
|---|---|---|
| 消息传递 | 离散消息经协调层（blackboard/message queue/event bus）；agent 不见彼此内部状态——**可审计+易安全隔离**，调试复杂 | 工程先例 |
| 共享内存 | 实现简单适合小系统；并发访问 race conditions | 工程先例 |
| 文件交接 | conversation history=天然 audit trail；结构化文件承载跨 agent 信息交换 | 二手 |

**对 C3**：crew_bus（消息传递+100% 落 SQLite 审计）+契约文件（shot_spec/semantic_map 唯一事实源）=业界推荐的混合模式——3.10 已定架构无需改动，调研反而确认了正确性。

### 4.3 冲突类型与解决（MAST 分类学）

MAST（arXiv:2503.13657，Why Do Multi-Agent LLM Systems Fail?）：150 条 trace 起步、**1600+ 标注 traces、7 框架、专家标注 κ=0.88**——多 Agent 失败不应只归因「模型回答错误」，三大类别：

| MAST 失败类别 | 含义 | C3 对策（已有设计） |
|---|---|---|
| FC1 System Design Issues | 系统配置/目标/流程/终止条件问题；agent 重复工作/不知何时停止 | shot_spec 唯一事实源；A13/A14 终止条件数值化 |
| FC2 Inter-Agent Misalignment | 信息流中断/错误假设/任务脱轨 | 导演仲裁+A14 强制升级；crew_bus 事件全落档 |
| FC3 Task Verification | 质量验证不足 | 场记 QC+A8 硬闸+A21 打回路由 |

**对 C3**：三大失败类别在 C3 设计中均有对应机制——MAST 分类学可直接作 A23 负例测试的设计来源（按 FC1/FC2/FC3 各设计诱导场景验证闸门拦截）。

### 4.4 信任链与验证（输出互检）

| 先例 | 机制 | 证据等级 |
|---|---|---|
| AutoGen Reflection 模式 | primary 生成→critic 评审→迭代至 approved | 二手 |
| CrewAI hierarchical | manager 评估结果+验证完成标准 | 一手（官方） |
| LLM-as-judge 约束 | 可作评估管道一部分但须校准（层三 3.2 三偏差） | 一手 |

**对 C3**：三层质检分层——①机器可验证（schema/IoU/响度/冻结）全代码化；②LLM 初筛（校准后，A25）；③人类仲裁（艺术判断/预算冲突/终审建议）。场记 QC 独立于导演（从众动力学对策）。

### 4.5 人格设计（对协作质量的实证影响）

| 研究 | 结论 | 证据等级 |
|---|---|---|
| The Power of Personality（arXiv:2502.20859） | Big Five 人格组合构建 agent team——行为与团队表现可观测 | 一手 |
| When Does Personality Composition Matter（arXiv:2606.27443） | **人格效果依任务结构**：结构化任务（coding）影响有限；开放式协作/bargaining 显著 | 一手 |
| Not Birds of a Feather（arXiv:2607.19785） | host 选 partner 按人格匹配：创意工作→open 候选人；多数其他→conscientious 候选人 | 一手 |

**对 C3**：A17 人设表的正确写法=「**约束+风格偏好+反馈方式**」而非性格标签——导演=明确决策/仲裁风格、制片=流程/成本/风险提醒、场记=质疑/记录不一致；「避免全员同风格」有实证支撑（同质化降低多视角收益）。

### 4.6 多 Agent 失败模式与团队规模评估（9 岗位合理性）

| 研究 | 结论 | 对 C3 |
|---|---|---|
| MAST | 失败主因=系统设计/协作机制，非单模型能力 | 岗位多少不是关键，机制才是——C3 重机制轻数量 |
| More Agents Is All You Need（arXiv:2402.05120） | 实为 **sampling-and-voting**（任务多采样+多数投票），非盲目加 Agent | 关键节点多次采样交叉验证>增加岗位 |
| When Do MAS Help?（arXiv:2607.16133，2026 信息瓶颈视角）※ | relay 任务（下游决策依赖上游详细证据）的收益取决于**上游信息压缩精确度** | 影视生产正是 relay 任务——**契约 schema 校验是多 Agent 收益的前提**（不是官僚开销） |
| Snowball Error（arXiv:2608.14588） | 幻觉级联四状态 Raw→Derived→Narrative→Invisible，**边界逃逸概率 24.6%→48.3%→89.3%**——越靠后的 Agent 越难发现早期错误 | **阶段边界 verification gate 是必须品**：剧本→shot_spec→白模→写实化每个边界都要闸（A8/A21） |
| CascadeDebate（arXiv:2604.12262） | 轻调用为主、不确定才上 ensemble 的成本感知设计 | C3 7 决策岗+2 工具岗（无 LLM）符合该形态 |

※ 注：本轮检索直接获得的是 2026 年信息瓶颈视角论文；2025 年同题原论文未直接抓到原文，结论以 2026 论文为准（诚实标注）。

**9 岗位规模判定**：无直接证据证明「9 是最优数」；可支撑结论=**「结构化契约+轻量 review+明确仲裁」优于「多 Agent 长辩论」**。C3 的 7+2 分工（判断岗少而精、执行岗工具化、LLM 全按档位限额）与全部实证方向一致——**规模不是风险，机制缺失才是**。

### 4.7 层四结论

1. **2 轮+仲裁获实证双支撑**：Voting or Consensus?+Debate or Vote 均证明轮次过多反降性能——A14 的「2」不是拍脑袋数字。
2. **全员辩论被明确反对**：MAD 胜率<20%（Debate Trap）——剧场=播报不是吵架。
3. **Snowball 级联是边界闸门的硬理由**：89.3% 的 Invisible 态逃逸率意味着写实化岗几乎不可能发现剧本级错误——每阶段契约校验是防线不是仪式。
4. **信息瓶颈理论为契约纪律背书**：多 Agent 收益的前提=上游信息压缩精确——schema 校验/探针回显从「纪律」升级为「收益条件」。
5. **人设=风格约束非性格标签**：A17 人设表写法有实证指引；避免全员同风格。
6. **9 岗位规模：机制>数量**：与成本感知设计（轻调用为主）一致，无反证。

---

## 五、四层综合 → 27 决策点映射（层五）

> 方法：四层调研结论逐条映射到 A1~A24+A6b 决策点，判定=维持（证据不冲突）/强化（证据直接支撑推荐）/新增（调研暴露真空带）。
> 结果：**22 项维持或强化、0 项推翻、2 项新增（A25/A26）**——第三轮设计整体通过外部证据检验。

### 5.1 维持/强化项映射表

| 决策点 | 四层证据（层号） | 判定 |
|---|---|---|
| A1 岗位卡事实源 | MetaGPT Role 基类（name/profile/goal/constraints/description+Primary Action）+角色输出 schema 结构化文档（层二 2.3-⑦）——「角色属性+结构化输出」路线有先例 | 维持 |
| A2 Flows 骨架+小 Crew | **CrewAI 官方「Crews vs. Flows」指南原文：生产就绪应用应从 Flow 开始定义整体结构/状态/逻辑，某步骤需要多 Agent 自主协作时在 Flow step 内嵌 Crew**（层二 2.3-②）——推荐 C 即官方推荐路径；仲裁小 Crew 可用 hierarchical+manager_agent=导演岗 | **强化** |
| A3 记忆全关 | 层三 3.6：无标准 success/failure memory 实现（业界也没做好）；AgentVerse reviewer=过程反馈非跨会话记忆 | 维持 |
| A4 推理分档 | CascadeDebate 成本感知级联：高置信走单模型（层三 3.4）——分档=成本感知路由的 C3 版 | 维持 |
| A5 决策单实例 | per-agent quota 工程：失控实例只耗尽自己配额（层三 3.3） | 维持 |
| A6 音效双链 | 层二 2.2 候选池终核（ACE-Step/CosyVoice 3/Qwen3-TTS/Stable Audio/排除 9 项） | 维持（已重写） |
| A6b 三分法 | When Do MAS Help 信息瓶颈：无判断增量则多 Agent 无收益（层四 4.6）——纯工具链岗不加 LLM 有理论依据 | **强化** |
| A7 路由三分类 | 置信路由（CascadeDebate）+defer 人类（Budgeted Act-or-Defer）先例形态（层三 3.4） | 维持 |
| A8 铁律分层 | Snowball 边界逃逸 24.6%→48.3%→89.3%：越靠后越难发现早期错误（层四 4.6）+MAST FC3 验证不足类（层四 4.3）——**硬闸=级联防线** | **强化** |
| A9~A12 命名/字段/上岗/工具绑定 | CrewAI agents.yaml 标准结构+task 级工具指定（层二 2.3-②/层三 3.1） | 维持 |
| A13 重试 2 次 | ATXP retry loop amplification：重试循环是无上限的成本漏洞（层三 3.1/3.3） | **强化** |
| A14 争执 2 轮升级 | **Voting or Consensus?（轮次过多降性能）+Debate or Vote（T=2→5 退化）+Debate Trap（MAD 胜率<20%）三重实证**（层四 4.1）——「2 轮」数字与研究结论吻合 | **强化** |
| A15 决策日志 | conversation history=audit trail+MAST trace 分析方法论（层三 3.2/层四 4.3） | 维持 |
| A16 岗位卡版本 | MAST：失败可归因到机制变更——版本化是归因前提（层四 4.3 间接） | 维持 |
| A17 剧场人设 | 人格研究三篇：效果依任务结构、partner 匹配按人格、**「约束+风格>性格标签」「避免全员同风格」**（层四 4.5） | **强化** |
| A18 闲聊防御 | 成本感知设计：无关输入不进 pipeline（层四 4.6 CascadeDebate 间接） | 维持 |
| A19 权限矩阵 | CrewAI task 级工具指定（方向一致）；三级权限无完整先例（层三 3.1）——**标注原创风险，R2 实测验证** | 维持+标注 |
| A20 并发写保护 | 共享内存 race conditions 工程警示（层四 4.2）——原子写+单实例双保险正确 | 维持 |
| A21 打回路由 | Snowball verification gate：阶段边界必须设闸（层四 4.6）——打回路由表=闸门的执行细则 | **强化** |
| A22 CrewAI 锁版 | MAST 跨 7 框架对比显示框架行为差异大——锁版隔离风险（层四 4.3 间接） | 维持 |
| A23 行为验收 | **MAST FC1/FC2/FC3 三分类可直接作负例测试设计来源**（层四 4.3） | **强化** |
| A24 隐式模式预留 | 成本感知+按需激活先例（层四 4.6） | 维持 |

### 5.2 新增项（调研暴露的两个真空带）

#### A25 场记 QC 评分校准制度（层三 3.2 证据）

- **真空带**：场记岗 QC 含 LLM 判断成分（构图/叙事/审美类），而 LLM-as-judge 有三系统偏差（长度/位置/冗长偏好，Microsoft Learn 一手）——未校准的评分不可信。
- **候选**：
  | 方案 | 做法 | 问题 |
  |---|---|---|
  | A. 直接用 LLM 评分 | 场记 QC 全走 LLM 打分 | 三偏差系统性污染 QC 结果 |
  | B. 分层+校准 | 机器可验证项（schema/IoU/响度/冻结）全代码化不走 LLM；判断型评分先建 **50–100 条人工校准样本集**，维度独立输出 score+pass/fail；R2 首验时计算 judge 与老板评分的相关性 |
  | C. 全机器指标 | 不用 LLM 评分 | 构图/叙事类无法代码化，QC 覆盖率不足 |
- **推荐 B**：与 A8 铁律分层同构（可代码化全代码化，LLM 只补判断型）；校准集是 LLM 评分可信的唯一证据（业界标准做法）。
- **可逆性**：可逆（校准集可扩充重建）。

#### A26 任务级预算信封（层三 3.1/3.3 证据）

- **真空带**：开拍单管「花钱动作授权」（按镜），A13 管「工具失败重试」（2 次），但**任务内 LLM 自我修正循环**（agent 反复尝试不同方案烧 token）无硬顶——ATXP 识别的 retry loop amplification 正是此漏洞；且 CrewAI 无内置预算熔断（须自建）。
- **候选**：
  | 方案 | 做法 | 问题 |
  |---|---|---|
  | A. 只靠开拍单 | 按镜授权花钱 | LLM 循环烧 token 不触发开拍单（LLM 调用不在「花钱动作」口径内） |
  | B. 开拍单+任务级信封 | 每任务（Flow 节点/仲裁 Crew）设 token/调用数硬顶，耗尽即停+FAIL 事件+上报制片 | 信封数值需实测标定 |
  | C. 全局月度预算 | 只限总额 | 单任务失控烧完全局额度才熔断，粒度太粗 |
- **推荐 B**：per-task envelope 有工程先例（ATXP）；信封初值 R2 按 cost_ledger 实测分布定（如 P95×1.5），进 M4 校验器并与 A15 日账联动。
- **可逆性**：可逆（配置数值）。

### 5.3 层五总结论

1. **零推翻**：四层调研没有任何结论与 25 个既有推荐冲突——第三轮设计整体通过外部证据检验。
2. **六项强化**：A2（官方原文背书）/A6b（信息瓶颈理论）/A8+A21（Snowball 级联）/A13（重试循环放大）/A14（辩论负面实证×3）/A17（人格研究）/A23（MAST 负例来源）——推荐不变、证据升级。
3. **两项新增**：A25（QC 评分校准——LLM judge 三偏差治理）+A26（任务级预算信封——重试循环成本硬顶）。
4. **两项标注原创风险**：A19 权限矩阵+开拍单（三级权限无先例）、A6b 台账驱动演化（经验沉淀无先例）——无先例≠错，但 R2 实测是唯一验证途径，已向老板明示。

---

## 六、参考来源

**层一（全部一手，除标注外）**
1. FilmAgent: https://arxiv.org/html/2501.12909 ｜项目页 https://filmagent.github.io/
2. Kubrick: https://arxiv.org/pdf/2408.10453.pdf
3. BlenderGPT GitHub API（★4,987）: https://api.github.com/repos/gd3kr/BlenderGPT
4. DreamFactory: https://arxiv.org/html/2408.11788v1
5. CineCrew: https://arxiv.org/abs/2609.07720 ｜项目页 https://jiabenchen.github.io/cinecrew/ ｜GitHub https://github.com/Ironieser/CineCrew（Apache-2.0，★11，2026-09-29 更新）
6. MovieAgent: https://arxiv.org/pdf/2503.07314
7. Mind-of-Director: https://arxiv.org/html/2603.14790v1
8. VideoCoCo: https://arxiv.org/html/2607.27380v2
9. MAViS: https://arxiv.org/pdf/2508.08487v4
10. Conformity Dynamics in LLM Multi-Agent Systems: https://arxiv.org/pdf/2601.05606v1
11. VGTeam 成本口径: https://arxiv.org/pdf/2509.01277v1
12. 成本二手参考（博客口径，仅定性）: GPT-5.6 Sol 案例/Claude Fable 5 案例/Nexus 摘要 https://www.zylmyuanbao.com/pdfs/Nexus.pdf

**层二（音频链）**
13. 三.md 5.2/5.3/5.5/6.2/M15/M16/7.1/7.5（项目内文档）
14. v2 实读：tools/acestep_client.py、tts_generator.py、gen_bgm.py、gen_sfx.py、gen_ambient.py、build_mix.py、pipeline/audio_cues_v1.json、docs/R3-架构定稿.md
15. 板块①b 调研（D:\AI影视团队v2\docs\调研-板块①b-质检链与音频链.md：TTS 许可三核/edge-tts 条款/豆包与 MiniMax 价格/ACE-Step 许可/Stable Audio/CC0 素材库/afir/ebur128 两遍法实测）
16. ACE-Step 1.5 权重卡（MIT 终核）/DiffRhythm 2/CosyVoice 3 论文与代码库/Qwen3-TTS 开源发布（2026-01）/GPT-SoVITS v4/Chatterbox/Stable Audio 3.0 Small SFX（Stability 社区许可条款）

**层三（团队↔成员：授权/考核/资源/上报/约束/反馈）**
17. CrewAI Hierarchical Process 官方文档（manager_llm 必配/agent 级与 task 级工具指定）: https://docs.crewai.com/en/learn/hierarchical-process
18. Microsoft Learn「Implement LLM-as-judge evaluation for multi-agent systems」训练模块（三偏差原文+50–100 条校准样本建议）: https://learn.microsoft.com/en-us/training/modules/aaai-design-evaluation-frameworks-multi-agent-azure/3-implement-model-judge-multi-agent-evaluation
19. MAST: Why Do Multi-Agent LLM Systems Fail?: https://arxiv.org/abs/2503.13657
20. Budgeted Act-or-Defer（置信路由 defer 人类）: https://arxiv.org/abs/2606.29654
21. CascadeDebate（成本感知级联）: https://arxiv.org/abs/2604.12262
22. S-Agents（hourglass 架构自组织）: https://arxiv.org/abs/2402.04578
23. ATXP 支付授权链（per-task envelope/retry loop amplification）与 OpenLegion 限流指南（per-agent quota/控制三件套）: 工程实践参考，调研 Agent 返回口径，URL 待补（结论在正文按「工程先例」证据等级标注，不影响决策）

**层四（成员↔成员：拓扑/信息传递/冲突/信任/人格/失败模式）**
24. Conformity Dynamics in LLM Multi-Agent Systems: https://arxiv.org/pdf/2601.05606v1（层一 #10 同源，层四复用）
25. Voting or Consensus?: https://arxiv.org/abs/2502.19130
26. Debate or Vote（NeurIPS 2025）: https://arxiv.org/pdf/2508.17536.pdf
27. Should we be going MAD?: https://arxiv.org/abs/2311.17371
28. Debate Trap（36 场景×4 模型×9 基准，MAD vs CoT 胜率<20%）: https://ordoresearch.ai/blog/the-debate-trap-why-multi-agent-ai-discussions-may-corrupt-rather-than-correct-reasoning ｜理论版（Reasoning Trap 之 MAD 实例）: https://arxiv.org/pdf/2605.01704
29. More Agents Is All You Need（sampling-and-voting）: https://arxiv.org/abs/2402.05120
30. When Do MAS Help?（信息瓶颈视角）: https://arxiv.org/abs/2607.16133
31. Snowball Error（幻觉级联边界逃逸 24.6%→48.3%→89.3%）: https://arxiv.org/abs/2608.14588
32. The Power of Personality: https://arxiv.org/abs/2502.20859
33. When Does Personality Composition Matter: https://arxiv.org/abs/2606.27443
34. Not Birds of a Feather: https://arxiv.org/abs/2607.19785
35. AutoGen Reflection/Group Chat 模式、消息传递/共享内存/文件交接架构对比: 二手概念汇总（正文按「二手/工程先例」证据等级标注）
