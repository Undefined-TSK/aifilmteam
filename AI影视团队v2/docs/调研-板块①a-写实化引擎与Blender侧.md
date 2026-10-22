# 调研 · R2 板块①a —— 写实化引擎 × Blender 侧技术

> 调研员：`research-engine-blender`（AI 影视团队 v2 · R2 板块①）｜日期：2026-09-27（全文访问日期均为此日）
> 范围：**仅外部公开资料**；未读写旧项目、未跑生成、零花费
> 老板三条硬要求已执行：**结论落在 ✅/❌/⚠️/❓**、**每条结论带「反方证据」**、**口径统一（来源+访问日期+证据等级；积分折算成元）**

---

## 0. 决策建议汇总表（先给结论）

| 候选 | 写实能力 | 结构控制强度 | 12GB+16GB 可行性 | 成本 | 许可 | 成熟度 | 风险 | **建议** |
|---|---|---|---|---|---|---|---|---|
| **fal 3DREAL render-to-real** | 高（真人质感） | 强（几何锁定，但**非硬约束**） | 云端，本地零显存 | `$0.0024075/MP × W × H × 帧数` | `other` → LTX-2 社区协议（**年营收 >$10M 需授权**） | 高 | **商用条款原文缺失** | ✅ **选为主力**（⚠️商用条款需落实） |
| **即梦 Seedance 2.5 白模** | 高 | 强（非硬约束；远景/小细节会漂） | 云端 | 780 credits / 30s@720p ≈ **35 元** | 生成内容归用户，需实名 | 高 | 插件版本早期；实测**掉帧+物理滑动** | ⚠️ **条件选（备选 B）** |
| Higgsfield for Blender | — 无自身引擎（转发 Seedance 2.5） | 取决于引擎 | 云端 | credits ≈ $0.033–0.07/credit | 不禁止商用；标准账号内容**可被用于训练** | 中 | 它是**编排层**不是引擎 | ❌ **不选**（重复投入） |
| Wan2.2-Fun-Control / VACE-Fun（本地） | 中（14B 好，需量化） | 强（Depth/Pose/Canny/轨迹） | ⚠️ GGUF 6–12GB 可跑但**极慢** | **0** | Apache-2.0 | 中 | 16GB 内存是硬瓶颈 | ⚠️ 条件选（480p 短片段） |
| **Wan2.1-VACE-1.3B（本地）** | 中低 | 强（参考/遮罩/V2V） | ✅ **≈8.19GB 可跑** | **0** | Apache-2.0 | 中 | 本机权重残缺（196MB vs 应 4.31GB） | ✅ **补齐权重后立刻可用（唯一零成本可控验证路径）** |
| Runway / Luma / Pika | 高 | ❌ **无白模/深度条件化** | 云端 | 订阅 | 商用 | 高 | 不满足"结构硬约束"前提 | ❌ 不选 |
| 腾讯混元 HunyuanVideo 1.5 | 中高 | ❌ 无原生白模/相机轨迹 | fp8+offload 14–16GB | 0 / API | **排除 EU/UK/韩国** | 中 | 无相机轨迹级控制 | ❌ 不选 |
| ComfyUI `blender-temporal` 节点 | — | 强（EXR 深度/法线→ControlNet） | 本地 | 0 | **PolyForm Noncommercial** | 低 | **禁止商用** | ❌ 不选（**但思路可借**） |

**核心判断**：**写实化主力选 fal 3DREAL，备选即梦白模；结构控制必须由 Blender 定死，引擎侧只做"重绘表面"；本地 Wan2.1-VACE-1.3B 是唯一零成本可控验证路径，且只需补齐权重。**

---

## 1. fal LTX-2.3 render-to-real / 3DREAL IC-LoRA

