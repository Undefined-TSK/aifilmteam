> 基线：../00-基线报告/项目基线报告.md ｜ 规约：../_执行须知.md ｜ 导航：../索引.html

# 维度 4 · 自造轮子 vs 现成方案对比表

> 铁律（原文）：坚持「所有工具与模型类型皆有价值，只差全链路结合点」原则，不轻易废弃任何工具，而是找到其在链路中的正确位置。
> 口径：迁移成本按人日粗估；建议分「保留自研 / 引入现成 / 双轨」。

---

## 1. 逐工具对比表

| 自造轮子（路径） | 功能 | 成熟替代方案 | 迁移成本 | 建议 | 理由 |
|---|---|---|---|---|---|
| `tools/llm_gateway.py` | 五档路由 + 额度链滑档 | LiteLLM / OpenRouter | 3 人日 | **保留自研** | 本地优先 + 额度链滑档 + 密钥零泄漏为项目定制，通用网关无此语义 |
| `tools/crew_bus.py` | 事件总线（SQLite WAL） | NATS / Redis Streams / Kafka | 5 人日 | **保留自研** | 单机单进程场景，纯标准库零依赖；引入消息中间件违背「少一个外部依赖」 |
| `tools/jobs.py` | 异步作业账本 | Celery / RQ | 4 人日 | **保留自研** | 成功才计费 + 内容哈希幂等为项目定制；Celery 需 broker 常驻 |
| `tools/handoff_manager.py` | Agent 间交接状态机 | CrewAI Flows / LangGraph | 3 人日 | **保留自研（可借鉴）** | 四态状态机已够用；CrewAI Flows 为 C3 M18 编排层候选，非替代关系 |
| `tools/vram_lock.py` | 12GB 显存独占锁 | — | — | **保留自研** | 业界无通用「单卡分时锁」；12GB 约束为项目独有 |
| `tools/vlm_check.py` | VL 视觉质检 | 云端 VL API | 2 人日 | **双轨** | 本地 Qwen3-VL-4B 为 0 元档，云端 qwen3-vl-flash 为质量档（17d vl_scorer） |
| `tools/comfyui_client.py` / `comfyui_generator.py` / `comfyui_start.py` | 本地 ComfyUI 驱动 | [ComfyUI MCP]（mcp.film 收录 40+ 工具） | 2 人日 | **双轨（评估引入）** | ComfyUI MCP 可把工作流作为工具暴露给 Agent；自研 client 保留为本地 0 元抽卡层 |
| `tools/exr_to_control.py` | EXR→控制图 | ComfyUI ControlNet 节点 | 2 人日 | **保留自研** | 白模 EXR 单层多通道→depth/normal/canny 为项目定制链路 |
| `tools/tts_generator.py` | TTS 配音 | 云端 TTS API / edge-tts（违规） | 1 人日 | **保留自研** | 合规版 v2.0 已换 CosyVoice3/Qwen3-TTS；edge-tts 违规已排除 |
| `tools/gen_bgm.py` / `gen_sfx.py` / `gen_ambient.py` / `acestep_client.py` | 音频生成 | ACE-Step 官方 / Stable Audio | 2 人日 | **保留自研（四件可合并）** | 四件功能重叠，建议合并为 audio_gen 统一入口 |
| `tools/t4_batch{1,2,3}_signoff.py` + `t4_final_backfill.py` | 三批次签核 | — | 1 人日 | **合并自研** | 批次差异仅是数据参数，17d §7.3 推荐合并为 signoff 通用工具 |
| `tools/blockout_batch_render.py` | Blender headless 批渲染 | Blender MCP（mcp.film 收录） | 2 人日 | **保留自研 + MCP 双注册** | 正式渲染主干与故障回退不依赖 MCP 层（17d §7.2 推荐 b） |
| `tools/qc_media.py` | ffprobe 媒体质检 | Kinocut（本地视频后处理） | 2 人日 | **保留自研** | G3b 帧数门机器件，轻量且已投产 |
| `tools/pngseq_to_mp4.py` | PNG→MP4 打包 | FFmpeg 直调 | 0.5 人日 | **保留自研** | 本机 Blender 无 FFmpeg，外部打包为必要环节 |
| `tools/dit_ingest.py` | 数据血缘摄取 | — | — | **保留自研** | SHA256+零字节+缺引用显式标记为项目独有（7 债务之一） |
| `tools/ai_label.py` | GB45438 双标识 | — | — | **保留自研** | 国标合规定制，无现成方案 |
| `tools/director_intent.py` | 导演意图管理 | Notion / Obsidian | 2 人日 | **双轨** | 文档管理可借 [Notion]/[Obsidian]；但 intent 机器契约须自研 |
| `tools/budget_manager.py` | 预算闸门 | — | — | **保留自研** | 云端 ≤18 次/50 池为项目定制 |
| `tools/asset_manager.py` / `k13_version_tree.py` | 资产/版本树 | DVC / git-lfs | 3 人日 | **保留自研 + git-lfs 补位** | 资产元数据自研；大文件版本化可引 git-lfs（维度 13） |
| `tools/blockout_min_v1.py` / `make_r4_l1_blockout.py`（早期单镜脚本） | 早期白模 | — | 0.5 人日 | **归档候选（不删）** | 逻辑已并入共享模块；作单镜最小样例保留教学价值（17d §7.2 推荐 b） |
| `tools/wan22_client.py` 等 Wan2.2 时代脚本 | 单镜生成 | — | 0.5 人日 | **归档候选（不删）** | 留作回归基线 |

---

## 2. 引入现成方案的三个候选（按适配度）

| 现成方案 | 类型 | 本项目适配点 | 引入成本 | 风险 |
|---|---|---|---|---|
| ComfyUI MCP | MCP server | 把本地 ComfyUI 工作流作为工具暴露给 Agent，替代部分自研 client 包装 | 中 | 与本机 ComfyUI 版本兼容；License 须核 |
| Blender MCP | MCP server | 官方标准 Blender MCP；但项目已自研 `baimo_mcp_server` + addon（13 工具），有 R17-8 试点背书 | 低~中 | 与自研双组件功能重叠，须评估是否合并 |
| Kinocut | 本地视频后处理 | 守卫式本地视频操作（FFmpeg/字幕/QC/SFX）——与 N5 剪辑链部分重叠 | 中 | 与自研 tech_cut/audio_mix 重叠，须去重 |

来源（2026-10-05 定向调研）：mcp.film/mcps/comfyui（40+ 工具）；mcp.film/recommendations（Blender MCP 为 3d-scene-control 首选、Kinocut 为 local-post）；docs.comfy.org。

---

## 3. 结论

1. **自研占比高是合理的**：核心 10 件（llm_gateway/crew_bus/jobs/handoff/vram_lock/dit_ingest/ai_label/exr_to_control/budget_manager/qc_media）均绑定项目独有语义（12GB 单卡、≤100 元、GB45438、本地优先），通用方案无法直接替代。
2. **可引入现成方案集中在「工具暴露层」**：ComfyUI MCP / Blender MCP / Kinocut 可替代自研工具的「包装」部分，但底层能力仍须自研。
3. **合并优于废弃**：音频四件、签核四件为内部重叠，合并为统一入口（不删逻辑）。
4. **归档不删除**：早期单镜脚本（blockout_min_v1/wan22 系列）留档作回归基线。