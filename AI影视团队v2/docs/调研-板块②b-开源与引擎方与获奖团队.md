# 调研-板块②b 开源读源码 + 引擎方与获奖团队

**范围**：comp-opensource（源码级）/ comp-vendors-awards（引擎供应方 + 获奖团队）
**访问日期**：2026-09-27 ｜ **核验人**：team-lead 亲自（子代理 LLM 通道 429 期间直取）
**老板三条硬要求**：结论落 ✅/❌/⚠️/❓ ｜ 每条带反方证据 ｜ 口径统一（来源+日期+证据等级）

---

## 一、开源读源码（comp-opensource）

### 1.1 头部开源项目（源码级核验）

| 项目 | 许可 | 规模 | 定位 | 与我们路线的关系 | 证据等级 |
|---|---|---|---|---|---|
| **VideoClaw** (HITsz-TMG/VideoClaw) | **MIT** | 1.3k⭐ | 智能体式"视频生成员工"，支持 Wan/Kling/CogVideoX 多后端 | 通用文生视频编排，**非** 3D-blockout 驱动 | 一手（repo + 二手综述） |
| **ViMax** (HKUDS/ViMax) | **MIT** | 5.7k+⭐ | 多智能体（Director/Screenwriter/Producer/Generator 一体） | 含 `best_image_selector.py` VLM 质检门 + `reference_image_selector`（≤8 参考图）；**图优先**，非白模驱动 | 一手（DeepWiki 源码拆解 + 二手） |
| **Mickmumpitz AI Renderer 2.0** (2026-02) | 免费工作流（CC? 未明示） | — | ComfyUI+Blender，Wan2.1 VACE14B+SkyReels V3 R2V+Z-Image Turbo+Depth Anything 3 | 本地白模→写实，**形态最接近我们**；24GB 显存下限 | 一手（官方博客/YouTube） |
| **Wan 2.2 VACE / Wan2.1-VACE-1.3B** | **Apache-2.0** | — | 本地视频生成，吃 depth/pose 控制 | **我们的本地零成本路径**（R4 先跑） | 一手（模型卡） |
| **ComfyUI-WanVideoWrapper + Blender** | 依上游 | — | 相机内参→AI、深度图→controlnet | 工程参考：相机/深度标准化桥接 | 二手（社区文） |

> ⚠️ **命名消歧**：npm 上的 `davendra/videoclaw` 是**另一个项目**（自定义专有许可，仅个人/非商用免费），与 HITsz-TMG/VideoClaw 无关。我们引用的开源 VideoClaw = HITsz-TMG 版，MIT。

### 1.2 ViMax 一致性检查实现（重点读）

`best_image_selector.py`（已读源码片段）做法：
- 一个镜头并行出 **N 张候选图** → 调 VLM 当裁判，从三维度打分：**人物一致性**（性别/族裔/年龄/面部/体型/外貌/发型七项逐项对参考图）、**空间一致性**（相对左右位置/场景布局/透视）、**文本符合度** → 只取最优，都不达标则重生成。
- 提示词硬性要求："优先选无白边/黑边/多余画框的图"。
- `reference_image_selector.py`：从角色肖像(前/侧/后三视角)+前序帧+机位过渡图里检索 **≤8 张最相关**参考，控上下文长度。

→ 这是"把抽卡变批量生成+自动品控"的成熟模式，**可迁移**到我们的 `script_supervisor` / 生成后验收（尤其 C-07 残余漂移量化可借鉴其 VLM 评分思路）。

### 1.3 ⚠️ 必须更正的一条（此前简报有误）

> 早期板块② 任务简报写「VideoClaw（含其'一致性检查'实现 + **非标准许可正文**）」——**此描述错误**。VideoClaw 实为 **MIT**（宽松），ViMax 亦 MIT。开源侧**无"非标准许可"阻碍**；我们的"非标准许可"风险只在 fal 3DREAL LoRA（见 E-08）与 LTX-2.3 权重（见下）。特此更正。

### 1.4 自研是否重复造轮子？（决策）

| 维度 | 开源已有 | 我们是否重造 | 结论 |
|---|---|---|---|
| 写实化模型 | Wan VACE（Apache-2.0）/ LTX-2.3（开源权重） | 否，直接复用 | ✅ 不重造 |
| 多智能体编排 | ViMax（Director/Screenwriter/Producer/Generator） | 部分借鉴模式 | ✅ 借鉴不重造 |
| VLM 一致性质检门 | ViMax `best_image_selector` | 借鉴思路进 script_supervisor | ✅ 借鉴不重造 |
| **真 Z-pass / 相机内参喂入** | 开源用 Depth Anything 3 **估计**深度 | 我们用 Blender **真值** Z/Normal | ⭐ **我们的增量** |
| **Blender-blockout 确定性驱动** | Mickmumpitz 同理念（但 24GB 跑不动） | 我们做 12GB 可行的 VACE-1.3B 版 | ⭐ **我们的增量** |
| **47 项 QC 契约** | 无对应 | 我们自建 | ⭐ **我们的增量** |

→ **结论：不重复造轮子**。模型与编排模式皆开源可复用；我们的增值 = 真 Z-pass 替代估计深度 + 12GB 可行的本地白模链路 + 数值化 QC 契约。这正是板块①定位的"工程标准化 + 云端接口产品"护城河，而非"别人没有这个输入项"。

---

## 二、引擎供应方（comp-vendors-awards · 上半）

