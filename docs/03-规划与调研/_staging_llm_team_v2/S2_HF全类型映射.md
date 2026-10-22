# S2 · HuggingFace 全任务类型 → 全链路映射表

> **调研人**：hf-matrix（LLM 团队构建·四维深度版·HuggingFace 全类型映射师）｜ **查询日期：2026-10-04**
> **性质**：纯调研，只写本文件，不改任何其他文件；不调用任何付费 API。
> **定位（老板硬约束）**：HuggingFace 只作"模型类型全集"的**参考坐标系**——用于校验我们的模型选型有没有漏掉一整类能力；实际部署一律走国内渠道（百炼 / ModelScope / 硅基流动 / Ollama 本地），全面去国外化。
> **事实源**：
> ① 额度/行号：`runtime/bailian_models_408.md`（408 模型台账，行号=该文件实际行号，已实读核对）；
> ② 官网枚举：https://huggingface.co/tasks （2026-10-04 实查快照，经搜索快照三份交叉一致；hf-mirror.com/tasks 对大陆外 IP 重定向回原站，枚举以原站为准）；
> ③ 先例：`docs/03-规划与调研/百炼模型调研-2026-10-03.md`；
> ④ 五节点定义：`docs/02-决策/17d-全链路操作员架构-重构版.md` §3（N1 意图理解 / N2 白模搭建 / N3 控制图派生 / N4 云端重绘 / N5 配音配乐剪辑）与 QC（质检链，17d §3 各节点锚点+要素④ VL 闭环）。

---

## 一、官网枚举核实结论

2026-10-04 实查 https://huggingface.co/tasks ，官方共 **6 大类 46 个任务类型**（页面模型数为动态值，以下计数取 2026-10-04 快照）：

| HF 官方大类 | 任务数 |
|---|---|
| Multimodal Any-to-Any（多模态任意到任意） | 8 |
| Natural Language Processing（自然语言处理） | 12 |
| Computer Vision（计算机视觉） | 19 |
| Audio（音频） | 4 |
| Tabular（表格） | 2 |
| Reinforcement Learning（强化学习） | 1 |
| **合计** | **46** |

说明：任务页曾传闻的 time-series / robotics / graph-ml / world-model 等分类**未出现在 2026-10-04 实查枚举中**，本表以官网实际枚举为准，不虚构。"reranking"对应官方类型名 **Text Ranking**。

链路关系图例：`N1`=意图理解，`N2`=白模搭建（MCP 操控 Blender），`N3`=控制图派生，`N4`=云端重绘，`N5`=配音配乐剪辑，`QC`=质检/审阅链，`—`=与全链路不相关。
替代标注：`台账`=百炼 408 台账内（给行号）；`渠道`=ModelScope/硅基流动/Ollama 本地；`本地自研`=项目已有本地工具链覆盖。

---

## 二、Multimodal Any-to-Any（8 类，全部相关）