| 结论 | 等级 | 出处 | 反方证据 | 处置 |
|---|---|---|---|---|
| 端点 `fal-ai/ltx-2.3-quality/render-to-real`；**`video_url` 驱动运动、`image_url` 驱动外观**；触发词 `3DREAL` 强制保留 | 一手 | fal API schema / HF `fal/LTX-2.3-3DREAL-LoRA` | 触发词强制不可改，细粒度控制只能靠 prompt；LoRA scale 无最优指引 | ✅ |
| 三档 adapter：**light**=最忠实结构、幻觉最少（**端点默认**）；**strong**=更激进写实、复杂场景更好但漂移更多；**strong-v2**=**同一 clip 内多镜/多切点保持连贯 + 同步音频 + 说话人脸/口型显著改善 + 更锐** | 一手 | HF README | 仅 strong-v2 有多镜能力 | ✅ **选 strong-v2** |
| **多镜一条 clip：支持（仅 strong-v2）** | 一手 | HF README（"stays coherent across cuts inside one clip"） | 无第三方独立复现 | ✅ |
| `num_frames` 必须 **8k+1**（17/33/41/81/97…）；IC-LoRA 控制预算：**720p ≤ 约 6s、480p ≤ 约 15s**，超限 422 | 一手 | fal API schema | 官方只给 "roughly"，实际边界需自测 | ⚠️ 长镜走 480p |
| `intensity`=adapter 预设（默认 light）；`enable_detail_refine`=2× 空间上采样+detailer，**输出宽高各 ×2 = 像素 ×4 ≈ 价格 ×4**（默认关）；`detail_refine_strength` 默认 0.75（fal 博客实测用 0.9）；`generate_audio` 默认 true；steps 默认 15 可至 30；guidance 默认 1 | 一手 | fal API schema + fal blog | 开 detail_refine 即 4× 成本，**是最容易被忽略的预算陷阱** | ⚠️ 仅终稿开 |
| **计费公式**：`$ = 0.0024075/MP × 宽 × 高 × 帧数 / 1e6`（向上取整）。1280×720×121 ≈ 112MP → **$0.270**；开 refine 后 2560×1440×121 ≈ 447MP → **$1.076** | 一手 | fal 计费说明 | — | ✅ |
| **失败不计费** | 二手 | aitrendtool（转述官方口径） | **未在 fal 官方计费页核到原文** | ⚠️ 需二次确认 |
| **许可**：HF 标 `license: other` → 指向 **LTX-2 Community License Agreement**；官方口径 **年营收 < $10M 免费商用，> $10M 需签商业授权** | 一手（HF model card）+ 二手 | HF LTX-2.3 Model Card | **3DREAL LoRA 仓库自身 `license:other` 未附条款正文**；HackerNoon 直指"需联系 fal 澄清商用权" | ❓ **商用条款原文未能验证**（需向 fal 书面确认 LoRA 权重是否随 LTX 社区协议） |
| 性能六要素（端到端秒数/峰值显存/GPU 利用率/是否含加载） | ❓ | README 未提供 | HackerNoon："未给出生成时间、显存、吞吐基线" | ❓ 需自测 |
| fal 博客流程：Blender MCP 驱动、**33 关键帧 × 4 seed = 132 条、zero failed jobs**；作者明确"**不是一句提示词就成的魔法**"，每阶段需人工验收 | 一手 | blog.fal.ai/from-clay-3d-render… | 单项目自述，无第三方复现 | ✅ 路线可信 |
| **宽高比陷阱**：16:9 参考图会**静默覆盖** 2.39:1 白模 | 一手 | fal blog | — | ⚠️ 白模与锚定图宽高比必须一致 |

---

## 2. 即梦 Seedance 2.5 白模控制

