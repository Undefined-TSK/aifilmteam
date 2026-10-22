# R2 核实报告：R1 遗留 9 项收口

- 调研员：技术调研员（AI 影视团队 / 任务 A）
- 日期：2026-09-27
- 任务：把 R1 报告 `research_R1_blockout_pipeline.md` 遗留的 9 项未验证项逐项收口。
- 取证规则：**开一手页面**，每条结论附 URL + 原文照抄；拿不到写「未能验证：具体原因」；禁止「预计能成 / 应该可以」类推断。
- 目标硬件（复述）：RTX 5070 Laptop 12GB / 16GB 内存（可用约 2GB）/ 国内网络 / 成本敏感。

> **本环境限制声明**：本轮 WebFetch 可正常运行；但**本机 Bash 无外网**（`curl` 走代理 127.0.0.1 失败），且**火山引擎文档站、即梦站、klingai.com、HuggingFace 主站**均为 JS 单页/受限：直开只返回标题或通用壳。凡此类情况，已在对应位置标注「正文经搜索引擎对官方页抓取取得」或「未能直开」。HuggingFace 最终经 **hf.co 镜像域名的官方 API** 取得一手元数据。

---

## ① 逐项核实表

### 项 1｜Kling 可灵（官方托管文档）

**一手来源（可灵官方合作方 = 阿里云百炼托管文档，非 klingai.com 原站）**：
https://help.aliyun.com/zh/model-studio/kling-video-generation-api-reference

| 子问题 | 结论 | 原文照抄（简体中文，逐字） | 置信度 |
|---|---|---|---|
| `refer_image`（元素参考图）与 `first_frame` 是否互斥 | **不可同用（等效互斥），但官方未用「互斥」二字**。文档以「仅支持以下组合 + 非法组合报错」的**封闭式列举**限定；允许组合中**没有** `refer+first_frame` | 「参考生视频：支持以下 media 组合。仅传入 feature 时：必须传入1个视频。仅传入 refer 时：参考图片与多图主体数量（element_list 的数组长度）之和不得超过7。传入 feature+refer 时：必须传入1个视频，且参考图片与多图主体数量之和不得超过4。传入 feature+first_frame 时：必须传入1个视频和1张首帧。」「**仅支持以下媒体素材组合，非法组合将报错。**」 | 高 |
| 元素参考图参数**实际命名** | 阿里云托管文档用 **`refer`**（不是 R1 引用的 `refer_image`）；素材类型枚举为 `feature`/`refer`/`base`（参考视频 feature、元素参考图 refer、待编辑视频 base） | 「参考生视频（type=feature、type=feature+refer、type=refer）：必须设置（aspect_ratio）」；「video 输入场景（omni模型）：…**引用视频类型主体后，不可再传参考图/图片类型主体**。」 | 高 |
| 音频开关**官方参数名** | **`audio`**（boolean，默认 `false`）。**既不是 `generate_audio`，也不是 `sound`** | 「**audio** `boolean`（可选）…是否生成有声视频…`false`：默认值，输出无声视频。`true`：输出有声视频。注意：当传入视频（`type=base或feature`）时，`audio` 只能设置为 `false`。`kling/kling-v3-turbo-video-generation` 固定生成音画同出视频，该字段不生效。」 | 高 |
| 附：原声保留参数（另一字段） | `keep_original_sound`（string，`no`/`yes`），与 `audio` 含义不同 | 「**keep_original_sound** `string`（可选）…生效条件：当且仅当传入视频（type=base或feature）时生效。是否保留原视频声音。`no`：默认值，不保留原声。`yes`：保留原声。」 | 高 |

> ⚠️ **命名冲突提醒**：R1 引用的 `refer_image` 来自 klingai.com 原文；本轮阿里云托管文档用的是 `refer`。两站**同一能力、不同字段名**，落地时必须按所选接入方（可灵原站 vs 阿里云百炼）的字段名传参。
> **未能验证**：klingai.com 官方原站正文（JS 单页，直开仅得标题「可灵AI 开放平台」）；「refer 不可与 first_frame 同用」的**一句直接措辞**仍缺，仅有封闭列举 + 报错规则。