| HF 任务类型 | 链路 | 国内替代（渠道+型号+台账行号） | 缺口 |
|---|---|---|---|
| Image-Text-to-Text（图文→文本，VLM） | N1/N2/N4/QC——VL 回看自检、抽卡评分、意图图像理解 | 台账：qwen3-vl-flash（L37，vl_scorer 主档）、qwen-vl-max（L95）、qwen3-vl-plus（L111）；本地：Ollama qwen3-vl（vlm_check.py 回退档）、Qwen3-VL-4B（tools/vlm_check.py 现用） | 无 |
| Video-Text-to-Text（视频→文本） | N4/QC——成片语义审阅、长视频理解 | 台账：qwen3-vl-flash（L37，支持视频输入按帧计 token）、qwen3.5-omni-flash（L248，720P/400s 音视频理解） | 无 |
| Audio-Text-to-Text（语音+文本→文本） | N5——带指令的语音理解、对白预演判读 | 台账：qwen3-omni-flash（L258）、qwen3.8-omni-flash（L255，12/17 效期）、qwen2.5-omni-7b（L246 可本地） | 无 |
| Visual Question Answering | QC——语义级辅助审阅（构图/穿帮） | 台账：qwen3-vl-flash（L37）、qvq-max（L31，疑难帧推演） | 无 |
| Document Question Answering | N1/QC——读剧本/分镜表/交付规格单 | 台账：qwen-vl-ocr 系（L11/23/56/59/61/120）、qwen3.5-ocr（L130） | 无 |
| Visual Document Retrieval（视觉文档检索） | QC/RAG——分镜参考图入检索（17d §2.7 资产层） | 台账：qwen3-vl-embedding（L398）、tongyi-embedding-vision 系（L393/394/397/403）、multimodal-embedding-v1（L400） | 无 |
| Image-Text-to-Image（图+文指令编辑） | N4——重绘/局部编辑/风格化 | 台账：qwen-image-edit-plus（L144）、qwen-image-edit（L156）、wanx2.1-imageedit（L158）、wanx-style-repaint-v1（L173）、image-out-painting（L210）、wanx-background-generation-v2（L228） | 无 |
| Image-Text-to-Video（图+文→视频） | N4/M8——白模首帧+prompt 写实化 | 台账：wan2.7-i2v（L147，首尾帧+口型）、wan3.0-video（L233，30s 原生音画）、wanx2.1-i2v-turbo（L167）、wan2.2-i2v-plus（L195） | 无 |

## 三、Natural Language Processing（12 类，11 类相关）

| HF 任务类型 | 链路 | 国内替代（渠道+型号+台账行号） | 缺口 |
|---|---|---|---|
| Text Generation | 全节点底座（N1-N5/QC 操作员 LLM） | 台账：qwen3.8-max（L139，11/01 先到期）、deepseek-v3.2（L79）、glm-5.3（L74）、kimi-k3（L106）、qwen3.8-flash（L93）；本地：Ollama qwen3:8b（llm_gateway 三连测全绿） | 无 |
| Text Classification | N1/QC——意图分类、情绪弧线标签、崩坏判读 | 台账：qwen3.8-flash（L93，低档结构化）、tongyi-intent-detect-v3（L63） | 无 |
| Token Classification（NER 等） | N1——剧本元素抽取（角色/道具/场景名，G0 元素 100% 抽取） | 台账：qwen-plus（L28）等 LLM 结构化输出承担（Pydantic schema 派生，17d §2.2）；本地 qwen3:8b tools | 无 |
| Question Answering | N1——导演意图澄清问答、RAG 问答 | 同 Text Generation 档（L139/L79/L93 等） | 无 |
| Sentence Similarity | RAG——同 SET 历史镜头/同元素类型教训检索 | 台账：text-embedding-v4（L407，1024 维已实测）、qwen3.7-text-embedding（L395）；本地：Ollama bge-m3 | 无 |
| Feature Extraction（文本 Embedding） | RAG——rag_vectors.jsonl 向量层（17d §2.7） | 台账：text-embedding-v4（L407）、text-embedding-v3/v2/v1（L404/405/402） | 无 |
| Text Ranking（Rerank） | RAG——检索精排 | 台账：gte-rerank-v2（L392）、qwen3-rerank（L401）、qwen3.7-text-rerank（L406）、qwen3-vl-rerank（L396） | 无 |
| Translation | N5——多语字幕；N1——外语剧本读入 | 台账：qwen-mt-plus（L116）、qwen-mt-flash（L9）、qwen-mt-turbo（L127）、qwen-mt-lite（L107） | 无 |
| Summarization | N1——导演意图摘要；RAG 经验层 op_log 摘要 | 同 Text Generation 档；qwen-long（L17，长文档） | 无 |
| Table Question Answering | N1——分镜表/额度台账读取 | 台账：qwen-long（L17）、qwen-plus（L28）结构化抽取 | 无 |
| Zero-Shot Classification | QC——场景元素免训判类 | 台账：VLM 承担（qwen3-vl-flash，L37）；渠道：ModelScope CLIP 类权重 | 无 |
| Fill-Mask（MLM 完形填空） | — | — | **不相关**：链路无 BERT 措辞补全场景，不设替代（ModelScope 有 chinese-roberta-wwm 等权重，不引入） |