| 结论 | 等级 | 出处 | 反方证据 | 处置 |
|---|---|---|---|---|
| 官方 Maya/Blender 插件，两入口「相机渲染」「本地上传」；**只吃渲染后的白模视频，不读 .blend/.ma 工程** | 一手（官方宣传页）+ 二手（实测文） | jimeng.jianying.com | 插件版本混乱：宣传页 0.8.0 / 实测文称 0.1 版 | ⚠️ |
| 输入白模视频 **2–30s**、输出 **4–30s**、**仅 480P/720P**（**2.5 砍掉 1080p/4K**）；30s 直出可延至 180s（Beta）；参考最多 30 图 + 10 视频 + 10 音频 | 二手（CLI 实测 + 官宣） | 公众号实测；apiframe；sohu | **2.0 原为 1080p，2.5 实际降到 720p**（官宣 4K 未兑现） | ⚠️ 分辨率天花板 |
| **上传体积(MB)/帧数上限** | ❓ | — | 官方未公开 | ❓ 未能验证 |
| **粗/细颗粒度**：粗=简单几何草模，AI 参考运动轨迹与空间关系**从零生成**；细=精细白模，AI 在其上**做着色渲染** | 二手 | csdn / cnblogs 横评 | 官方定义文件未定位 | ⚠️ 概念可用，口径待官方确认 |
| CLI：`dreamina multimodal2video --video=<白模mp4> --model_version=seedance2.5 --duration=5 --video_resolution=720p`；另有 text2video/image2video/user_credit | 二手 | 公众号实测 + skillhub | **CLI 完整参数表未公开** | ⚠️ |
| **credits→元（口径混乱）**：41元/725分→0.0566；780分/30s@720p≈35元→0.0449；¥10=140分→0.0714；4K 路径 69元/505分→0.136 → **区间 ≈ 0.045–0.136 元/积分** | 二手 | 极目新闻；smzdm；sohu | 同一平台多口径并存，**横向比价不成立** | ⚠️ 按实付套餐换算 |
| 实测口径：5s@720p = **160 credits**；输出 1280×720 ≈ 5.056s，**可变帧率 ≈24.12fps**（任务摘要标 24fps） | 二手 | 公众号实测 | 任务摘要帧率不可信，以 ffprobe 为准 | ⚠️ |
| **商用条款**：生成内容知识产权"由您自行在合法合规范围内维护和使用"，纠纷自负；**生成内容可能非独特**；平台获授权用于优化服务；需实名 | 一手 | 火山 即梦AI 服务条款 3.3–3.5 | **官方条文未直接写"可商用"**，仅"由用户自行维护使用" | ⚠️ **条件商用**：需实名 + 禁名人肖像/品牌 LOGO/影视截图，无排他性 |
| **本地 HTTP 桥接**：插件在本机**随机端口**起临时 HTTP 服务，绑 **127.0.0.1** + **随机 token**；**生成链接后不能立刻退出 Blender**；Workbench 预览需真实 OpenGL 视口，**纯后台模式走不通** | 二手 | 公众号实测 | 未在官方文档核到 | ⚠️ **批处理一律走 CLI 绕开插件** |

**反方证据（即梦，重要）**：实测**严重掉帧 + 不自然物理滑动，场景渲染"像色块涂抹"**；BGM 被环境声生硬取代；**道具会退回白模占位形状、角色身份漂移、追逐关系消失**；小尺度建筑/远景/轨道数量/标牌**会漂移**；2.5 砍掉 1080p/4K；积分消耗比 2.0 高约 50%，续写 3–4 分钟后一致性明显下滑，多角色音色不统一、残留低频嗡鸣。

---

## 3. Higgsfield for Blender

| 结论 | 等级 | 处置 |
|---|---|---|
| 七分页：Scene Builder / 3D Model / Character Animation（自动装配带权重骨骼+关键帧）/ Image（原生 4K）/ Video / Camera / Asset | 一手 | — |
| Video 分页引擎 = **Seedance 2.5**，"viewport 直喂"，带 Anti-Slop 模式，约 1 分钟出片 | 一手 | ⚠️ |
| Camera 分页：**手机当虚拟相机，物理移动手机实时驱动场景相机** | 一手 | ✅ 创意可用 |
| **MCP Bridge** `bridge.higgsfield.ai/mcp`：额外获得"操作**当前打开场景**"能力。**边界**：条款允许限制频率/并发/payload/算力；云端依赖；**MCP/CLI/Canvas/Supercomputer 一律消耗 credits，Unlimited 仅限 web 端** | 一手 + 二手 | ⚠️ |
| **更值得抄的开源 MCP**：`higgsfield-ai/fnf-local-pluging-bridge-mcp`，**Blender 4.2+**，控制**后台 Blender 进程**，无需插件/HTTP/开窗口；工具含 `bl_add_primitive` / `bl_set_transform` / `bl_add_camera` / `bl_insert_keyframe` / `bl_render` / `bl_execute`；**无自动重试与回滚，Blender 崩溃不自动重启，Python 未沙箱** | 一手（GitHub README） | ✅ **可参考实现自己的 MCP** |
| 价格：Starter $15/月(200cr)、Plus $49月/$39年(1000cr)、Ultra $129月/$99年(3000cr)；credit ≈ **$0.033–0.070** | 一手 + 二手 | — |
| 是否支持上传自有白模 mp4 | ❓ | ❓ 未能验证 |
| **整体定位**：**它没有自己的写实化引擎**，Video 分页就是调别家；卖点是编排 | — | ❌ **不选（重复投入）** |