---

### 项 2｜Seedance 2.0 / 2.5 是否音频开关

**官方来源（火山引擎，均为官方 URL）**：
- https://docs.volcengine.com/docs/82379/1521675 （查询视频生成任务列表）
- https://www.volcengine.com/docs/82379/1520757 （创建视频生成任务）
- https://www.volcengine.com/docs/82379/2298881 （视频生成入门教程，含请求示例）

| 结论 | 原文照抄 | 置信度 |
|---|---|---|
| **有音频开关，官方参数名 = `generate_audio`（boolean），支持 Seedance 2.5 与 2.0 系列** | 「\\*generate_audio boolean \| 是否生成同步音频 \| 生成的视频是否包含与画面同步的声音。\\*true：模型输出的视频包含同步音频。\\*false：模型输出的视频为无声视频。\\*模型支持：Seedance 2.5、Seedance 2.0 系列」 | 中 |
| 官方请求体示例（逐字） | `"generate_audio": true, "ratio": "adaptive", "duration": 5, "watermark": false` | 中 |
| 参考音频输入（另一字段，注意区分） | 「\\*audio_url object 必选 \| 音频对象…Seedance 2.5：单个音频时长 [2, 30] s，最多传入 10 段参考音频…Seedance 2.0 系列：单个音频时长 [2, 15] s，最多传入 3 段参考音频」 | 中 |

> **结论**：R1 的矛盾证据（一方称「无开关、音频恒开」）**被否定**——官方存在 `generate_audio` 布尔开关。R1 的「未验证」→ 本轮**收口为「有，参数名 generate_audio」**。
> **取证说明（诚实标注）**：上述官方页为 **JS 单页渲染**，`WebFetch` 直开只返回通用壳（甚至串页到无关文档）。正文系**搜索引擎对上述官方 URL 的抓取结果**取得，未能在浏览器内逐字复核页面 DOM。故置信度标「中」。

---

### 项 3｜Wan 2.6 是否开源权重

**官方一手来源（GitHub 官方组织页）**：https://github.com/Wan-Video

| 结论 | 原文照抄 | 置信度 |
|---|---|---|
| **Wan 2.6 未开源权重**。官方 GitHub 组织仅 6 个仓库，**无任何 Wan2.6 / Wan2.5 / Wan2.7 权重仓库** | 组织页仓库列表（逐字）：`Wan2.2`（「Wan: Open and Advanced Large-Scale Video Generative Models」，Apache-2.0）、`Wan2.1`（同上，Apache-2.0）、`Wan-Dancer`（Apache-2.0）、`Wan-Animate-2`（Apache-2.0）、`Wan-skills`（Apache-2.0）、`diffusers`（fork）。「Showing 6 of 6 repositories」 | 高 |
| 可获得的开源权重仅到 **Wan 2.2（Apache-2.0）** | 组织页 `Wan2.2` 仓库 license 标注 `Apache-2.0`，描述「Wan: Open and Advanced Large-Scale Video Generative Models」 | 高 |

> **二手旁证（按要求标注为二手）**：「Wan 2.6 Dec 2025 ❌ No (Commercial API)」、2.5/2.6 关闭、官方 2.6 发布稿仅提「available on Alibaba Cloud's Model Studio…」不提开源与 license。来源：https://howaiworks.ai/blog/alibaba-wan-open-weights-stopped-at-2-2 、http://wan27.org/blog/wan-2-6-open-source-guide 、https://bytewaves.news/reviews/wan-2-6-open-source-video-model-alibaba-s-free-alternative-to-veo-and-kling-reviewed 、https://www.usefastlane.ai/models/wan-2-6 。
> **未被本报告采信的说法**：部分二手页称「Wan 2.7 已 Apache-2.0 开源」，与官方 GitHub 组织无 2.7 仓库的事实**冲突**，按「以官方为准」不予采信。
> **未能验证**：HuggingFace 官方组织页（huggingface.co/Wan-AI）本环境直开失败，未能逐一核对其 27 个仓库清单（该数字来自二手）。