## 四、Computer Vision（19 类，18 类相关、2 类缺口）

| HF 任务类型 | 链路 | 国内替代（渠道+型号+台账行号） | 缺口 |
|---|---|---|---|
| Depth Estimation | **N3 核心**——depth 条件图五件套 | 本地自研：tools/exr_to_control.py（EXR 深度直出，已投产 #37）+ Blender 原生深度 pass；渠道：ModelScope depth-anything 权重（照片无 EXR 时兜底） | 无（自研覆盖，无云端 API 不影响） |
| Image Classification | QC——画面元素判类、资产归类 | 台账：VLM 承担（qwen3-vl-flash，L37）；渠道：ModelScope CLIP/InternVL-C 权重 | 无 |
| Image Feature Extraction | RAG——参考图向量入库、特征锁检索 | 台账：tongyi-embedding-vision 系（L393/394/397/403）、multimodal-embedding-v1（L400） | 无 |
| Image Segmentation | QC——SAM2 IoU 一致性硬指标 | 本地自研：SAM2 已入 qc_media v7 质检链（三.md M26）；渠道：ModelScope sam-vit 权重 | 无（本地覆盖） |
| Image-to-Image | N4——静帧风格化/重绘 | 台账：qwen-image-edit-plus（L144）、wanx-style-repaint-v1（L173）、wanx-x-painting（L239） | 无 |
| Image-to-Text（打标/描述） | N3——prompt_builder 语义标注（17d B4②）；QC | 台账：qwen3-vl-flash（L37）、qwen-vl-ocr 系（L56）、qwen3-omni-30b-a3b-captioner（L298） | 无 |
| Image-to-Video | **N4/M8 主力**——白模帧→写实视频 | 台账：wanx2.1-i2v-turbo（L167，200 次）、wan2.7-i2v（L147）、wan2.2-i2v-flash（L199）、wanx2.1-i2v-plus（L186）、wan2.2-kf2v-flash（L177 首尾帧） | 无 |
| Keypoint Detection（人体姿态） | N3——pose 控制条件候选；QC 动作核对 | 渠道：ModelScope DWPose/RTMPose 权重（ComfyUI 常规件，可本地推理） | **半缺口**：百炼无通用姿态 API；开源权重本地可解，暂不阻塞 |
| Mask Generation | QC——分割掩码（与 SAM2 同件） | 本地自研：SAM2（qc_media v7）；渠道：ModelScope SAM 权重 | 无（本地覆盖） |
| Object Detection | QC——元素覆盖辅助对账（G2） | 台账：VLM 承担（qwen3-vl-flash，L37，2D/3D 空间定位）；垂类台账件：liveportrait-detect（L148）、emo-detect-v1（L149）、emoji-detect-v1（L218）、animate-anyone-detect-gen2（L222） | 无 |
| Video Classification | QC——抽卡筛崩坏、镜头类型判别 | 台账：VLM 帧采样承担（qwen3-vl-flash，L37） | 无 |
| Text-to-Image | M20——概念图/分镜参考图/三视图量产 | 台账：wanx2.1-t2i-turbo（L168，500 张）、wan2.2-t2i-flash（L194）、z-image-turbo（L162）、qwen-image（L157）、qwen-image-2.0（L159）、wanx-sketch-to-image-lite（L150）、wanx-poster-generation-v1（L237） | 无 |
| Text-to-Video | N4/M8——文生视频叙事 | 台账：wan2.7-t2v（L161，1080P 多镜头）、wan3.0-video（L233）、wanx2.1-t2v-turbo（L180，已实测）、wan2.2-t2v-plus（L160）、happyhorse-1.0-t2v（L179） | 无 |
| Unconditional Image Generation | — | — | **不相关**：GAN 无条件生成无影视场景，不引入 |
| Video-to-Video | N4——视频重绘/风格迁移/续写 | 台账：wan2.7-videoedit（L143）、video-style-transform（L219）、wan2.7-r2v（L164，参考视频一致性）、wan3.0-video（L233，first_clip 续写） | 无 |
| Zero-Shot Image Classification | QC——免训风格/场景判类 | 台账：VLM 承担（L37）；渠道：ModelScope CLIP 权重 | 无 |
| Zero-Shot Object Detection | QC——免训元素检出 | 台账：VLM 承担（L37）；渠道：ModelScope OWL-ViT/Grounding-DINO 权重 | 无 |
| Text-to-3D | N2 边缘——3D 资产生成 | 渠道：ModelScope TripoSR/混元3D（Hunyuan3D）权重可本地推理；国产闭源 Tripo（VAST）未纳入四渠道 | **缺口**：百炼/硅基流动/Ollama 均无 t23d API。最近似方案=ModelScope 权重本地部署；且项目哲学即"白模=基本体几何拼装"（17d §1.2），t23d 仅作资产库扩展区，不阻塞 P0-P2 |
| Image-to-3D | N2 边缘——单图重建 3D 资产 | 渠道：ModelScope TripoSR/Hunyuan3D-Image 权重本地推理 | **缺口**：同上，无现成 API；最近似=ModelScope 权重；同样仅资产扩展区 |

