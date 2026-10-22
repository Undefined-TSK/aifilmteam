# R1 调研报告：Blender 白模粗片 → 大模型写实化 路线

- 调研员：技术调研员（AI 影视团队 / 任务 A）
- 日期：2026-09-27
- 目标路线：Blender 极简白模占位（相机/灯光/动作/时间轴全定死并渲染粗片）→ 大模型后期把白模粗片写实化成片（大模型只做执行不做决定）
- 目标硬件：Windows 笔记本 / RTX 5070 Laptop 12GB / 约 15GB 可用内存 / 成本敏感 / 偏好免费开源本地部署

> **取证原则声明**：本报告结论优先来自一手页面（GitHub README / SKILL.md / 官方 API 文档 / 官方博客）。凡官方页面为 JS 渲染、无法抓取正文，或仅有第三方转载页的，均已在对应位置显式标注「未能验证」及原因。所有英文引用为照抄原文。

---

## ① 调研总结

### 任务 1｜7 个现成方案逐项核实

#### 1. Kovname/nano-banana-render（Nanode / Omni Engine）

来源：https://github.com/Kovname/nano-banana-render （README + Releases，抓取于 2026-09-27）

| 问题 | 结论 | 原文关键句（照抄） |
|---|---|---|
| (a) 管线步骤 | Blender 里做 blockout/Eevee/Workbench → 导出运动引导视频 → 上传给 Google Gemini Omni Flash / Veo 3.1 → 结果回灌到当前场景 Video Sequencer | "**Omni Engine** renders a rough Blender animation into a finished 720p video while preserving camera motion, timing, subject movement, geometry, and composition."；"Capture the active animation using Eevee or Workbench." / "Upload the motion guide as a single video with the selected `16:9` or `9:16` camera." |
| (b) 保留相机运动与时序 | **是（明确宣称）** | "Re-render motion, camera, timing, and scene structure with AI-generated shading."；"Edit with a text prompt while preserving duration, motion, camera path, and identity." |
| (c) 首帧图锚定外观 | **是** | "Start from text, an image, reference images, or supported first/last frames."；"**Style Reference for video** transfers rendering medium, materials, lighting, palette, texture treatment, and color grade without copying objects from the reference." |
| (d) license 全称 | **GNU General Public License v3.0（GPL-3.0）** | "Nanode AI Render Engine is open-source software licensed under [GPL-3.0]." |
| (e) 脚本化/自动化 | **仅 GUI 插件**（Blender 原生 render engine + 侧栏面板）。README 未提供任何 CLI/API/headless 批量入口；仅提到可切「Personal Google API mode」。判定：**需适配（自建脚本包装）** | "It works as native Blender render engines and editor panels, so generated media stays inside the scene, Render History, Image Editor, and Video Sequencer." |
| (f) 依赖国内不可直连云 | **是**。核心模型为 Google `gemini-*` 与 `veo-3.1-*`，走 Google API；另有 Nanode 自身 credits。国内不可直连 Google | "Nanode name Google model … `gemini-3.1-flash-image` … `Veo 3.1 Lite, Fast, and Standard`"；"Personal Google API mode bypasses Nanode credits." |

补充：v2.8.0「video generation workflows」发布于 2026-07-24；项目自述由 Google Cloud for Startups 支持（"Nanode is supported by the **Google Cloud for Startups** program."）——即其开源插件背后仍依赖 Google 云。

---

#### 2. Yi-111-a/blender-shot-video（Claude Code skill）

来源：https://github.com/Yi-111-a/blender-shot-video 及 https://raw.githubusercontent.com/Yi-111-a/blender-shot-video/main/SKILL.md

| 问题 | 结论 | 原文关键句（照抄） |
|---|---|---|
| (a) 管线步骤 | 6 步：①文本→三段式脚本/镜头规格 ②风格确认闸 ③首帧图 ④Blender 灰白模 previs ⑤生成成片 ⑥对比合成 | "① breakdown (free) → 3-section script … ② style gate (ASK) … ③ first frame (PAID*) → 1 establishing image … ④ white-model (free) → Blender gray previs with the planned camera move ⑤ generate (PAID) → final video = first frame + white-model previs + prompt ⑥ comparison (free)" |
| (b) 保留相机运动与时序 | **是**。白模 previs 就是相机/运动/空间引导；支持三种运镜模式（简单/多段关键帧/跟随运动主体） | "the **white-model previs** (camera + motion + spatial guide)"；"**Multi-phase** — `camera.keyframes`"；"**Follow a moving subject** — set top-level `cameraFollow`" |
| (c) 首帧图锚定外观 | **是（核心设计）** | "**The core idea:** ④ gives the model three things at ⑤ — the **first frame** (look anchor), the **white-model previs** (camera + motion + spatial guide), and a **director-shot prompt**." |
| (d) license 全称 | **未声明许可**。仓库无 LICENSE 文件（GitHub API 返回 `"license": null`）。据此默认保留全部权利，商用需另行确认 | 未能验证：GitHub API `https://api.github.com/repos/Yi-111-a/blender-shot-video` 返回 `"license": null`；仓库文件列表仅含 examples/references/scripts/README/SKILL.md，无 LICENSE |
| (e) 脚本化/自动化 | **是**。提供 4 个 CLI 脚本，且白模步骤可 headless 调 Blender | "`blender -b -P scripts/build_whitemodel.py -- --shot-spec shot.json --output previs.mp4`"；"`python scripts/generate_video.py --first-frame ff.jpg --previs previs.mp4 --prompt \"<videoPrompt>\" --out final.mp4 --duration 10 --ratio 16:9`" |
| (f) 依赖国内不可直连云 | **默认不依赖**。捆绑适配器是火山方舟/Seedance（Volcengine Ark，国内可直连），且整体 model-agnostic；但其 Ark 视频适配器要用 cloudflared 把本地文件变成公网 URL，需外网可达 | "a Volcengine Ark / Seedance implementation is bundled as a reference; swap in any provider"；"Many video models fetch **public URLs** and cannot reach `localhost`; the bundled `generate_video.py` solves this with a temporary cloudflared tunnel" |

补充（关键设计约束，值得抄作业）：硬性规则要求"白模是代理，不许模型复现灰模材质"、"付费前必须人工确认"。原文：
- "**White model is a proxy** — the ⑤ prompt must tell the model NOT to reproduce the gray/low-poly/block look; each shape only marks a subject's position/orientation."
- "**Review the white-model before paying** for ⑤ (mandatory gate)."
- "Keep camera moves **gentle** (slow push-in / pan / slight rise). Avoid fast 360° orbits and whip moves — they cause limb/neck flips at the model layer."

---

