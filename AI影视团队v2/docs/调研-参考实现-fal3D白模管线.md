# 调研 · 头号参考实现 —— fal《From clay 3D render to a real action short》

> 原文：`blog.fal.ai/from-clay-3d-render-to-a-real-action-short-a-3d-to-ai-pipeline-with-total-control/`（2026-07-13，**一手**）
> 定位：**目前与我们路线完全同构、且信息密度最高的单一竞品文档** → 升格为本项目**头号参考文档**，R3 架构定稿必须逐条对照。
> 核验：`comp-commercial` 逐字核验（第 7 版勘误）

---

## 1. ⭐ 宽高比陷阱 —— 原文机制比转述**更狠**

原文逐字：
> "**The aspect-ratio trap** cost us a full generation round: 16:9 references quietly overrode the 2.39:1 clay frame. **Crop your refs.**"
> "the edit model **matches the MAJORITY aspect of its inputs** — widescreen refs + one clay frame = **recomposed 16:9 output**."

**机制不是"参考图被改成 16:9"，而是模型按输入的「多数宽高比」投票** —— 多张宽银幕参考 + 一张白模帧 → **输出被整体重构成 16:9**。

→ **必须写进质检校验清单**：
1. **所有参考图的宽高比必须裁成与白模帧完全一致**；
2. **数量上不能让宽银幕参考占多数**（少数服从多数，不是"有白模就以白模为准"）。

---

## 2. ✅ 护城河判断：从二手**升级为一手**

原文逐字：
> "**3DREAL is an in-context LoRA** … the model receives **the CG clip itself as a dense conditioning stream (motion, layout, camera)** plus **one keyframe as the appearance anchor**."
> "`video_url` drives motion, `image_url` drives look"

→ **一手确认 fal 吃的是「RGB clay 视频 + 一张关键帧」，全文未出现 `depth` / `normal` / 通道类输入。**
→ 因此护城河表述（"fal 占的是云端**收 RGB 白模**位，不是收 depth 位"）**由二手升为一手**，可以放心用。

---

## 3. ✅ `8k+1` 规则：首次拿到**一手原文**

> "`num_frames` must satisfy **8k+1** …: **the temporal autoencoder compresses time by a factor of 8, plus one anchor frame**. Cut your clay clips to these lengths from the start."

→ 此前那条更正（`8k+1` 属 LTX/fal、`4n+1` 属 WAN）**得到一手确认**。
⚠️ **但原文举例写作 "17, 33, 41, 81, 97…"，间距不规律**（疑为示意或笔误）→ **合法集合仍以数学定义 `8k+1` 为准**（9, 17, 25, 33, 41, 49, 57, 65, 73, 81, 89, 97, …）。

---

## 4. ⭐ 失败率一手数据点（对成本模型重要）

> "the full run was **33 validated keyframes × 4 seeds = 132 videos, generated with zero failed jobs**"

→ **fal 3DREAL 在这条真实管线里 0 失败 / 132 次**。
→ **成本模型要改**：fal 的证据等级从"**失败率未知**"改为"**一手实测 0/132**（⚠️ 单项目样本，非统计样本，不可当 SLA 用）"。
→ **并且不可把可灵的 30–40% 失败率外推到 fal** —— 两家证据等级与量级都不同。但"**按有效成本报价**"这条总纪律仍成立。

---

## 5. ⭐ 他们的工程做法（**可直接抄**）