## 五、Audio（4 类，全部相关）

| HF 任务类型 | 链路 | 国内替代（渠道+型号+台账行号） | 缺口 |
|---|---|---|---|
| Audio Classification | QC——音频事件/静音/爆音判读 | 台账：Omni 系承担（qwen3.8-omni-flash，L255）；本地自研：ebur128 响度、qc_media v7 机器件 | 无 |
| Audio-to-Audio（含音色转换） | N5——变声/音色转换/角色声线统一 | 台账：qwen3-tts-vc-2026-01-22（L308）、qwen3-tts-vc-realtime 系（L343/359） | 无 |
| Automatic Speech Recognition | N5——对白转录/SRT 字幕；音画对轴 | 台账：qwen3-asr-flash（L296，2027/01/25 全场最长，热词注入角色名）、paraformer-v2（L266，长期）、fun-asr（L355）、gummy-realtime-v1（L269）；本地：faster-whisper（CPU） | 无 |
| Text-to-Speech | **N5 核心**——角色配音 | 台账：qwen3-tts-flash（L305，17 音色+方言）、qwen-audio-3.1-tts-flash（L326，情感标签，1M 额度）、cosyvoice-v3.5-flash（L391）、cosyvoice-clone-v1（L389，长期，10-20s 复刻）、qwen-voice-design（L330）+qwen-voice-enrollment（L333）、sambert 系（L270 等 40+ 音色）；本地：CosyVoice | 无 |

## 六、Tabular（2 类）与 Reinforcement Learning（1 类）

| HF 任务类型 | 链路 | 国内替代 | 缺口 |
|---|---|---|---|
| Tabular Classification | — | — | **不相关**：链路无结构化表格预测场景（额度台账对账用规则代码，非 ML 分类） |
| Tabular Regression | — | — | **不相关**：同上 |
| Reinforcement Learning | — | — | **不相关（现阶段）**：属模型训练范畴非推理链路；若未来微调走 ModelScope ms-swift，不进运行时 |

---

## 七、统计