| 供应方 | 模型 | 许可 / 商用 | 关键规格 | 与白模路线关系 | 决策 |
|---|---|---|---|---|---|
| **fal** | LTX-2.3 + 3DREAL IC-LoRA | 端点 Commercial ✅；LoRA 条款未闭合 | 见板块②c（已一手核验） | **云主力** | ✅ 选 |
| **Lightricks** | LTX-2.3 (22B) | ⚠️ 许可冲突（见下） | 4K/50fps、原生音频(Mar 2026)、训练数据已授权（最强法务位）、依赖 Gemma-3-12B(Google 条款)；权重 46GB+、VRAM 24GB+ | 本地可跑但**超本机 12GB** | ⚠️ 条件选（换卡/云端才可行） |
| **字节** | Seedance 2.5（即梦） | 国内可用、需实名商用 | 白模插件 / CLI `dreamina multimodal2video` | 国内备选白模路径 | ⚠️ 条件选 |
| **阿里** | Wan 2.2 VACE | **Apache-2.0** | 吃 depth/pose 控制，本地 | **本地零成本路径**（R4） | ✅ 选（本地） |
| **MiniMax** | Hailuo 2.3 / H3 | 付费计划含商用权 | ~$0.08–0.56/video；H3 原生音频/omni、4–15s/2K | 非白模条件化 | ❌ 不作写实化主力 |
| **Tripo / Mirelo** | 3D 资产生成 | 各异 | 图/文→3D 资产 | 仅作**资产源**，非写实化 | ➖ 参考 |
| **Runway** | Gen-4.5 / Aleph | 订阅 | V2V、$0.28/s(Aleph) | **无白模条件化** | ❌ 排除（写实化） |

### ⚠️ LTX-2.3 许可冲突（须闭合）

二手源严重不一致：
- **说 Apache-2.0**：freeainews / digitalapplied / floyo / yfarmx（"Apache 2.0, free under $10m ARR"）。
- **说 LTX-2 Community License（Lightricks 自研，非 Apache）**：ltx23.app 详细逐条读——**年营收 ≥$10M 须企业授权**、衍生品继承同协议、须保留署名；并指出依赖 Gemma-3-12B（Google 条款）构成"第二份协议"。

→ 冲突判定：权威应以 **Lightricks 仓库内 LTX-2 Community License Agreement 原文** 为准（ltx23.app 的逐条读更可信；yfarmx 的"Apache 2.0"大概率混淆了 LTX-2 与更早 LTX-Video 的 Apache 许可）。**本清单 E-08 已记"LTX-2.3 权重 LTX-2 Community License，年营收 >$10M 需授权"——与详细读一致**。➡️ **待闭合：向 Lightricks 取许可证原文确认**（与 E-08 的 LoRA 条款闭合一并处理）。

---

## 三、获奖团队与公开复盘（comp-vendors-awards · 下半）

### 3.1 Runway AIFF 2025（一手/二手）

- 规模：**6,000+ 投稿**（2023 仅 ~300 → 2024 ~3,000 → 2025 6,000），Lincoln Center + 10 家 IMAX，奖金 $61.5k。
- 获奖：
  - **Grand Prix** Jacob Adler《Total Pixel Space》（9min 论文式，Runway+其他）
  - **Gold** Andrew Salter《JAILBIRD》
  - **Silver** Ricardo Villavicencio & Edward Saatchi《ONE》
  - **Honoree/Merit** Illya Dutsyk 等《Distance Between Two Points Of Me》、Herinarivo Rakotomanana《More Tears Than Harm》、Vallée Duhamel《Fragments Of Nowhere》、Hachi and IO《RŌHKI》、Simon Rieth《6000 Lies》、Riccardo Fusetti《Editorial》

### 3.2 趋势（对我们有利的独立验证）

- 🟢 **"音频设计是业余与专业作品的最大分水岭"**（AIFF 2025 复盘原文）——**独立验证板块①音频链投资的正确性**。
- 🟢 **"多工具工作流出最精致结果"** —— 验证我们"Blender+大模型"混合路线。
- 🟢 **"叙事片胜纯视觉实验" / "拥抱 AI 怪癖而非隐藏更真实"** —— 支持"大模型只执行不决定 + 人工叙事把控"。

### 3.3 反方证据（公开失败 / 保留态度）

- 🔴 **Coca-Cola AI 广告被批 "soulless"**：即便用可控的 Gen-4 参考工作流，仍须**大量人工筛选**（10,000 帧 / 5,000 段 → 选极少部分）——验证"可控模型也需重人工 QC"，支撑我们的 QC 层哲学。
- 🟡 **《Fragments Of Nowhere》被 Ars Technica 评"缺乏新意、与过往 AI 片雷同"** —— 提示纯视觉炫技易审美疲劳，需叙事/结构支撑（反方：光有写实化不够）。

---

## 四、板块②b 决策倾向汇总

| 项 | 倾向 | 理由 |
|---|---|---|
| 云主力 | ✅ fal 3DREAL | 已一手核验 schema，白模条件化唯一成熟 |
| 本地零成本 | ✅ Wan2.1-VACE-1.3B | Apache-2.0，R4 先跑通链路 |
| LTX-2.3 本地 | ⚠️ 条件选 | 权重/显存超本机 12GB，须换卡或云端 |
| 自研模型/编排 | ❌ 不重造 | 开源可复用，我们做集成+QC 增量 |
| 音频链 | ✅ 强化 | AIFF 趋势独立验证为专业分水岭 |
| Runway/Hailuo 写实化 | ❌ 排除 | 无 blockout 条件化 |
| LTX-2.3 许可 | ❓ 待闭合 | 二手源冲突，须取 Lightricks 原文 |

**待老板拍 / 待闭合**：① LTX-2.3 许可原文确认 ② fal 3DREAL LoRA 商用条款（E-08）③ 本机 12GB 下本地路径锁定 Wan2.1-VACE-1.3B（不碰 LTX 本地）。