#### 3. RonaldXDZ/blender-video-workflows（**注意：该 URL 已 404，实际仓库名带后缀**）

来源：任务给定的 `https://github.com/RonaldXDZ/blender-video-workflows` **返回 404（Page not found）**。经查该用户的公开仓库列表，实际存在的是 fork 版：**https://github.com/RonaldXDZ/blender-video-workflows-blender-**（MIT，fork，1 star，2026-09-20 建立）

| 问题 | 结论 | 原文关键句（照抄） |
|---|---|---|
| (a) 管线步骤 | 两套 Codex skills，均为「3D 灰白模动画 → 提示词 → 视频模型生成」：`blender-video-recreate`（复刻参考视频）与 `blender-video-original`（文字原创） | "两套中文 Codex skills：参考视频复刻与文字创意原创。均采用「3D 灰白模动画 → 提示词 → 视频模型生成」流程。" |
| (b) 保留相机运动与时序 | **是（宣称复刻动作与运镜）**，但作者自己声明未做端到端实测 | "复刻我上传视频的动作与运镜，先做灰白模，再生成写实科幻视频。"；"结构验证通过不等于所有外部工具组合均通过端到端实测，具体状态见 VALIDATION.md。"；"未取得链接文章完整正文，不宣称逐条还原作者教程" |
| (c) 首帧图锚定外观 | **未明确**。流程以「白模 + 提示词」为主，README 未声明首帧锚定 | 未能验证：README 未出现 first frame / 首帧 锚定外观的表述 |
| (d) license 全称 | **MIT License** | "本仓库原创 skill 文档以 MIT 许可发布，见 LICENSE。" |
| (e) 脚本化/自动化 | **是**。Codex skill，可用 Computer Use 或 Blender Python 批处理 | "需要可用的 Blender 与控制方式；界面操作需 Computer Use 权限，批处理可使用 Blender Python。视频探测和转码可使用 FFmpeg/ffprobe 或等效工具。" |
| (f) 依赖国内不可直连云 | **未指定**。最终风格化依赖"支持相应输入的视频生成服务和用户授权"，未点名 provider；因此无法判定是否依赖不可直连云 | "最终风格化需要支持相应输入的视频生成服务和用户授权，可能产生服务费用。未配置服务时交付白模、工程和提示词，不能假称完成生成。" |

补充：交付物清单为"镜头表、.blend、白模 MP4、提示词、验收记录"。原文："每次运行交付镜头表、.blend、白模 MP4、提示词、验收记录，以及服务可用时的生成视频。"

---

#### 4. 即梦 Seedance 官方 Blender/Maya 插件（白模视频渲染插件）

来源：
- 官方入口页 https://jimeng.jianying.com/ （左侧「工具」→「白模视频渲染插件」）
- 官方发布稿转载：https://www.readaitime.com/zh-hant/news/2026-08-05/elgo54fm ；https://it.sohu.com/a/1057206660_100111246
- 官方插件安装教程（第三方实录，含插件界面截图）：CSDN/公众号长文（URL 未能验证，见下）

| 问题 | 结论 | 原文关键句（照抄） |
|---|---|---|
| (a) 管线步骤 | Blender/Maya 中搭白模并设机位/走位 → 插件内选「相机渲染」或「本地上传」导出白模视频 → 点「上传至即梦生成」→ Seedance 2.5 渲染材质/光影/氛围 | "在 Maya 或 Blender 中敲定镜头空间、人物站位和场景结构（即 3D 白模预演），然后一键调起 Seedance 2.5 完成材质渲染、光影细节和氛围填充。"（来源：https://www.aitop100.cn/infomation/details/34403.html） |
| (b) 保留相机运动与时序 | **是（官方口径为"结构约束"）** | 官方稿："白模参考…使模型能更好地理解创作意图"；"白模里的几何体位置、透视关系、运动轨迹全部被模型当作硬约束来遵守"（第三方评测，见 CSDN 转载，非官方原文，标注为存疑） |
| (c) 首帧图锚定外观 | **白模视频作为"参考视频"输入**；官方同时支持首尾帧（图生视频）。二者属不同模式（见任务 2 互斥规则） | 官方插件界面文案："视频上传方式：本地上传 / 相机渲染"，"并把渲染好的白模视频作为参考视频输入"（第三方实录截图） |
| (d) license 全称 | **闭源商业产品，无开源许可** | 未能验证：官方无 license 声明；插件以 .zip/.atp 形式分发，仅限 Blender 5.1+ / Maya 使用 |
| (e) 脚本化/自动化 | **仅 GUI 插件**（Blender Add-on + Maya plugin，版本号 0.1.0 / 0.5.0）。生成动作是"上传至即梦生成"按钮，走即梦 Web，无公开 CLI/API 注入白模轨道 | 未能验证：未找到官方 CLI/API 文档；插件只做「相机渲染导出 + 上传」 |
| (f) 依赖国内不可直连云 | **否**。即梦（jimeng.jianying.com）与火山方舟 Seedance 均为国内可直连服务 | "即梦 Seedance2.5 还新增了白模参考、绿幕编辑等能力"；"即梦AI同步上线了Maya / Blender 插件" |

补充（官方/口碑约束，均来自第三方实录，标注为**待官方文档确认**）：单条白模参考视频最大 200M、单段最多 72 帧（第三方博客称"最大支持720帧/200M"文案不一致，需以插件为准）。

---

#### 5. Higgsfield for Blender + Higgsfield Bridge / MCP

来源：
- https://higgsfield.ai/blog/higgsfield-blender-plugin （官方博客）
- https://higgsfield.ai/creator-hub/help-center/integrations/external-integrations-higgsfield （官方帮助中心）
- https://higgsfield.ai/blog/higgsfield-3d-jutsu （官方博客，3D Jutsu 白模/预演工作流）