| 做法 | 原文 | 我们的落点 |
|---|---|---|
| **Agent 驱动 Blender** | 用 **Blender MCP** 由 Agent 建场景（**含自建 ray-cast 守卫**） | ⚠️ 本机 Blender 5.2.2 正在社区 MCP 的断裂区间 → 我们自建/走 bpy 直调，但**"Agent 驱动 + 自建守卫"这个形态照抄** |
| **每镜 20–40 个候选** | "**Volume is a feature.** With 20-40 candidates per shot, the perfect draw exists; your job becomes **selection**" | ⭐ **写进 `realizer` 岗位卡**：抽卡数量是特性，不是浪费；人的工作是"选"不是"抽" |
| **用叠加图评审，不靠感觉** | "**Verify with overlays, not vibes.** If edges double in the 50% blend, **the perspective drifted** — and the video model will faithfully animate that drift later." | ⭐ **写进 `script_supervisor` 质检工具**：**50% overlay 叠加 + 看边缘是否重影** = 便宜的透视漂移检测 |
| **200+ 候选 → 33 定稿** | 200+ 关键帧候选用 overlay 评审后定 33 个 | 与我们 `qc_rubric` 的"多帧投票 + 人工抽检"一致 |
| ⚠️ **`ffmpeg` 循环里的静默 bug** | 一个 **ffmpeg-in-a-loop bug 静默毁掉 3 个镜头首帧** | ⚠️ **教训：ffmpeg 在循环里必须加 `-nostdin`**（否则会吞掉 stdin 导致静默失败） |

---

## 6. ✅ cap 条款：**已定位到一手出处，恢复为可用**（本轮由 ❓ 恢复）

**经过一轮双向核验，结论是「引错页面」而不是「条款不存在」** —— 数字本身没错，出处是 **fal API Schema 页**（`fal.ai/models/fal-ai/ltx-2.3-quality/render-to-real` 的 `/api` 标签页），**一手**。
而且**同一个 cap 在 `resolution` 与 `num_frames` 两个字段里各写了一遍**（冗余表述，不像笔误）：

> **`resolution` 字段**："**The IC-LoRA control path caps the resolution × frames volume**, so resolution trades against duration: **720p allows up to ~6s (sharper), 480p up to ~15s (softer but longer)**. A request above the budget is rejected with a clear error."
>
> **`num_frames` 字段**："**The IC-LoRA control budget caps the resolution × frames volume: roughly 6s at 720p or 15s at 480p; a request above it returns a 422.**"

### 6.1 恢复后的结论（含限定）

| 项 | 内容 |
|---|---|
| 该 cap | ✅ **一手**，恢复使用 |
| ⚠️ 限定 | 官方用词是 "**roughly**" → **基数本身模糊**，4.4s 只能标为"**指示值**" |
| ✅ **`720p + 宽银幕` 双重代价** | **恢复进排期表**：成本 **+34%** ／ 时长 **−27%**（约 4.4s） |
| 方向性结论 | ✅ **逻辑必然、不依赖精确基数**：cap 是**乘积**（原文用词 "volume"）→ **宽银幕必然吃掉时长预算** |

### 6.2 责任与教训（写入证据纪律）

**这次的错误是"给了引文却没给页面"** —— 在"每个结论必须带来源 URL"的纪律下，这不该发生。
→ **规范补充**：**引用必须精确到「页面 + 字段/章节」**，不能只写"官方文档"或"某博客"。**同一个产品里，API Schema 页 与 博客 的内容是不一致的**——本次就栽在这里。

### 6.3 ⭐ 宽高比机制的精修（比原文转述更可执行）

fal 原文：**"the edit model matches the MAJORITY aspect of its inputs — widescreen refs + one clay frame = recomposed 16:9 output"**。

→ **校验规则升级为**：**clay 帧的宽高比必须在全部输入中占多数**（最稳做法：**把全部参考都裁成 clay 的宽高比**）。

⚠️ **反直觉风险（这条以前没意识到）**：
**参考图加多了，反而可能把比例投错** —— 为了"风格更准"而多加几张 16:9 参考，会把 2.39:1 的 clay 投成 16:9。
→ **"多加参考"存在隐藏上限**：**参考图不是越多越好，宽高比一致性优先于数量**。

---

## 7. ⭐ 三条施工级送检项（来自 fal 一手复盘）