---

## 4. 其他"白模/深度条件化"引擎

| 候选 | 控制输入 | 可行性 | 等级 | 反方证据 | 处置 |
|---|---|---|---|---|---|
| **Wan2.2-Fun-Control / VACE-Fun** | Canny/Depth/Pose/MLSD/轨迹 + 首尾帧 + V2V | 14B 官方需 ~60GB；Kijai BF16/GGUF 量化后 **6–12GB 可跑但慢** | 一手 + 二手 | "5B 变体更轻但质量更低、伪影更多" | ⚠️ 条件选（480p 短片段） |
| **Wan2.1-VACE-1.3B** | 参考图/视频、V2V、遮罩编辑 | **~8.19GB VRAM 可跑**；F16 权重 **4.31GB**（GGUF Q8=2.32GB）；**Apache-2.0** | 一手 + 二手 | 1.3B 质量有限；VACE 无音画/口型能力 | ✅ **补齐权重即为零成本可控路径**（本机 196MB `.part` vs 官方 4.31GB，缺口已定位） |
| Runway / Luma / Pika | 仅文字 + 图/视频参考 + 相机控制 | — | 二手 | 多份横评明确"**均不支持白模输入**" | ❌ |
| 腾讯混元 1.5 | 无原生白模/相机轨迹，靠文字语义 | fp8+VAE tiling **14–16GB**（3090 约 5–6 min/5s） | 二手 | 无 ControlNet 式相机路径；许可**排除 EU/UK/韩国** | ❌ |
| Seedance 2.5 直接 API（ModelArk/Apiframe） | 与官方同源 | $0.15/s@480p、$0.34/s@720p | 二手 | — | ⚠️ 备选（绕开即梦 UI） |
| **ComfyUI `blender-temporal`** | Blender Z/Normal pass → EXR → ControlNet depth | 技术路线教科书级 | 一手（GitHub） | **许可 PolyForm Noncommercial，禁止商用** | ❌ 不选（**思路可借**：Blender Z pass 是 ground truth，比 MiDaS/ZoeDepth 估计更准） |

---

## 5. Blender 侧技术

### 5.1 极简低模库
| 结论 | 等级 | 反方证据 | 处置 |
|---|---|---|---|
| 行业惯例 = 方块/长方体/平面/薄板做 blockout（靠轮廓/遮挡/透视/时序说话） | 一手（fal 博客自述） | — | ✅ |
| 可直用 CC0 库：**Kenney**（2 万+ 资产，含 BLEND）、**Quaternius**（CC0）、**KayKit**（CC0）、**Poly Haven**（CC0，PBR/HDRi） | 一手 + 二手 | Kenney 低多边形风格高度可辨识，直用会"一眼 Kenney"（白模阶段无所谓） | ✅ 选 |
| 参数化生成：`bpy.ops.mesh.primitive_*` + 自定义 operator 批量生成 | 二手 | — | ✅ |

### 5.2 通用人体模型（human_generic）
| 结论 | 等级 | 反方证据 | 处置 |
|---|---|---|---|
| **MPFB2（MakeHuman Plugin For Blender）为首选**：基础网格/目标/纹理/服装/姿势**全部 CC0**；源码 GPLv3；兼容 **Blender 4.2+**；原生支持 **Rigify 与 Mixamo 动画**；可导出 Alembic/glTF/USD；官方明示"输出不含程序逻辑痕迹，视为你的数据，无使用限制" | 一手 | MPFB 2.08"部分功能尚粗糙、部分工具测试有限" | ✅ **选** |
| MakeHuman 独立版 2020 后停更，主线转 MPFB2 | 二手 | — | ✅ |
| **"白模头要不要带基础面部量感"：证据方向是要带** —— 白模越简单留给模型自由解释的空间越大，会出现"道具退回占位形状""角色身份漂移"；官方排障表要求用**颜色/高矮/位置**锁死角色身份 | 二手 | **未能验证**业界针对"无五官白模→人脸漂移"的系统性研究/官方规范 | ⚠️ **条件选：头部保留头型/颈部体量/朝向等基础量感，五官交给参考图定义；不要做成球头** |