| 问题 | 结论 | 原文关键句（照抄） |
|---|---|---|
| (a) 管线步骤 | 插件 7 个 tab：Scene Builder / 3D Model / Character Animation / Image / Video / Camera / Asset。3D Jutsu 工作流：prompt 生成灰模场景 → Export 渲染 previz 视频 → 生成角色/场景参考图 → 在同一 chat 里合成 → 出片 | "The bar covers seven tabs: Scene Builder, 3D Model, Character Animation, Image, Video, Camera, and Asset."；"**Step 1:** Block the previz … builds the scene in grey proxies … **Step 2:** Render the previz … **Step 4:** Combine in the same chat … The previz provides a reference for the intended camera path, framing, and character behavior" |
| (b) 保留相机运动与时序 | **是**。3D Jutsu 用 camera trajectory 控制镜头，previz 渲染作为相机路径/构图/表演的参考 | "Animation — A timeline with a playhead; motion comes from a camera trajectory, an animated character, or a GLB file imported with its animation"；"Camera work — Camera presets and trajectory editing frame the shot" |
| (c) 首帧图锚定外观 | **是**（角色身份来自 Soul 2.0 肖像、场景来自 Soul Cinema，作为参考注入） | "The character comes from Soul 2.0: a portrait that carries the identity and the wardrobe. The location comes from Soul Cinema: an empty subway car interior." |
| (d) license 全称 | **闭源商业**。依据其 Terms of Use：不主张用户输入/输出所有权、不限制商用，但标准账户内容可能被用于训练模型 | "the company does not claim ownership of user inputs or outputs and does not restrict commercial use of generated outputs."；"standard user content, including inputs and outputs, may be used to improve and train Higgsfield models."（来源：https://digitalproduction.com/2026/09/23/higgsfield-brings-ai-generation-into-blender-oh-goodey/ 与官方 ToU） |
| (e) 脚本化/自动化 | **是（Agent 级）**。提供 Higgsfield Bridge（MCP）让 agent 直接操作当前打开的 Blender 场景 | "Higgsfield Bridge connects an AI agent to the installed add-on, so the agent works in the scene that's currently open instead of only generating assets."；"The documented endpoint is https://bridge.higgsfield.ai/mcp" |
| (f) 依赖国内不可直连云 | **是**。云推理在 Higgsfield 服务器（higgsfield.ai），需直连外网 | "Generation runs in the cloud, so a powerful GPU is not required"；"AI generation runs in the cloud" |

补充（版本/成本约束）：
- 环境："**Requirements:** Blender 5.1 or later, on Windows or macOS."（帮助中心另有版本 4.2–5.1 说法，与博客"5.1+"存在不一致，标注为**待官方确认**）
- 计费："The number on the Generate button is the credit price, visible before you press it"；"Unlimited access and free generations apply only on higgsfield.ai."
- 一个完整白模→成片案例（官方博客给出完整 prompt，8 秒 / 16:9 / 单镜 360° 环绕）：见 https://higgsfield.ai/blog/higgsfield-3d-jutsu

---

#### 6. tin2tin/Pallaidium

来源：https://github.com/tin2tin/Pallaidium （README + LICENSE.txt）

| 问题 | 结论 | 原文关键句（照抄） |
|---|---|---|
| (a) 管线步骤 | Blender VSE 内：选 Output(Image/Video/Audio/Text) → 选模型 → 设 Input(Prompts 或 Strips) → 配参数 → Generate / Generate from Strips | "If using `Prompts`, click the **`Generate`** button. If using `Strips`, click the **`Generate from Strips`** button." |
| (b) 保留相机运动与时序 | **部分**。以 ControlNet / control_video 驱动结构，多时间点锚定（N-Anchor / FLF），但 README **未明文承诺"精确保留源片相机运动"** | "the active input strip drives control_video"；"LTX-2.3 N-Anchor mode — place 3+ Image strips in a Meta strip to pin video generation at multiple time points."；"Pre-trim every temp audio/scene/video render … to the model's required 8n+1 frame count" |
| (c) 首帧图锚定外观 | **是** | "a separate reference image supplies the frame-0 appearance condition (video_url + image_url)."；"**LTX-2.3 3DREAL — video + reference image control.** With Output: Video, the active input strip is rendered to a trimmed clip and used as the IC-LoRA `control_video`, while the **Ref Strip** dropdown (now accepts an IMAGE) supplies the frame-0 appearance reference" |
| (d) license 全称 | **GNU General Public License v3（GPLv3）**（LICENSE.txt 正文："GNU GENERAL PUBLIC LICENSE / Version 3, 29 June 2007"）。**注意：模型权重不含在内，各自许可** | "Pallaidium does not include any genAI models(weights). If the user decides to use a model, it is downloaded from HuggingFace."；"In general, the models can only be used for non-commercial purposes and are meant for research purposes." |
| (e) 脚本化/自动化 | **是**。批处理 + Render Queue（异步批作业）+ MCP/Claude 集成 + 插件架构 | "call `generate_image()`, `generate_video()`, `generate_audio()`, etc. from Claude agents through the MCP server."；"Render Queue (async batch jobs)"；"Plugin architecture — models auto-discovered from `models_plugins/`." |
| (f) 依赖国内不可直连云 | **默认本地**，云端为可选（可接 fal.ai / MiniMax / Google，这些为境外云） | "Pallaidium runs models **locally** by default. Optionally, it can also drive an external generation server … This is entirely opt-in"；"**Model Source** — choose … **Local** (default)" |

补充（成本/体积约束）："5-30 GB must be downloaded first the first time any model is executed."

---

#### 7. fal.ai 博客「From clay 3D render to a real action short」

来源：https://blog.fal.ai/from-clay-3d-render-to-a-real-action-short-a-3d-to-ai-pipeline-with-total-control/ （作者 Lovis Odin，2026-07-13）

| 问题 | 结论 | 原文关键句（照抄） |
|---|---|---|
| (a) 管线步骤 | 4 阶段 3 条 prompt：P1 Blender 里由 AI（Fable/Claude via Blender MCP）搭灰模并动画 → P2 生成参考图 + 每镜关键帧 → P3 `fal-ai/ltx-2.3-quality/render-to-real` 出片 → P4 剪辑/音效/音乐/调色 | "this is not a one-prompt magic trick. The pipeline runs on *three* prompts — one per phase — with a human validation step between each."；"A 3D blockout owns the geometry — cameras, motion, timing, cuts."；"`render-to-real` owns the final pixels — powered by the **3DREAL LoRA for LTX 2.3**" |
| (b) 保留相机运动与时序 | **是（最强证据）**。`video_url` 喂 clay clip 驱动运动，相机 easing 在 f-curve 内 | "`video_url` drives motion, `image_url` drives look"；"All easing lives in the cameras, not the subjects."；"`render-to-real` is specialized in reproducing the exact motion of the render you feed it" |
| (c) 首帧图锚定外观 | **是**。关键帧作外观锚点，且用 contract 锁几何 | "image_url = the validated keyframe (look)"；"Image 1 is the ONLY source of truth for geometry and composition. Repaint surfaces only. Do not reframe, recenter or zoom." |
| (d) license 全称 | **基础模型 LTX-Video 代码为 Apache-2.0**；但**训练出的 3DREAL LoRA 在 HF 上标注为 `other`（未给具体许可，商用未明）**；`render-to-real` 托管端点属 fal 商业服务 | HF 模型卡：`License: other`；"the 3DREAL LoRA we trained for LTX 2.3 is on Hugging Face (Light and Strong variants)" |
| (e) 脚本化/自动化 | **是**。全程 prompt + API/MCP 驱动，脚本化执行（含 ~10 并发滚动窗口、job 状态落盘可恢复） | "Rolling window of ~10 concurrent jobs"；"Connect Blender MCP and the fal MCP server to the same agent"（fal.ai 另一页说明） |
| (f) 依赖国内不可直连云 | **是**。全程跑在 fal.ai（境外），关键帧用 fal 上的 Nano Banana Pro / Seedream / GPT Image 2 / FLUX.2 | 端点均为 `fal.ai/models/...`；"the hosted `render-to-real` endpoint already runs it." |