| # | 送检项 | 为什么对我们**尤其**重要 |
|---|---|---|
| 1 | **ffmpeg 一律加 `-nostdin`** | fal 因缺此参数**静默毁掉 3 个镜头的首帧**。**我们正踩同一条路径**——本机 Blender 5.2.2 无 FFMPEG 编码器，我们被迫走"**PNG 序列 + 外部 ffmpeg**" |
| 2 | **每次合成都做 50% overlay 自检** | 原话 "**Verify with overlays, not vibes.** If edges double in the 50% blend, **the perspective drifted**" → 便宜的透视漂移检测 |
| 3 | **首次联调只用官方演示过的帧数：`17 / 33 / 41 / 81 / 97 / 121`** | 原文举例**刻意跳过 25 / 49 / 57 / 65 / 73 / 89**。**用未演示值出问题时，你无法区分是"帧数取值问题"还是"模型问题"** → 基线跑通后再放开全部 `8k+1` |

---

## 8. 一处仍是"未提及 ≠ 不支持"

原文**未提及相机内参处理**（只讨论相机运动、绑定、手持抖动噪声）。
→ 与"fal 不携带内参"的判断**一致**，但**仍是"该文未提"，不等于平台不支持** → 标 ❓。

---

## 9. 待补验清单

| 项 | 状态 |
|---|---|
| fal 是否支持/携带相机内参输入 | ❓ 该文未提，≠ 不支持 |
| `8k+1` 举例间距不规律是笔误还是另有约束 | ❓ 以数学定义为准备用 |
| `enable_detail_refine` / `detail_refine_strength` 默认值的一手原文 | 🔵 已请 `comp-commercial` 核 API Schema 页 |

---

# 10. 引擎参数与风险精修（勘误第 9 版收敛，**以本节为准**）

> 来源：`comp-commercial` 第 9 版（`research-engine-blender` 复核出两处语义错误后更正）。**其中两条是撤回性质的更正，且第一条原本被标为"最重要"，会给排期带来实质误导。**

## 10.1 🔴 撤回：**fps 是「回放速率杠杆」，不是「时长杠杆」**

| | 内容 |
|---|---|
| **错误表述（已撤回）** | "调低 fps 可在同一帧预算内延长时长——720p 用 ~144 帧，24fps≈6s，**12fps≈12s，成本相同**" |
| **正确口径** | 成本（`$ ∝ 宽×高×帧数`）与 cap（`resolution × frames`）**都只基于帧数，与 fps 完全无关**。**帧数才是内容/信息量的上限，fps 只是回放速率。** |
| **后果** | 144 帧 @12fps **不是"12 秒的故事"，而是把同一段 6 秒的动作放慢 2 倍（慢动作）**。要真正讲 12 秒叙事需约 **288 帧** → **成本翻倍且远超 cap → 做不到** |

**正确表述**：
> **fps 是「回放速率」杠杆，可以免费做慢动作；不是「时长杠杆」。延长叙事仍必须增加帧数、因而增加成本。**

- 慢动作确有运镜价值，可作**实验项**；但"运动是被**重新生成为更慢**"还是"仅按 12fps **慢放**"，取决于 LTX-2.3 是否 fps-conditioned → **❓ 未能验证**
- ⭐ **新增施工纪律**：**白模视频与输出 fps 必须保持一致（默认 24）**；把 fps 当**受控变量单独实验**，**不要在联调阶段混用**（否则无法归因）
- ⚠️ **对排期的影响**：若误用旧结论，会同时导致**排期与报价双重误判**——**以本节为准**

## 10.2 🔴 设计级更正：**基线配置应为「不传 `image_url`」**

schema 原文：`image_url` 是**可选**的，且只是"**frame 0** 的锚（image-to-video anchor）"，"**leave empty to let the render alone drive the result**"。

→ ⭐ **不传参考图时，输入只有白模视频一个 → "宽高比多数投票陷阱"根本不存在**（只有一个输入，无"多数"可言）。

| 配置 | 宽高比风险 | 额外成本 | 外观可控性 |
|---|---|---|---|
| **不传 `image_url`（基线）** | **无**（仅 1 个输入） | 无 | 低 |
| 传 `image_url`（受控增强） | **有**（多数投票） | 无 | 高 |

→ **口径更正**：宽高比多数原则**不是默认风险**，应改标为「**仅在启用参考图增强时引入的风险**」。（此前写成通用风险项，**口径过宽**。）