### 5.3 四足动物
| 结论 | 等级 | 处置 |
|---|---|---|
| 开源可商用四足：Quaternius / KayKit / Kenney 均有 CC0 低多边形动物包（含绑定与动画） | 二手 | ⚠️ 用 CC0 动物包或自建 box-rig |
| Mixamo **不支持非人形** | 二手 | — |
| 专门的"四足通用白模标准资产库" | ❓ | ❓ 未能验证 |

### 5.4 动作来源与缓动
| 结论 | 等级 | 反方证据 | 处置 |
|---|---|---|---|
| **首选 Quaternius Universal Animation Library**（CC0，120+ clips，8 向 locomotion/jog/sprint/爬行/游泳/近战/跑酷，FBX/GLB/.blend，**可再分发原始文件**，商用无附加条款） | 二手 | 需自行 retarget 到目标骨架 | ✅ 选 |
| Mixamo：免费、royalty-free 可商用，但**不支持中国区国家代码账号**、**不可再分发原始文件**、不可修改捕捉数据、多数 clips 无 root motion | 二手 | 许可措辞存在解读分歧；大量项目共用同一库易"撞脸" | ⚠️ 条件选 |
| CMU mocap / ACCAD BVH：免费但老式 marker 采集，**有 tracking 误差/抖动/漂移，需清理**；SFU 库质量较高可补充 | 二手 | 质量对 hero 动画不够 | ⚠️ |
| **避免 Blender 默认 ease-in-out**：① Preferences > Animation > F-Curves > **Default Interpolation 改 LINEAR**（仅影响之后新建关键帧）② 已有曲线选中按 **T** 选 LINEAR 或 CONSTANT ③ 脚本走 `bpy.ops.graph.interpolation_type(type='LINEAR')` ④ 真抛物线用物理仿真/手动采样，**禁止用 BEZIER 近似** | 一手（Blender API docs）+ 二手 | LINEAR 会丧失自然加减速，不适合"有重力的跳跃" → **按镜头性质分通道设插值** | ✅ 统一 LINEAR + 抛体用物理 |

### 5.5 渲染与导出（本机无 FFMPEG 编码器）
| 结论 | 等级 | 反方证据 | 处置 |
|---|---|---|---|
| **PNG 序列 + 外部 ffmpeg** 为标准做法（实测：Blender 5.1 构建"没有可用的 FFmpeg 输出枚举"，改出 120 张 PNG 由系统 ffmpeg 合成 1280×720/24fps/H.264） | 二手（实测） | 与本机 Blender 5.2.2 情况一致 | ✅ 确认 |
| **深度/法线导出**：View Layer Properties > Passes > Data 勾 **Z / Normal**（可加 Vector/UV）；Output Properties > File Format = **OpenEXR MultiLayer**，把全部已启用 pass 写入同一文件；**Compositor 的 Z 口不必连接**（4.2 起 Composite 节点已无 Z 口，但 pass 仍会保存） | 一手 + 二手 | 多层 EXR 单帧 15 个 pass 可达 30–50MB | ✅ |
| 精度：depth/vector 建议 **32-bit full float**，一般合成用 16-bit half；压缩用 ZIP/PIZ 无损（**PXR24 会丢 depth 精度**） | 二手 | — | ✅ |
| **姿态图**：对渲染结果跑 OpenPose/DWPose 等预处理器（VACE-Annotators 提供官方预处理） | 二手 | — | ⚠️ 需自行串联 |
| **相机参数**：EXR header 可嵌相机矩阵等 metadata；脚本按帧导出 `camera.data.lens / sensor_width / sensor_fit` + `matrix_world` | 二手 | 未找到官方"一键导出相机内参"功能 | ⚠️ 自写脚本 |