补充（规模/成本）：
- 实际成片：10 秒 / 12 镜 / 24fps / 2.39:1（1920×804）/ 720p 出（detail refine 后观感约 2K）；33 个验证关键帧 × 4 seed = 132 条视频，0 失败。
- **未披露任何具体金额**："the Reference-to-video 模型 remain expensive"（原文未给数字）。标注：**成本未披露**。

---

### 任务 2｜云引擎能力边界（官方 API 文档）

> 说明：Kling 官方开发者站点（`klingai.com` / `app.klingai.com`）为 **JS 单页渲染**，`WebFetch` 只能取到标题、取不到正文。因此 Kling 部分正文引用取自 (i) 同一官方 URL 的搜索索引片段、(ii) 阿里云百炼托管的可灵 API 官方文档 `help.aliyun.com`（官方合作方一手文档）。已逐条标注来源等级。

#### 2.1 可灵 Kling v3-omni（`kling-v3-omni`）

官方文档 URL：
- https://www.klingai.com/document-api/apiReference/model/OmniVideo
- https://www.klingai.com/document-api/api/video/3-0-omni/video-omni/legacy
- 阿里云托管镜像：https://help.aliyun.com/zh/model-studio/kling-video-generation-api-reference

| 子问题 | 结论 | 原文关键句（照抄）+ 来源 |
|---|---|---|
| 多图参考 feature 与 first_frame 能否同时用？ | **不能同时用（互斥）**。图像参考类型枚举为 `first_frame / last_frame / refer_image`；官方组合规则只允许 `feature`（特征参考视频）与 `refer`/`first_frame` 特定搭配，而不是 refer_image 与首尾帧并列 | 官方：`first_frame`:首帧图素材标识。 `last_frame`:尾帧图素材标识。 `refer_image`:元素参考图素材标识。 `feature_video`:特征参考视频素材标识。 `base_video`:待编辑视频素材标识。 `element`:主体素材标识。（klingai.com/document-api/apiReference/model/OmniVideo）<br>阿里云托管官方文档："传入 feature+first_frame 时:必须传入 1 个视频和 1 张首帧。"；"传入 feature+refer 时:必须传入 1 个视频,且参考图片与多图主体数量( element_list 的数组长度)之和不得超过 4。"（help.aliyun.com/zh/model-studio/kling-video-generation-api-reference）<br>ComfyUI 官方合作节点文档："end_frame … cannot be used at the same time as reference_images"；"reference_images — up to six additional references, and it's this or the end frame, not both."（comfy.icu/node/KlingOmniProFirstLastFrameNode） |
| 有无 audio 开关？ | **有**。存在音频生成开关（`generate_audio` / `sound`），且与"参考视频编辑"模式互斥 | "generate_audio - off by default, only on kling-v3-omni."（comfy.icu 官方合作节点）<br>"klingParams.generate_audio boolean true … **Cannot be combined with reference_video.**"；"generate_audio and reference_video are mutually exclusive — a request that sets both is rejected."（apiframe.ai/docs/videos/kling/kling-3-0-omni）<br>另一镜像参数名为 `sound`："\"sound\": \"on\""（docs.gmicloud.ai/model-quickstarts/video/kling-v3-omni）<br>视频编辑模式保留原声参数：`keep_original_sound`：yes 保留,no 不保留（官方 klingai.com 文档片段） |
| 其他限制 | 无参考视频+多图主体时图片+主体 ≤7；有参考视频时 ≤4；kling-video-o1 不支持 4K/音频/storyboard | "无参考视频+有参考视频时…不得超过7/不得超过4"（官方 klingai.com 文档片段）；"o1 pays for its budget pricing with hard limits: 10 seconds max, no 4K, no audio, no storyboards."（comfy.icu） |

未验证项：Kling 官方页正文因 JS 渲染无法整页抓取；上述"参考图与首尾帧互斥"的关系，官方原文我**只取到组合规则表**，未取到一句"refer_image 不可与 first_frame 同用"的官方直接措辞。标注为**高可信但非官方逐字**。

---

#### 2.2 MiniMax Hailuo H3 / Hailuo-02

官方文档 URL：
- H3（官方）：https://platform.minimax.io/docs/api-reference/video-generation-v2-h3-context-ir
- Hailuo-02 首尾帧（官方）：https://platform.minimax.io/docs/api-reference/video-generation-fl2v
- 官方指南镜像：https://minimax-cac98058.mintlify.dev/docs/guides/video-generation

| 子问题 | 结论 | 原文关键句（照抄）+ 来源 |
|---|---|---|
| H3：参考 role 与 first_frame/last_frame 是否互斥？ | **互斥，不可混用**。role 合法值：`first_frame` / `last_frame` / `reference_image` / `reference_video` / `reference_audio` | "Image-to-video and reference-to-video are mutually exclusive: if any reference_image / reference_video / reference_audio role appears in content, then first_frame / last_frame must not appear (and vice versa); the two cannot be mixed."（platform.minimax.io 官方 H3 文档）<br>"role: first_frame - first frame, at most 1 image；last_frame - last frame, at most 1 image；reference_image - reference image, at most 9 images"（官方 H3 文档）<br>"Reference audio cannot be used alone. Include at least one reference_image or reference_video."（官方 H3 文档） |
| H3：有无音频？ | **有，且为原生立体声，与画面同批生成**（H3 无独立 audio 布尔开关，输出即含音频） | "MiniMax also states that all H3 audio output is native stereo and that voice, sound effects and music are modelled jointly rather than as separate domains"（aiwiki 汇总官方表述）<br>"Image-to-video, first & last frame … Reference-to-video: text + any combination of reference images … reference videos … and reference audio"（官方 H3 文档） |
| Hailuo-02：参考 role 与首尾帧是否互斥？ | **Hailuo-02 无 role 机制**。仅 `image_urls`（首帧，1 张）+ `metadata.last_frame_image`（尾帧）；不存在 reference_image/role 参考模式，因此**无"互斥"问题——因为根本没有多图参考能力** | "image_urls string[] First frame image URL array. Not provided: text-to-video；1 image: image-to-video"；"last_frame_image string Last frame image URL for first-last-frame generation mode."（platform.minimax.io/docs/api-reference/video-generation-fl2v）<br>"this page is not for native audio, long-form assembly, video-to-video editing, or multi-image reference packs beyond one first frame plus an optional last frame."（apidot.ai/models/hailuo-02） |
| Hailuo-02：有无音频？ | **无原生音频**（文档无 audio 参数；有 15 条运镜指令） | "For MiniMax-Hailuo-02, you can use [commands] syntax for camera movement control. … Supported 15 camera commands: Truck/Pan/Push/Pedestal/Tilt/Zoom/Shake/Follow/Static"（官方 fl2v 文档）<br>"this page is not for native audio"（apidot.ai） |