---

### 项 4｜成本（是否有公开计费页 / 价格数字）

| 方案 | 结论 | 原文照抄 / 数字 | URL | 置信度 |
|---|---|---|---|---|
| **fal.ai `render-to-real` 端点** | **有公开定价**（R1 曾判「未披露」→ 本轮修正） | 「Your request will cost **$0.0024075** per megapixel of generated video data (width × height × frames), rounded up. For example, if you generate a video that is 121 frames long at 1280 × 720, your total generated video is ≈112 MP, and your request will cost **$0.270**. If you turn on **enable_detail_refine**, the output is delivered at 2× the width AND 2× the height — that is **4× the pixels, so roughly 4× the price**: the same 121 frames delivered at 2560 × 1440 are ≈447 MP, and your request will cost **$1.076**.」 | https://fal.ai/models/fal-ai/ltx-2.3-quality/render-to-real | 高 |
| **即梦 / Seedance（火山官方）** | **有公开计费页**（token 计价）。插件**专属价官方未披露** | 官方模型价格页：「doubao-seedance-2.5 输出视频分辨率为 480p,720p · 输入不含视频：70.00 元/百万token · 输入包含视频：42.00」「doubao-seedance-2.0：不含视频 46.00 / 含视频 28.00」。另一官方页按秒计价：「seedance_2.5 无输入视频 480p 1.346 元/秒、720p 3.024 元/秒；有输入视频 720p 1.814 元/秒」 | https://docs.volcengine.com/docs/6454/1544106 ；https://www.volcengine.com/docs/6492/2595411 | 中 |
| 即梦插件活动价 | 即梦站促销语（页面抓取）：「年卡会员最高加赠25条Seedance 2.5 720P成片，叠加折扣单秒首月低至 **￥0.28**」 | —— | https://jimeng.jianying.com/ | 中低（促销语境，非单价表） |
| **3DREAL LoRA（HF）** | **无独立计费页**；授权 `other`，使用走 fal 端点按上文 MP 价 | 模型卡未给价格；计费即 fal 端点价 | https://huggingface.co/fal/LTX-2.3-3DREAL-LoRA | 高（「无独立价」为确认事实） |

> **结论**：R1「各方案均未披露金额」的表述**部分被修正**——fal 端点、火山 Seedance 均有**公开的、可查的价格数字**；「官方未披露」的只剩**即梦白模插件的专属计费**与 **3DREAL LoRA 的独立定价**。

---

### 项 5｜即梦白模插件参数级细节 + OiiOii how-it-works

**A. 即梦白模能力（官方一手：飞书官方使用手册）**：https://bytedance.larkoffice.com/wiki/RXh5ww6EqighMdkVTMccm2d4n7e

| 结论 | 原文照抄 | 置信度 |
|---|---|---|
| **Seedance 2.5 官方具备「白模控制」能力（一手确认存在）** | 「🎬 专业级白模控制：引入强大的白模能力，无论是复杂的镜头调度、分镜设计，还是角色的站位与运动轨迹，都能实现工业级的精准把控。」；「还新增了白模控制与绿幕编辑的能力！」 | 高 |
| 时长能力（官方手册） | 「单次最高支持 30 秒内的视频延长生成…最长可以延长至60秒」；「使用超长视频模式，可以最多生成180秒视频」；「🎯时间戳文本控制…可精确到具体秒数下达指令」 | 高 |

**B. 插件参数级细节（能否导出相机渲染 / 体积 / 帧数上限）**——**官方插件页 JS 无法抓取，以下为二手实录，按要求标注**：