### 5.6 Blender MCP（⚠️ 本机踩雷区）
| 结论 | 等级 | 反方证据 | 处置 |
|---|---|---|---|
| **官方** Blender Lab MCP server（blender.org/lab/mcp-server），要求 **Blender 5.1+**，GPL-3.0+；官方自述"**无任何防护地执行 LLM 生成代码**，建议在虚拟机或无敏感数据系统上使用"，其 `weak_sandbox.py` 自嘲"只是拍一下手腕" | 二手 | — | ⚠️ |
| **社区** `ahujasid/mcp-for-blender`（原 blender-mcp，2026-09-16 改名），MIT，**29,326 stars**，**36 个工具**：`execute_blender_code` / `get_viewport_screenshot` / `add_keyframe` / `render_from_camera` / `export_scene` / `bpy_api_lookup` + Poly Haven / Sketchfab / Hyper3D Rodin / Hunyuan3D / Tripo 集成 | 二手 | — | ⚠️ |
| **能力**：建几何 ✅、设关键帧 ✅、渲染 ✅、读预览（viewport screenshot）✅、导深度图 ✅ | 一手（工具表） | — | ✅ |
| **失败模式（决定性的）**：socket **无认证无加密**（"任何能连到该端口的人都能在 Blender 里跑 Python"）；2026 年发布 **4 个 CVE**（含 Poly Haven 下载器路径穿越 CVE-2026-66004）；**Blender 5.1.x / 5.2 下响应被截断在 51 字节 → "Incomplete JSON response"，5.0 可用、5.1 起坏**；另有大量 ~4 分钟超时无报错案例 | 一手（GitHub issue #339）+ 二手 | **本机 Blender 5.2.2 恰在断裂区间** | ❌ **高风险：不宜直接用该 MCP**；建议走 **bpy 脚本直调 + `-b` 后台模式**或自建 MCP |

### 5.7 版本与 API 坑
| 结论 | 等级 | 反方证据 | 处置 |
|---|---|---|---|
| Blender 4.4 引入 slotted actions：`action.fcurves` / `action.groups` / `action.id_root` 降为 **legacy proxy，仅作用于 slot[0]**；该 legacy API 声明**将在 5.0 移除** | 一手 | — | ⚠️ |
| **Blender 5.x：`action.fcurves` 已被整体移除**，`action.fcurves.new(...)` 抛 `AttributeError`；必须走 `action_ensure_channelbag_for_slot(action, slot)`（5.1+ 从 `bpy_extras.anim_utils` 导入）或 `action.layers[].strips[].channelbag(slot).fcurves` | 二手（高可信）+ 一手 | — | ✅ **本项目脚本一律走 channelbag 路径** |
| **必须同时设置 `obj.animation_data.action` 与 `anim_data.action_slot`**，否则动画"像没发生" | 二手 | — | ✅ |
| Blender 5.1 其他脚本兼容问题：对象命名触发解析错误；无 FFmpeg 输出枚举 | 二手（实测） | — | ⚠️ |

---

## 6. 未验证清单（为什么没验）

| 项 | 原因 |
|---|---|
| fal 3DREAL LoRA 的**商用条款原文** | HF 以 `license:other` 占位，未附条款正文；需向 fal 书面确认 |
| fal "失败不计费"的官方原文 | 仅二手转述，未在 fal 计费页核到 |
| fal render-to-real 端到端秒数/峰值显存/GPU 利用率 | 官方 README 与 API 页均未公布 |
| 即梦插件上传体积(MB)/帧数硬限 | 官方说明页未列出 |
| 即梦白模"粗/细颗粒度"官方定义 | 只找到二手横评表述 |
| `dreamina` CLI 完整参数表 | 官方未公开全表 |
| Higgsfield 插件最低版本（≥5.1 vs 4.2） | 官方 FAQ 与第三方文章矛盾 |
| Higgsfield 是否支持上传自有白模 mp4 | 官方文档仅描述"viewport 直喂" |
| 四足专用"通用白模"标准资产库 | 未检索到 |
| "无五官白模→人脸漂移"的业界系统性经验 | 仅找到二手翻车排查表，无官方规范/论文 |
| Blender"一键导出相机内参"官方功能 | 未找到，需自写脚本 |
| fal 那支片子具体使用的 Blender MCP 项目名 | 原文未指名 |

---

## 7. 反方证据汇总（"唱反调"的部分）