补充：Hailuo-02 的**独立运镜指令**是这批云引擎里唯一有"结构化 camera 指令"的：`[Push in]`、`[Pan left, Pedestal up]`、`[Tracking shot]` 等（官方 fl2v 文档）。H3 则用自然语言 prompt 描述运镜。

---

#### 2.3 Seedance 2.0 / 2.5（火山方舟 / 即梦）

官方文档 URL：https://www.volcengine.com/docs/6285/1393047 （火山方舟「创建视频生成任务」）

| 子问题 | 结论 | 原文关键句（照抄）+ 来源 |
|---|---|---|
| role 合法取值有哪些？ | 图片 role：`first_frame` / `last_frame` / `reference_image`；视频 role：`reference_video`；音频 role：`reference_audio` | 官方："图生视频-首帧 字段 role 取值:需要传入 1 个 image_url 对象, role 为 first_frame 或不填。"；"图生视频-首尾帧 字段 role 取值:…首帧图片对应的 role 为 first_frame；尾帧图片对应的 role 为 last_frame"；"图生视频-参考图 字段 role 取值:必填,每张参考图对应的 role 均为 reference_image"（volcengine.com/docs/6285/1393047）<br>第三方镜像补全视频/音频 role："Only reference_video is currently supported in multimodal reference mode."；"Only reference_audio is currently supported"（docs.toapis.com/docs/en/api-reference/videos/seedance-2/generation） |
| 三组 role 是否互斥？ | **互斥，不可混用** | 官方："图生视频-首帧、图生视频-首尾帧、全模态参考生视频 (包括参考图、视频、音频)为 3 种互斥场景, 不可混用。"（volcengine.com/docs/6285/1393047）<br>官方补充："全模态参考生视频 可通过提示词指定参考图片作为首帧 / 尾帧,间接实现「首尾帧 + 全模态参考」效果。" |
| 有无独立 camera 字段？ | **无独立 camera 参数**。运镜靠 prompt 文本描述（含时间戳分段） | 官方文档参数表中未见 camera/运镜字段；仅见 role/duration/ratio/resolution 等。第三方镜像亦无 camera 字段："aspect_ratio … Options: 21:9 16:9 4:3 1:1 3:4 9:16 adaptive"，"prompt … We recommend clearly describing the scene, camera motion, subject action"（docs.toapis.com） |
| 音频 | 2.5 支持全模态参考含音频；是否可关存在**矛盾证据**（不同来源不一致） | 第三方镜像："audio_urls … Audio MUST be paired with at least one image or video reference."（glama.ai）；"generate_audio boolean default:true Whether to generate synced audio."（docs.toapis.com）<br>另一来源称 2.0 无音频开关："Audio: always on (music, narration, ambient). There is no audio toggle parameter for Seedance 2.0."（ChatCut-Inc/agent-plugin）<br>**未能验证**：官方文档未见 audio 参数条目，故"有无开关"以官方为准——**未验证** |

---

#### 2.4 Wan 2.6 / 2.7（阿里云百炼 DashScope）

官方文档 URL：
- 图生视频首帧（2.1–2.6）：https://help.aliyun.com/en/model-studio/legacy-image-to-video-api-reference/
- 参考生视频（2.6）：https://help.aliyun.com/zh/model-studio/legacy-wan-reference-to-video-api-reference
- Wan 2.7 图生视频（官方指南）：https://docs.qwencloud.com/developer-guides/video-generation/image-to-video

| 子问题 | 结论 | 原文关键句（照抄）+ 来源 |
|---|---|---|
| 有无独立 camera 参数？ | **无独立 camera 字段**。运镜写在 prompt 里；仅有 `shot_type`（multi/single）控制多镜切换 | 官方参数表未见 camera：图生视频请求体为 `input{prompt,img_url}` + `parameters{resolution,prompt_extend,duration,audio,shot_type}`（help.aliyun.com）<br>"shot_type (string, optional): Generate video in multi camera angles … Options: \"multi\", \"single\""（atlascloud.ai 镜像官方 schema）<br>官方示例把运镜写进 prompt："The camera slowly moves up from below the sea turtle."（docs.qwencloud.com） |
| i2v + audio 能力？ | **有**。`parameters.audio`（2.5 及以后支持声音）；Wan 2.7 用 `media[].type = driving_audio` 传驱动音频 | 官方："僅支持wan2.6-r2v-flash生成无声视频。當生成無聲視頻時,必須顯式設定 parameters.audio = false。"（help.aliyun.com 参考生视频 2.6）<br>官方示例："\"parameters\": { \"resolution\": \"720P\", \"prompt_extend\": true, \"duration\": 10, \"audio\": true, \"shot_type\":\"multi\" }"（qwencloud 官方 Wan2.6 i2v）<br>"Audio capabilities: Supports automatic dubbing or uploading audio to achieve audio-video sync. (Supported by wan2.5 and later)"；Wan 2.7 `media` 组合："First frame with audio: first_frame + driving_audio"（docs.qwencloud.com / docs.anyfast.ai 官方 schema 镜像） |
| 其它 | Wan 2.7 支持首帧+尾帧、视频续写（first_clip）；Wan 2.6 及更早仅首帧 | "Wan 2.7 - image-to-video supports first-frame-to-video, first-and-last-frame-to-video, and video continuation. We recommend this version. The image-to-video (based on first frame) feature for Wan 2.6 and earlier models supports only first-frame-to-video."（help.aliyun.com） |

> **命名提醒（按要求）**：本次核实的是 **Wan 2.6 / 2.7**；不存在"Wan 3.0"这一版本。Wan 2.1/2.2 为 Apache-2.0 开源权重，**Wan 2.5/2.6 为 API-only，未开源**。原文："Wan 2.1 and 2.2 are open under Apache 2.0. … Wan 2.6 hasn't followed that pattern … Access runs through Alibaba Cloud's Model Studio"（bytewaves.news 评测；此为二手，标注为**待官方确认**）。