| 子问题 | 结论 | 依据（二手） | 置信度 |
|---|---|---|---|
| 是否支持**相机渲染导出** | **是**。插件内「视频上传方式」可选「**相机渲染**」或「**本地上传**」；相机渲染可选相机参数/分辨率/保存位置（Maya 另有「帧范围」），渲染完点「上传至即梦生成」 | 第三方实录（自称「官方使用手册」）：https://www.blenderx.cn/blog/seedance25 | 中低（二手） |
| 支持的**体积 / 帧数 / 分辨率上限** | 截图口径：**单次上传 200M、输出 720P、720 帧、24fps、mp4/h264** | 社区文章引用「0.1版插件面板截图」：https://post.smzdm.com/p/avgwkp39 | 低（二手 + 版本号 0.1，官方未披露） |
| Blender 版本要求 | 插件为 Blender 附加上载器；具体版本官方未在本轮页面上给出 | —— | **未能验证**（官方插件下载页 `jimeng.jianying.com/ai-tool/*` 为 JS 单页，直开无正文） |

**C. OiiOii 官方 how-it-works 是否提到白模**

| 结论 | 原文照抄 / 判定 | URL | 置信度 |
|---|---|---|---|
| **官方 how-it-works 页无任何 white model / previs / blockout 字样**（一手确认） | 该页仅描述 7 Agent（Art Director / Scriptwriter / Character Designer / Scene Creator / Animator / Editor / Sound Engineer）与「25+ underlying models」；全文无「white model / previs / blockout / Blender」 | https://www.oiioii.ai/how-it-works | 高 |

> **结论**：R1 对 OiiOii 的判断**被证实**——白模仅出现在 PR 稿，官方 how-it-works 不提。即梦白模**能力**由官方手册一手确认；但**插件参数级上限（200M/720帧）官方仍未披露**，仅二手。

---

### 项 6｜许可（一手 API 元数据）

| 对象 | 结论 | 原文照抄（API 原始 JSON） | 置信度 |
|---|---|---|---|
| **`Yi-111-a/blender-shot-video`** | **仍无 LICENSE（license = null）** | `"license": null`（`https://api.github.com/repos/Yi-111-a/blender-shot-video`，字段逐字）；仓库 `default_branch: "main"`，`created_at: 2026-06-29`，`pushed_at: 2026-07-19`，`stargazers_count: 4` | 高 |
| **`VideoClaw`（npm 包 `videoclaw`）** | **非标准开源许可**，指向仓库内的自定义 LICENSE 文件 | `"license":"SEE LICENSE IN LICENSE"`（`https://registry.npmjs.org/videoclaw` 原始 JSON，逐字）；最新版本号 `3.0.0-alpha.15` | 高 |
| **`fal/LTX-2.3-3DREAL-LoRA`（HuggingFace）** | **license 字段 = `other`**（无标准开源/商用许可，需联系 fal） | HF API 逐字：`"tags":[...,"license:other",...]`，`"cardData":{"license":"other","base_model":"Lightricks/LTX-Video","base_model_relation":"adapter",...}`；`"likes":255`，`"downloads":0`（https://hf.co/api/models/fal/LTX-2.3-3DREAL-LoRA） | 高 |

> 说明：`yi-111-a` 与 `videoclaw` 均经**官方 API** 直接取得；HuggingFace 主站直连失败，改由 **hf.co 镜像域名的官方 API** 取得模型元数据（内容与 huggingface.co 同源）。

---

### 项 7｜Higgsfield for Blender 要求的 Blender 版本（定论）

**官方一手（两处，均 2026-08 更新的现行版本）**：

| 来源 | 原文照抄 | URL |
|---|---|---|
| 官方博客 | 「**Requirements:** Blender 5.1 or later, on Windows or macOS.」 | https://higgsfield.ai/blog/higgsfield-blender-plugin |
| 官方帮助中心（Blender 段落） | 「Works on **Blender 5.1 or later**, on Windows or macOS.」 | https://higgsfield.ai/creator-hub/help-center/integrations/external-integrations-higgsfield |
| 官方帮助中心（FAQ 直答） | 「**Which Blender versions does the plugin support?** Blender 5.1 or later, on Windows or macOS.」 | 同上 |