| 对象 | 反方证据 | 来源 |
|---|---|---|
| **fal 3DREAL** | ① 许可 `other` 需联系 fal 澄清商用 ② 触发词强制不可改，细粒度控制只能靠 prompt ③ LoRA scale 无最优指引 ④ **未公布任何性能基线** ⑤ 作者自述"不是一句提示词就成的魔法"，每阶段需人工验收 ⑥ **16:9 参考图会静默覆盖 2.39:1 白模** | HackerNoon；fal HF README；fal blog |
| **即梦 Seedance 2.5 白模** | ① 实测**严重掉帧+不自然物理滑动**，场景"像色块涂抹" ② BGM 被环境声生硬取代 ③ **道具退回白模占位形状、角色身份漂移、追逐关系消失** ④ 小尺度建筑/远景/轨道数量/标牌会漂移（"强空间参考而非硬约束"）⑤ 2.5 砍掉 1080p/4K ⑥ 积分消耗比 2.0 高约 50%，续写 3–4 分钟后一致性明显下滑、多角色音色不统一、残留低频嗡鸣 ⑦ 社区质疑"上传工程=交饭碗" | 腾讯云开发者测评；今日头条白模实测；搜狐测评；smzdm |
| **Higgsfield** | 条款允许限流；云端依赖，本地 Blender 不可替代；agent 改开放场景带来命名/版本/可重复性/审批边界风险；无公开 benchmark；自身 pilot 曾同时获赞与质疑 | digitalproduction；explainx |
| Wan2.2-Fun-Control | 官方需 ~60GB；量化虽降到 6–12GB 但极慢；5B 变体质量更低伪影更多 | ComfyUI docs；stablediffusiontutorials |
| Wan2.1-VACE-1.3B | 1.3B 质量有限；VACE 无原生音画/口型能力；官方未给统一 VRAM 最小值 | aiwiki；aikolhub |
| Mixamo | 许可措辞存在解读分歧；**中国区国家代码账号不可用**；不可再分发原始文件；多数 clips 无 root motion；不可修改捕捉数据；大量项目共用同一库易"撞脸" | Mixamo FAQ（多来源转述） |
| MPFB2 | 2.08 版"部分功能尚粗糙，部分工具测试有限" | cgchannel |
| Kenney | CC0 低多边形风格高度可辨识，直用会"一眼 Kenney" | indiehackers |
| **Blender MCP** | socket 无认证无加密；2026 年 4 个 CVE（含路径穿越 CVE-2026-66004）；**Blender 5.1.x/5.2 下响应截断 51 字节**；超时 4 分钟无报错；官方 MCP 自述无防护执行 LLM 代码 | GitHub issue #339；strayspark |
| Blender 4.4+ API | legacy `action.fcurves` 仅作用于 slot[0]，5.0 移除，迁移期大量插件失效 | developer.blender.org；devtalk |
| ComfyUI blender-temporal | **PolyForm Noncommercial，禁止商用** | GitHub repo LICENSE |
| 腾讯混元 | 无原生白模/相机轨迹控制；许可**排除 EU/UK/韩国**；自托管 5–12 min/片段 | vantaige |
| Runway / Luma / Pika | **均无白模或深度条件化输入**，只有文字+参考图/视频+相机控制 | sohu；wideframe；bottlerocket |

---

## 8. 落到本项目的五条动作（我这一路的建议）

1. **写实化主力 = fal 3DREAL `strong-v2`**：480p 做长镜（≤15s）、720p 做 ≤6s；`num_frames` 从剪辑长度倒推 8k+1；**detail_refine 仅终稿开**（4× 成本）；**白模与锚定图宽高比必须一致**。
2. **备选 = 即梦 Seedance 2.5 白模**，**走 CLI**（绕开 HTTP 桥接与 OpenGL 视口限制），先 480p 验证再升 720p。
3. **本地零成本验证 = 补齐 Wan2.1-VACE-1.3B 权重**（目标 4.31GB F16 或 2.32GB Q8，Apache-2.0，≈8.19GB 显存可跑）——这是**先跑通链路、不花钱**的最优解。
4. **Blender 脚本规范**：统一 LINEAR 插值 + 抛体用物理；动画走 **channelbag** 路径并显式绑定 `action_slot`；渲 **PNG 序列 + 外部 ffmpeg**；Z/Normal 走 **OpenEXR MultiLayer（depth 用 32-bit float + ZIP/PIZ）**。
5. **资产选型**：人体用 **MPFB2（CC0）+ 保留头颈基础量感**；低模用 **Kenney/Quaternius（CC0）**；动作优先 **Quaternius CC0 动画库**。**不投 Higgsfield 插件**（无自有引擎）；**不用 ComfyUI blender-temporal**（非商用）；**不直接用社区 Blender MCP**（本机 5.2.2 在已知断裂区间 + 无认证 + 4 个 CVE）→ 走 **bpy 脚本直调 + `-b` 后台模式**。