---

### 任务 3｜真实案例（白模 / 3D previs → AI 写实化 成片）

| 主体 | 是否有白模→写实化成片 | 产出形态（时长/分辨率） | 是否公开管线 | 成本披露 | 授权说明 | 来源 URL |
|---|---|---|---|---|---|---|
| **即梦 Seedance** | **是**。有官方行业案例（电影频道《山河纪》AIGC 纪录片用了白模+绿幕参考） | 单段原生 30s；超长模式最长 3min；官方称"原生4K输出+10bit"（第三方转述，标注存疑）；24fps | **部分公开**（官方公开白模参考工作流与插件；官方发布演示 prompt 见第三方文章） | **未披露具体金额** | 未披露 | https://jimeng.jianying.com/ ；https://m.toutiao.com/article/7669745302030565926 ；https://it.sohu.com/a/1057206660_100111246 |
| **Higgsfield** | **是**。官方 3D Jutsu 博客给出完整"灰模 blockout → previz → 出片"案例（说唱歌手地铁车厢 8s 单镜 360° 环绕） | 示例 8 秒 / 16:9；插件视频用 Seedance 2.5，生成约 1 分钟 | **公开**（官方博客给完整 prompt 与四步流程） | 未披露金额；仅"credits 在 Generate 按钮上显示" | ToU：不主张输入/输出所有权、不限制商用；标准账户内容可能用于训练 | https://higgsfield.ai/blog/higgsfield-3d-jutsu ；https://higgsfield.ai/blog/higgsfield-blender-plugin |
| **fal.ai** | **是**（这篇博客本身就是案例）。1930s 皮卡 pk 蒸汽火车"二人转"动作短片 | 10 秒 / 12 镜 / 24fps / 2.39:1 (1920×804) / 720p 出（detail refine 后观感约 2K） | **公开（最完整）**：4 阶段 3 prompt、每镜参数、失败经验全公开 | **未披露金额**（仅称 reference-to-video "expensive"） | 3DREAL LoRA 在 HF 标 `other`；LTX-Video 代码 Apache-2.0；端点属 fal 商业服务 | https://blog.fal.ai/from-clay-3d-render-to-a-real-action-short-a-3d-to-ai-pipeline-with-total-control/ ；https://huggingface.co/fal/LTX-2.3-3DREAL-LoRA |
| **OiiOii (oiioii.ai)** | **声称有**。PR 稿称 Seedance 2.5 提供"3D white-model previs"，走 7-Agent 工作流 | 30s 原生单条；平台称支持 170+ 风格 | **未真正公开管线**（官方 how-it-works 页只讲 7 Agent，**未提白模**；白模只在 PR 稿出现） | 有："Generation across OiiOii starts at $0.06 per second" | 未见 | https://www.oiioii.ai/how-it-works ；https://www.tmcnet.com/usubmit/2026/08/07/10427174.htm |
| **VideoClaw** | **否（不是白模路线）**。存在两个同名实体：① npm CLI `videoclaw`（终端 agent，30+ 功能，含 vision QC，provider 为 Veo/Seedance/Runway）；② videoclaw.com（Humeo 的桌面 app）。二者都**不做 3D 白模预演** | npm CLI：产出 MP4（含旁白/音乐）；桌面版：私人 alpha | 部分公开（npm 有 30+ 功能页与 CLI reference） | npm 版按 provider 计费；桌面版 credits | **未能验证**：npm 包 license 未在页面取得 | https://www.npmjs.com/package/videoclaw ；https://videoclaw.com/ |
| **ViMax** | **否（不是白模路线）**。HKUDS 多 Agent 视频生成框架，走"先图后视频 + 参考帧 + 首尾帧"，**无 3D 白模阶段** | 由底层模型决定（Veo/Seedance 等），README 举例多为短片段 | **公开**：README + 技术报告 + Web UI + TUI | 无（自付各 provider API） | **MIT**（README badge："MIT License"；LICENSE 文件存在） | https://github.com/HKUDS/ViMax |

**小结**：公开可复现的"白模→写实化成片"案例，最强的是 **fal.ai 的 clay→action short**（管线全公开）与 **Higgsfield 3D Jutsu**（prompt 全公开）。**即梦**有官方行业案例但缺参数级细节、成本不透明。**OiiOii** 只停留在 PR 宣称。**VideoClaw / ViMax** 都不是这条路线。

---

## ② 复用审查结论（禁止重复造轮子）

### 2.1 Blender 无头（headless）批量渲染 + bpy 脚本注入

| 项目 | URL | license | 一句话能力 | 判定 |
|---|---|---|---|---|
| Blender 官方命令行 | https://docs.blender.org/manual/en/latest/advanced/command_line/render.html | Blender 本体 GPL（文档 CC-BY-SA 4.0） | `blender -b file.blend -a` 无 GUI 渲染整段动画；`-s/-e` 定起止帧；`-f` 单帧；`-P` 跑 Python | **可直接复用**（这是官方标准做法，且已在本机 Windows 可用） |
| MCP for Blender（原 blender-mcp） | https://github.com/ahujasid/blender-mcp | **MIT** | Agent 通过 socket 控制 Blender，可执行任意 bpy、导出 GLB/FBX、生成/操作场景 | **可直接复用**（注意 `execute_blender_code` 可跑任意 Python，安全上需自带沙箱/审查） |
| bpy 注入范式参考 | Yi-111-a `scripts/build_whitemodel.py`（见任务 1-2） | 无 license（默认保留权利） | 用 shot-spec JSON 一次生成带相机动画的白模 previs mp4 | **需适配**（可参考其参数结构，代码不可直接商用） |

官方原文引用（Blender 命令行）：
- "`-b` Render in the background (without UI)."
- "`-a` Render the whole animation using all the settings saved in the blend-file."
- "`-s 10 -e 500` Set the start frame to `10` and the end frame to `500`."
- "**Always** position `-f` or `-a` as the last arguments."

MCP for Blender 原文：
- "**Code execution** Run arbitrary Python code in Blender from Claude"
- "**Export the scene, the selection or named objects to GLB/FBX for other applications (`export_scene`)"
- "By default, the AI can run any Python code in Blender. Set `BLENDER_MCP_SAFE_MODE=1` to check every script before it runs and block risky code"

### 2.2 白模粗片 → 写实化 的 video-to-video / img2img 开源模型（12GB 可跑）

> 判定基准：RTX 5070 Laptop 12GB 显存。