| 指标 | 数值 | 说明 |
|---|---|---|
| HF 官方任务类型总数 | **46** | 2026-10-04 实查 huggingface.co/tasks，6 大类 |
| 与全链路相关（N1-N5/QC） | **41** | 多模态 8 + NLP 11 + CV 18 + 音频 4 |
| 与链路不相关 | **5** | Fill-Mask、Unconditional Image Generation、Tabular×2、RL |
| 相关类型中有国内替代 | **39** | 其中台账内直接替代 **35**（百炼 408 台账，含行号），渠道/本地自研替代 **4**（Depth、Image Segmentation、Mask Generation、Keypoint Detection——均为本地工具链或 ModelScope 开源权重覆盖） |
| **缺口** | **2** | Text-to-3D、Image-to-3D（详见缺口清单） |
| 覆盖率 | 相关类型 41 类中 95.1% 有落地方案；全类型 46 类中 84.8% | — |

**408 台账核对声明**：本表引用的全部行号均出自 `runtime/bailian_models_408.md` 实读（表体行号 1-410，模型行 3-410，共 408 行模型记录），未编造行号。

## 八、缺口清单（仅 2 项，均不阻塞主线）

| # | HF 类型 | 缺口本质 | 最近似方案 | 阻塞判定 |
|---|---|---|---|---|
| 1 | Text-to-3D | 四渠道（百炼/ModelScope 托管 API/硅基流动/Ollama）均无托管 API | ModelScope 开源权重（TripoSR / 混元3D Hunyuan3D）本地推理；国产闭源 Tripo 未纳入老板四渠道白名单，不引入 | **不阻塞**：17d §1.2 已裁定白模=bpy 基本体几何拼装，3D 生成属资产库扩展区（LY_NODE 同级），P0-P2 无调用点 |
| 2 | Image-to-3D | 同上 | 同上（TripoSR 单图重建） | **不阻塞**：同上 |

**半缺口备注（不算缺口）**：Keypoint Detection 无百炼 API，但 ModelScope DWPose/RTMPose 权重本地推理即 ComfyUI 常规件；Depth/Seg/Mask 同理由自研 EXR 管线与 SAM2 覆盖——此四类为"无云端 API、有本地方案"，计入替代不计入缺口。

## 九、对全链路的结论

1. **模型类型坐标系无遗漏**：全链路五节点+QC 实际调用的能力（LLM/VLM/TTS/ASR/T2I/I2V/T2V/V2V/Embedding/Rerank/音乐）在 46 类官方分类中全部有落点，且**35 类可直落百炼 408 台账**（含行号可核），无"整类能力"缺位。
2. **HF 仅作坐标系**：46 类中 5 类与影视全链路无关（MLM/无条件生成/表格×2/RL），验证了"不追齐 HF 全集、只覆盖链路所需"的去国外化选型策略成立。
3. **唯二缺口在 3D 生成**，且与项目"白模=几何拼装"哲学正交，建议保持不投入，待资产库扩展需求出现时再评 ModelScope 本地权重路线。
4. 与 `百炼模型调研-2026-10-03.md` 的交叉：该报告 §四 C 清单判定"不投入"的 aitryon/wordart/emoji/gui-plus 等垂类，对应 HF 类型（试穿/艺术字/表情包）本就**不在 HF 46 类官方枚举内**，属百炼电商垂类扩展，两份结论互洽。

## 十、出处

- HF Tasks 官方枚举：https://huggingface.co/tasks （2026-10-04 实查，搜索快照三份交叉一致：hf.co/tasks、huggingface.co/tasks、hf.co/tasks?utm… 三份枚举均为 6 大类 46 类型）
- hf-mirror.com/tasks 实查（2026-10-04）：对非大陆 IP 重定向回原站，枚举以原站为准
- 额度台账与行号：`runtime/bailian_models_408.md`（408 行模型，2026-10-04 实读）
- 先例映射：`docs/03-规划与调研/百炼模型调研-2026-10-03.md`
- 五节点定义与工具注册表：`docs/02-决策/17d-全链路操作员架构-重构版.md` §3/§4