> **定论**：**Blender 5.1 或更高版本（Windows / macOS）**。R1 记录的「帮助中心 4.2–5.1」说法在**当前官方页面上已不存在**（帮助中心正文与 FAQ 口径均已统一为 5.1+，博客口径一致）。
> **对本机**：本机 Blender **5.2.2 ≥ 5.1**，**满足**插件版本要求（`5.2.2` 由用户提供，未在本轮独立复核版本号）。置信度：高。

---

### 项 8｜跳过（本地实测项，由主线自测）

按要求跳过，不在本轮范围。

---

### 项 9｜cloudflared 隧道（免费 quick tunnel + Windows）

**官方一手**：
- https://developers.cloudflare.com/cloudflare-one/connections/connect-networks/do-more-with-tunnels/trycloudflare/
- https://developers.cloudflare.com/cloudflare-one/networks/connectors/cloudflare-tunnel/downloads/

| 子问题 | 结论 | 原文照抄 | 置信度 |
|---|---|---|---|
| 免费 quick tunnel 能力 | **有**。一条命令把 localhost 暴露为公网随机子域 `trycloudflare.com` | 「Developers can use the TryCloudflare tool to experiment with Cloudflare Tunnel without adding a site to Cloudflare's DNS. TryCloudflare will launch a process that generates a random subdomain on `trycloudflare.com`. Requests to that subdomain will be proxied through the Cloudflare network to your web server running on localhost.」；命令：「`cloudflared tunnel --url http://localhost:8080`」 | 高 |
| 定位 / SLA | **仅测试与开发用，无 SLA / 不保证在线** | 「Quick Tunnels are intended for testing and development only.」；「We don't guarantee any SLA or uptime of TryCloudflare… not for deploying a production website.」 | 高 |
| 限制 | 并发硬上限 200 in-flight；不支持 SSE | 「Quick Tunnels are subject to a hard limit on the number of concurrent requests… **200 in-flight requests**. If a Quick Tunnel hits this limit, the HTTP response will return a `429`」；「Quick Tunnels do **not** support Server-Sent Events (SSE).」 | 高 |
| Windows 支持 | **官方提供 Windows 客户端**（.exe 与 .msi） | Windows 段：「Download the latest release from GitHub… **Executable**：`cloudflared-windows-386.exe` / `cloudflared-windows-amd64.exe`；**MSI**：`cloudflared-windows-386.msi` / `cloudflared-windows-amd64.msi`」；「Instances of `cloudflared` do not automatically update on Windows.」 | 高 |
| 注意事项 | 有 `config.yaml` 时 quick tunnel 不生效 | 「TryCloudflare quick tunnels are currently not supported if a `config.yaml` configuration file is present in the `.cloudflared` directory.」 | 高 |

> **结论**：`Yi-111-a/blender-shot-video` 用 cloudflared 把本地白模变公网 URL 的做法，**在官方文档层面能力成立**（免费、有 Windows 客户端、一条命令）。**未能验证**：在本机「国内网络」下的**实际连通性/可用性**（本轮只做文档核实，未做联网实测）。

---

## ② 相对 R1 修正了什么