| 项目 | URL | license | 一句话能力 / 显存 | 判定 |
|---|---|---|---|---|
| **LTX-Video**（含 LTX-2 / 3DREAL 基础） | https://github.com/Lightricks/LTX-Video | **Apache-2.0**（仓库代码；权重另有条款，需查模型卡） | DiT 视频模型，支持 i2v、多关键帧、v2v、音频；**2B distilled / fp8 版本低显存可跑** | **需适配**（12GB 可跑 2B/distilled/fp8；LTX-VideoQ8 更友好） |
| LTX-VideoQ8（社区量化） | https://github.com/Lightricks/LTX-Video （Community 章节） | 随上游（Apache-2.0 派生，需核对） | 8bit 优化版，"Generate 720x480x121 videos in under a minute on RTX 4060 (8GB VRAM)" | **可直接复用（12GB 充裕）** |
| **Wan 2.2** | https://github.com/Wan-Video/Wan2.2 | **Apache-2.0** | MoE 视频生成；**5B 变体可跑消费卡；1.3B 更轻** | **需适配**（5B 在 12GB 上需量化/offload） |
| **CogVideoX**（zai-org/CogVideo） | https://github.com/zai-org/CogVideo | **Apache-2.0** | 文/图生视频，生态成熟（diffusers 支持） | **需适配**（12GB 可跑 2B，5B 需优化） |
| Wan 2.6 / 2.7 | （官方 API，无权重） | 闭源 API | —— | **必须自建无意义**：权重未开源，只能走云 API |

原文引用：
- LTX-Video："The model supports image-to-video, multi-keyframe conditioning, keyframe-based animation, video extension (both forward and backward), **video-to-video transformations**, and any combination of these features."；"**LTX-VideoQ8** … 🎥 Generate 720x480x121 videos in under a minute on RTX 4060 (8GB VRAM)"
- Wan 2.6 硬件（二手，标注待官方确认）："最低配置 … 显存 16 GB(FP8 精度,480p 文生视频) … 推荐 … 显存 24 GB 以上"（wan27.org）
- Wan 2.2 显存（二手）："The 5B variant runs on 8GB VRAM (RTX 3070/4060)"（cliprise.app，标注待官方确认）

**关键结论**：想要"白模粗片→写实化"且**本地 12GB 可跑**，最贴合的是 **LTX-Video（2B/distilled/fp8/Q8）+ 自训练或社区 IC-LoRA（如 3DREAL 思路）**。3DREAL 权重虽在 HF 开放下载，但**许可为 `other`、商用未明**，见 2.5。

### 2.3 镜头运动 / 时序保持（camera motion preservation）

| 项目 | URL | license | 一句话能力 / 显存 | 判定 |
|---|---|---|---|---|
| **MotionCtrl** | https://github.com/TencentARC/MotionCtrl | **Apache-2.0** | 统一控制器，独立控制相机运动（相机位姿序列）与物体轨迹；提供分支（VideoCrafter/SVD/AnimateDiff） | **需适配**（官网 DeepWiki 记 "GPU NVIDIA GPU with at least 8GB VRAM"，12GB 可跑；但需接到你的生成后端） |
| **CameraCtrl** | https://github.com/hehao13/CameraCtrl | **Apache-2.0** | 用相机轨迹控制视频生成（AnimateDiffV3 主干 + SVD 分支） | **需适配** |
| **"把 clay 视频当密集条件流"思路**（LTX 3DREAL / render-to-real） | https://blog.fal.ai/from-clay-3d-render-to-a-real-action-short-a-3d-to-ai-pipeline-with-total-control/ | 端点商业；LoRA `other` | 直接喂 CG clip 做运动/布局/相机条件 + 关键帧做外观锚点 | **需适配**（端点不可本地跑；可参考其训练范式自训 IC-LoRA） |
| 最实用的"零成本"方案 | 白模渲染本身即最稳的相机控制（Yi-111-a / Higgsfield / fal 三家用同一逻辑） | —— | 用 Blender 把相机定死，把白模当参考视频输入 | **可直接复用（思路）** |

原文引用：
- MotionCtrl："MotionCtrl can Independently control complex camera motion and object motion of generated videos, with only a unified model."；"`condtype=camera_motion` means only control the camera motion in the generated video."
- 第三方汇总官方许可："CameraCtrl: the Apache-2.0 code and weights target camera control on AnimateDiffV3, with an SVD branch."；"MotionCtrl: the Apache-2.0 project separates camera motion and object motion conditioning"（aikolhub.com；标注为二手）

### 2.4 自动质检（PSNR / SSIM / CLIP 打分）

| 项目 | URL | license | 一句话能力 | 判定 |
|---|---|---|---|---|
| **pyiqa / IQA-PyTorch** | https://github.com/chaofengc/IQA-PyTorch | ⚠️ **PolyForm Noncommercial License 1.0.0（+ NTU S-Lab License）——非商用！** | 一站式 FR/NR IQA：PSNR/SSIM/LPIPS/FID/NIQE/MUSIQ/CLIP-IQA 等，GPU 加速 | **必须自建或换许可**（商用被禁止）。若只做内部研究可复用 |
| fal.ai 的做法（可照抄） | https://blog.fal.ai/from-clay-3d-render-to-a-real-action-short-... | —— | `ffmpeg edgedetect` + PSNR 排序 + 50% 叠加图肉眼校验 | **可直接复用（思路，零依赖）** |
| Yi-111-a `compare_stack.py` | https://github.com/Yi-111-a/blender-shot-video | 无 license | 上下堆叠白模/成片做对比，仅需 OpenCV | **需适配**（代码无许可，建议自写） |

原文引用（pyiqa 许可，重点）："This work is licensed under the **PolyForm Noncommercial License 1.0.0** (see LICENSE) and the NTU S-Lab License for applicable components."
原文引用（fal 质检）："edge-detect both candidate and clay (ffmpeg edgedetect), compute PSNR, rank. ~17+ is good."；"**Verify with overlays, not vibes.**"

### 2.5 AI 影视流水线的开源 Agent 编排项目

| 项目 | URL | license | 一句话能力 | 判定 |
|---|---|---|---|---|
| **ViMax**（HKUDS） | https://github.com/HKUDS/ViMax | **MIT** | 7-Agent 编排：剧本→分镜→资产→一致性→合成；Idea2Video/Novel2Video/AutoCameo；TUI + Web UI | **需适配**（**无白模阶段**，需自行在前期插入 Blender 环节） |
| **Pallaidium** | https://github.com/tin2tin/Pallaidium | **GPL-3.0**（权重另计） | Blender VSE 内一站式生成/批处理/渲染队列/MCP | **需适配**（GPL 传染性；默认本地） |
| **VideoClaw (npm CLI)** | https://www.npmjs.com/package/videoclaw | 未能验证 | 终端 agent，分步流水线 + 人工闸 + vision QC + provider 路由 | **需适配**（license 未明，non-白模路线） |
| Higgsfield Bridge（MCP） | https://bridge.higgsfield.ai/mcp | 商业 ToU | Agent 直接操作打开中的 Blender 场景 | **需适配（商业/云）** |