## 10.3 🟡 两条新增风险项

| # | 项 | 内容 | 处置 |
|---|---|---|---|
| 1 | **`enable_safety_checker` 默认 `true`** | **默认开启的内容审核**。我们动作/冲突类题材**可能被默认拦截，必须实测确认是否误杀** | ⚠️ **合规红线**：若确认受限，**走平台正规途径询问条款与可用范围**。**不提供、也不采用任何规避审核的做法** |
| 2 | **`video_quality` 默认 `high`**（low/medium/high/maximum） | **它是否影响计价或可用时长 ❓待核实** | **核实前不要假设它免费** |

## 10.4 🟡 锚点精度修正（覆盖此前两个数）

| 档位 | 旧值（作废） | **新值** | 理由 |
|---|---|---|---|
| **480p 档上限** | ~~361 帧~~ | **353 帧（14.71s）** | 361/24 = **15.042s 略超**官方 "~15s"，属**边界值、有 422 风险**；**353 = 8×44+1**，稳在 "~15s" 内 |
| **720p 实用上限** | ~~121 帧（当上限）~~ | **约 137 帧（5.71s）** | 由官方 "~6s" 与 `8k+1` 共同推出 |
| **720p 推荐默认** | 121 帧 | **121 帧（5.042s）** ✅ **仍安全，继续作为推荐默认** | — |

**另**：**`num_frames` 上限（481）与 cap 是两道独立约束，取更严者**。
（481 帧仅在低像素/窄画幅如 480p 1:1 下可达；**720p 16:9 的 481 帧 ≈443 MP 必 422**。）

## 10.5 ✅ 其余采纳项

| 项 | 采纳后的口径 |
|---|---|
| **`intensity` 分阶段** | **联调用 `light`（保结构）→ 结构验收通过 → 终稿用 `strong-v2`**（与 fal 博客终稿设定一致）。**不再写成二选一** |
| **`3DREAL` 前缀** | ⭐ **我方模板不要自己写 "3DREAL"**（避免重复前缀）；**复核 output 回传的最终 prompt** 作为**免费的正确性自检** |
| **`enable_prompt_expansion`** | 保持默认 **`false`** |
| **"Output size follows the source video"（第三重证据）** | → 推论：**白模宽高比必须在 Blender 阶段定死** —— 这正是我们"**结构在 Blender 定死**"前提的**正向验证** |

## 10.6 商业侧清单最终版（11 项，`comp-commercial` 定稿）

**报价项**
1. 单镜成本 = `0.0024075 × 宽 × 高 × 帧数 / 1e6`，**向上取整到整数 MP**（取整税 < 1 MP ≈ < $0.0024，**与分辨率无关**）
2. **按「每镜宽高比」计价**（2.39:1 比 16:9 贵约 **34–39%**）
3. **`detail_refine` 单列开关**（开 = 单镜 **×4** + 多阶段耗时 + **结构漂移风险**，**仅终稿开**）
4. ⛔ **不承诺连续秒数**，用 `8k+1` 帧档枚举（推荐 **121 帧**；480p 上限 **353 帧**；720p 上限 **~137 帧**）
5. ⭐ **fps 是回放速率不是时长杠杆**；白模与输出 fps 必须一致且**单独实验**
6. **成本必须含重试倍数**（fal 一手 **0 失败/132**，但**单次项目非统计样本**；可灵 **30–40% → ×1.54–1.67**）

**交付 / 版权项**

7. ⭐ **基线不传参考图**；**启用参考图增强时**才受"clay 宽高比占多数"约束，且**"多加参考图"有隐藏上限**
8. 必带 `3DREAL` 前缀（由端点保证），并**复核回传 prompt**
9. ⚠️ **`enable_safety_checker` 默认 true → 合规实测项，走正规途径咨询，不做规避**
10. **`video_quality` 默认 high → 是否计价 ❓待核实**
11. **商用许可**：fal 端点 **Commercial use ✅ 一手**；但 **LTX-2.3 权重 > $10M 营收需授权**、**fal LoRA 条款未附正文 → ❓待商务书面确认**