1. **Kling 音频参数名定论**：官方（阿里云托管）为 **`audio`**（boolean，默认 false）。R1 的两个候选 `generate_audio` / `sound` **均被否定**。
2. **Kling 素材字段命名**：阿里云托管文档的元素参考图字段为 **`refer`**（R1 引用的 `refer_image` 来自 klingai.com 原站命名）；两站字段名不一致，**落地须按所选接入方传参**。
3. **Seedance 音频开关定论**：**有**，官方参数名 **`generate_audio`**（支持 2.5 与 2.0 系列）。R1「未验证 → 有矛盾证据」本轮**收口为「确有开关」**。
4. **Wan 2.6 未开源**：由 **官方 GitHub 组织页**一手证据确认（仅 2.1/2.2 + 衍生仓库；无 2.6/2.5/2.7 权重仓库）。R1 仅为二手推断，本轮升级为**一手**。
5. **成本**：**fal `render-to-real` 有公开定价数字**（`$0.0024075 / MP`，例 121帧@720p ≈ `$0.270`，detail refine 4× ≈ `$1.076`）。R1「未披露」**被修正**。火山 Seedance 亦有公开 token/秒级价。
6. **Higgsfield Blender 版本定论 = 5.1+**（博客与帮助中心两处一致，FAQ 直答同口径）。R1 的「4.2–5.1 vs 5.1+ 冲突」**已消解**；当前官方页面不再有 4.2–5.1 说法。
7. **3DREAL LoRA 许可升级为一手**：HF API 字段 `"license":"other"`（含 `"license:other"` tag）。R1 已是二手 `other`，本轮**升级为一手确认**。
8. **OiiOii 白模**：官方 how-it-works **确实不提白模**（一手确认）。R1 判断被证实，**收口为「白模仅见 PR 稿」**。
9. **即梦白模能力**：官方飞书手册**一手确认存在「专业级白模控制」**（R1 仅有第三方转述）。

---

## ③ 仍缺什么（明确列出）

1. **Kling 官方原站（klingai.com）逐字表述仍缺**：该站 JS 单页，直开只返回标题。「refer/refer_image 与 first_frame 不可同用」的**一句官方直接措辞**仍未取到，现结论依赖**封闭列举 + 非法组合报错**规则（等效互斥）。且两站字段命名不一致（`refer` vs `refer_image`）。
2. **Seedance 官方文档正文未能整页直开**：`generate_audio` 原文系搜索引擎对**官方 URL**抓取所得，未能在浏览器内逐字复核页面 DOM（火山文档站 JS 渲染）。建议主线用官方 SDK/接口实测该字段。
3. **即梦白模插件的官方参数级上限未披露**：`200M / 720帧 / 72帧 / 24fps` 等**仅来自社区截图（0.1 版）**，官方插件页（`jimeng.jianying.com/ai-tool/*`）JS 无法抓取，**未能验证官方口径**。
4. **即梦白模插件无公开独立计费页**：仅有通用 token/秒级价与活动语，**无插件专属单价**。
5. **Wan-AI 的 HuggingFace 官方组织页未能直开**：`huggingface.co/Wan-AI` 本环境抓取失败，「27 个仓库、均 ≤2.2」为二手；官方 GitHub 组织页已完成一手核实。
6. **cloudflared 在「国内网络」下的实际可用性未实测**：仅完成官方文档层面的能力与 Windows 支持核实，**联网连通性未验**。
7. **本机 Blender 5.2.2 版本号**为输入信息，未在本轮独立复核（属本地实测项，归主线）。

---

## ④ 达标判定

**R2 达标。** 判定依据：

- 9 项中，第 8 项按任务要求**明确跳过**（本地实测项）；其余 **8 项全部给出结论**，其中：
  - **7 项为一手/官方来源**（项 1 官方托管文档、项 3 官方 GitHub、项 4 fal 官方端点页、项 6 官方 API、项 7 官方博客+帮助中心、项 9 官方文档、项 5-OiiOii 官方页）。
  - **项 2（Seedance 音频）** 结论可靠但**页面为 JS 渲染**，原文经搜索引擎对官方 URL 抓取取得，置信度标「中」并已如实说明。
  - **项 5 插件参数级上限** 官方未披露，已如实标注为**二手**，未以推断填充。
- 全程**无「预计能成 / 应该可以」类推断**；拿不到的一律写「未能验证：具体原因」。
- 本轮**修正 R1 共 9 处**（见 ②），其中「Kling 音频参数名 = `audio`」「Seedance 有 `generate_audio`」「fal 有公开定价」「Higgsfield = 5.1+」为**结论级修正**。

**结论：R2 达标**（8/8 可核实项均已收口，1 项按要求跳过；剩余缺口已在 ③ 逐条列明且不影响主线决策）。

---

（报告结束）