原文引用（ViMax）："ViMax is an agentic video creation framework that connects narrative planning, visual consistency, image generation, video generation, and final assembly in one extensible workflow."；"**Consistent production pipeline** — coordinate references, first frames, camera continuity, and final assembly end to end."

---

## ③ 行动方案建议

基于以上核实，给出 3 条可落地路线，按"免费/本地优先"排序：

**路线 A（推荐主线）：自建「Blender 白模 + LTX-Video 3DREAL 范式」本地管线**
- 白模层：Blender 官方 CLI（`blender -b -P` + `-s/-e` + `-a`），用 JSON shot-spec 注入相机关键帧/时间轴；脚本参考 Yi-111-a 的参数结构（**自写代码，不复制其代码**，因其无许可）。
- 写实化层：本地跑 **LTX-Video 2B/distilled/fp8 或 LTX-VideoQ8**（Apache-2.0，12GB 有余）；训练/引入 IC-LoRA 复刻 3DREAL 思路（`video_url` 驱动运动 + `image_url` 驱动外观）。
- 质检层：自写 `ffmpeg edgedetect` + PSNR + 50% 叠加图（照抄 fal 思路）；**不要**直接依赖 pyiqa（非商用许可）。
- 编排层：自建薄编排（Python），或适配 ViMax（MIT，但需插入白模阶段）。
- 优点：零云费、许可清晰；缺点：IC-LoRA 训练需数据与算力。

**路线 B（快速验证）：借道国内可直连云**
- 白模层同上（Blender 本地）。
- 写实化层：**即梦 Seedance 2.5 官方 Blender 插件**（白模参考，国内可直连）或**火山方舟 Seedance API**（`role=reference_video` + `first_frame`，注意三组 role 互斥）。运镜靠 prompt，无独立 camera 字段。
- 质检/编排自建。
- 优点：最快见效、国内网络无阻；缺点：按量付费、可控性弱于路线 A。

**路线 C（对照参考，不建议作为主线）**
- 用 fal.ai `render-to-real`（管线全公开、效果最强）做"金标准"对照片，用于校准路线 A/B 的质量上限；但依赖境外云、成本不透明、LoRA 许可 `other`，不适合作为交付主线。

**关键工程约束（务必写进规范）**
1. **白模必须是纯灰、不贴图**（贴图会让模型读成"平面图片"）——三份一手资料一致。
2. **必须设"付费/生成前人工闸"**：先在白模层把相机与走位定死、验收后再付费。
3. **帧数对齐**：LTX 系需 `8k+1` 帧；Seedance 单条白模参考视频有体积/帧数上限（约 200M / 72 帧单段，**待官方确认**）。
4. **运镜要克制**：避免快速 360°/甩镜，否则肢体/颈部翻转。
5. **许可红线**：pyiqa（非商用）、3DREAL LoRA（`other`）、Yi-111-a（无许可）三者在商用前必须替换或取得授权。

---

## ④ 本轮新增了什么 / 仍缺什么

### 本轮新增（相对此前认知）
1. 把 7 个方案的 **6 问**逐项落到一手引用，明确了「谁是白模路线、谁不是」：**白模路线 = nano-banana-render / blender-shot-video / RonaldXDZ / 即梦插件 / Higgsfield / Pallaidium / fal 3DREAL**；**非白模路线 = VideoClaw / ViMax**。
2. 发现并纠正 **两处关键事实**：
   - `RonaldXDZ/blender-video-workflows` **URL 已 404**，实际仓库为 `RonaldXDZ/blender-video-workflows-blender-`（MIT，fork，1 star）。
   - **`pyiqa` 是非商用许可**（PolyForm Noncommercial 1.0.0），不能作为商用质检组件。
3. 明确云引擎**互斥矩阵**：Kling（参考图 vs 首尾帧互斥）、MiniMax H3（i2v vs r2v 互斥，role 五类）、Seedance（首帧/首尾帧/全模态参考三互斥）、Wan（无 camera 字段，audio 用 `parameters.audio`）。
4. 确认 **Wan 2.6/2.7 均为 API-only（未开源）**，"Wan 3.0"不存在；12GB 本地可跑的写实化候选收敛到 **LTX-Video 系 + Wan 2.2 5B/1.3B + CogVideoX 2B**。
5. 找到**两个官方样板案例**可做 prompt/参数抄作业：fal.ai clay 博客（全公开）、Higgsfield 3D Jutsu（全 prompt 公开）。

### 仍缺 / 未验证项（明确列出）
1. **Kling 官方文档正文无法整页抓取**（klingai.com / app.klingai.com 为 JS 单页）。因此「refer_image 与 first_frame 互斥」只有官方组合规则表 + 合作方节点/镜像措辞作为证据，**未取到官方一句直接表述**；音频参数名在不同来源有 `generate_audio` / `sound` 两种，**官方原生命名未验证**。
2. **Seedance 音频开关是否存在**存在矛盾证据（一方称 2.0 无开关、音频恒开；一方称 `generate_audio` 布尔）。**以官方 volcengine 文档为准 = 未验证**。
3. **Wan 2.6 是否开源权重**：官方无开源发布页证据，仅有二手评测称"API-only、未开源"。标注**待官方确认**。
4. **各方案具体金额**：fal.ai blog、即梦官方稿、3DREAL 案例**均未披露成本数字**；仅有 fal/Higgsfield/OiiOii 的单价片段。
5. **prompt/参数级细节缺失**：即梦官方未公开《山河纪》白模参数的完整 prompt；OiiOii 官方 how-it-works **未提白模**（白模仅见 PR 稿）。
6. **部分仓库许可缺失**：Yi-111-a/blender-shot-video（无 LICENSE，默认保留全部权利）；VideoClaw npm 包 license 未取得；3DREAL LoRA（HF 标 `other`，商用未明）。
7. **Blender 版本要求存在冲突**：Higgsfield 官方博客称 "Blender 5.1 or later"，帮助中心另有 "4.2 到 5.1" 说法，**未定论**。
8. **12GB 显存实测缺失**：LTX-VideoQ8 的 8GB 结论来自官方 README，但 **RTX 5070 Laptop 12GB 上的真实吞吐/fp8 支持** 未做实测（本轮不写代码，属未验证）。
9. **Windows 端 cloudflared / MCP 隧道**在实际网络环境下的可用性未验证（Yi-111-a 依赖它把本地白模变公网 URL）。

---
（报告结束）
