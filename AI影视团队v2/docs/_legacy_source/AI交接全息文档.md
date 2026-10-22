# AI交接全息文档——《雨夜寻猫》AI影视项目

> **文档版本**：v1.2 ｜ **最后更新**：2026-09-27（A 接手·只读盘点轮） ｜ **维护者**：接手AI「A」（SeniorDeveloper）
> **A 轮产出**：`logs/_handoff_A_20260927/` 下 A0 探索报告 / A1 合并方案 / A2 三张对照表 / A3 目录结构方案 / A4 待替换词清理清单 / A5 接手准备报告 / research_R1_blockout_pipeline.md。⚠️ 本轮**只读**：三项待拍板（合并 / 目录整理 / 待替换词）与审计件§13十项**均未执行**。
> **文档性质**：项目唯一入口文档——任何AI（包括原助手本人）接手工作时，**必须先完整读完本文档再动手**
> **第五批必读附件**：《docs/阶段0体检审计报告与规划修订v6.0.md》——含15条实测证据、职能体检、§9修订后阶段路线、§13拍板单10项。凡与手册v5.0冲突的执行条款以该审计件为准（老板2026-09-26指令"先全面体检再推进"的产出）。

---

## 0. 本文档的用途与维护契约（接手AI必读，最高优先级）

### 0.1 用途
本文档是《雨夜寻猫》AI影视项目的中枢交接件。老板（用户）会把这份文档发给接手的AI；AI接手后一切工作的依据、边界、历史、现状都在这里。目标：**另一个AI读完本文档，能像现实生活中同事交接班一样无缝接手继续工作**。

### 0.2 维护契约（强制，每次对话必须执行）
1. **每次对话结束前**，接手AI必须更新本文档：
   - 第14节「会话日志」追加一行本次会话记录（日期+做了什么+结论）
   - 第12节「当前待办」勾掉完成项、补充新任务
   - 涉及工具状态/目录/服务变化的，同步更新第5-10节对应表格
   - 文档头部「最后更新」时间戳刷新
2. **只追加或修改条目，不删除历史记录**（与记忆文件同一约束）
3. 老板会把更新后的本文档重新发回（发给原AI或新AI均可），AI凭第14节会话日志恢复上下文继续工作——**本文档是跨AI会话的持久记忆载体**
5. **【第五批新增】跨工作区写入限制**：接手AI若经MCP远程工作区操作，文件写入被限制在 `D:\ai_film_projects\` 内，C盘记忆文件（§11路径）**只能读不能写**。此时约定：把记忆增量写入 `logs/_mem_mirror/PENDING_MEMORY_APPENDS.md`（工作区内待回写清单）并在本文档§14标注，由有本机权限的助手或老板回写记忆文件。禁止只在对话里说"记忆已更新"。
4. 本文档与记忆文件（见第11节）双轨并行：本文档给"接手AI+老板"看，记忆文件给"AI运行环境"看。两边都要更新，内容保持一致。

### 0.3 接手后的第一个动作（检查表）
- [ ] 完整读完本文档（约15分钟）
- [ ] 读记忆文件：`c:\Users\LZH\.trae-cn\memory\projects\-c-Users-LZH-AppData-Local-hermes--p2-95933d038ffd3d514624\project_memory.md` 和 `c:\Users\LZH\.trae-cn\memory\user_profile.md`
- [ ] 检查服务状态**并留实测记录**：ComfyUI(8188)、api_server(8190)；再跑 §2.2 的"只读体检四件套"（shots计数 / ffprobe交付规格 / `tools`内引擎与锁引用 / `hermes\profiles`实存数）——文档与实存已发现 6 处不一致（审计件§10），**不看实测就会按错前提干活**
- [ ] 查第12节待办 + 读 `docs/阶段0体检审计报告与规划修订v6.0.md` §13（十条建议是否已拍板），向老板确认当前优先级后开工
- [ ] 【第五批】读 `logs/_mem_mirror/PENDING_MEMORY_APPENDS.md`：若已有未回写条目，先提醒老板回写C盘记忆，再继续干活（否则你在按旧记忆做判断）

---

## 1. 项目一句话定位

用本地开源模型（Wan2.2等）+按需云端引擎（可灵/MiniMax H3），以**19个AI岗位组成的虚拟剧组**（对标好莱坞真人剧组全职能）制作《雨夜寻猫》80秒短片成片，要求成片**像现实剧组实拍**（对标 oiioii.ai 水准），**不能有PPT感**（一图一图的幻灯片式镜头是已被老板否决的失败形态）；最终目标是能接商单的AI影视制作能力（阶段3商业化）。

---

## 2. 老板画像与协作规则【最高优先级，违反=工作作废】

### 2.1 沟通与性格
- 语言：中文。直接说正事，省略寒暄客套开场白
- **不着急，节奏放缓、深度到位**——老板明确说过"感觉你太着急了，不着急，慢慢来，不慌"
- 喜欢编号列表和表格，厌恶大段文字
- 先给结论，再给推导；深奥概念用生活类比；技术术语首次出现附一句通俗解释

### 2.2 每轮对话的标准工作流（4步，不可跳过）
1. **读记忆**：对话开始先读project_memory.md（含TODO板块）和user_profile.md，总结当前进度
2. **执行任务（第五批补前置）**：一次一个明确任务，完成后标记✅；技术选型/API/框架版本不确定点**先搜索验证再动手**；**动手前先"只读体检"**（§2.2 第0步四件套：实测优先于文档）
0. **第五批修订·只读体检（动手前必做）**：先确认能读到什么、实测是什么，再规划。最小体检集：
   - `Get-ChildItem D:\ai_film_projects\projects\雨夜寻猫\shots -Filter *.mp4 | Select-Object Name,Length`
   - `ffprobe -v error -show_entries format=duration,bit_rate -show_entries stream=codec_type,width,height,r_frame_rate,sample_rate <粗剪.mp4>`
   - `Select-String -Path tools\*.py -Pattern "dashscope|minimax|kling|vram_scheduler"`（查工具是否真被调用）
   - `Get-ChildItem C:\Users\LZH\AppData\Local\hermes\profiles -Directory | Select-Object Name`（查岗位真实运行实例数）
   原则：**先实测后下结论**；实测与文档冲突以实测为准，并回写文档。
3. **更新记忆**：任务完成后追加到记忆文件——踩坑/调研结果→project_memory「踩坑记录」；新偏好→user_profile；进度→「TODO」板块
4. **输出进度概览**：回复末尾固定格式：
```
---
📋 项目进度：[当前阶段名] | 完成度：[x%]
📝 剩余待办：
- [任务1] ([状态])
---
```

### 2.3 硬性偏好（历史决策，不要推翻）
- **省成本**：偏好免费额度/开源本地部署，拒绝高开销（之前Kimi K3+CC switch烧钱教训）；云端API只按开拍单精准调用
- **本地开源优先**：生图/生音频/生视频优先可本地部署的开源模型（Wan2.2/ACE-Step/MuseTalk等），云端闭源仅作实拍感主力按需用
- **反补丁式修补**：偏好系统性重构解决根因，不接受"只加不整导致越来越乱"
- **不确定就问，别逞强**：老板原话"别太逞强，我会帮你的"——遇到飞书开放平台/云控制台等需要人工操作的事，诚实求助
- **细节确认后再动手**：老板像CSS设计师，期望像素级细节确认后再实现
- **数据驱动**：参数选择要有数据依据（例：分析12个NBS文件111K音符定2.5s静默阈值）

### 2.4 设计与UI偏好
- 禁止emoji作UI图标，必须用SVG线性图标（Lucide风格），图标与文字flex垂直居中对齐
- "简约风"=拒绝廉价俗气（强对比色块/丑字体/电商广告式堆砌），不是"元素少"——MC风格GUI、丰富动画、多样运镜只要服务主题都要
- 喜欢Blender几何节点式的模块化节点界面

### 2.5 老板的职责边界
- 老板=出品人+监制：保留**最终剪辑权与绿灯决策权**（导演岗不转移这两权）
- 账号注册/云控制台操作由老板人工完成（已发向导：`D:\ai_film_projects\start_账号注册向导.bat`），AI负责写.env配置和验证调用

---

## 3. 用户的原始要求全集（演进链，不可遗忘）

老板的需求是用加号连接的一大串，历经多轮扩展，**当前生效全集如下**：

1. **成片形态**：像现实剧组实拍（对标 oiioii.ai），无 PPT 感；解决"人物五官奇怪"问题
2. **技术路线**：优先可本地开源部署的生图/生音频/生视频大模型（不限于MiniMax）；云端引擎按镜补强；多引擎混合（本地Wan2.2兜底+云端H3/可灵主力）
3. **团队规模**：建议给团队加人（灯光师/道具师等）→原团队可拆分+可合并+可删减+新增→岗位优化细分精简、专业化对口化→已定稿**19岗位**（仍可再议）
4. **调研要求**：对应工具技术调研+同类竞品全面检索+深度搜索+查看文档+权威官方网站+了解AI影视团队现状/成就/进度——**全覆盖、不省略任何步骤**
5. **对标要求**：现实好莱坞大片真实剧组+可直接执行的详细规划（**零返工**：不需要做到某一步反过来补做规划工作）
6. **Agent技术**：skill+tool+mcp+Function Calling等技术也要调研并择优吸收（结论见团队架构v4.0第5节：三层模型，保留自研机制+吸收MCP工具接入层等3点+明确不引入重型框架）
7. **复刻oiioii.ai**：做同类功能（AI影视生成平台），先以本片流程验证能力
8. **文档要求**：所有文档保持更新（本节即体现）；交接文档（本文档）必须详细到另一个AI能无缝接手
9. **商单愿景**：阶段3商业化（合规清单已列入手册——FLUX dev非商用红灯、AI生成内容标识办法2025-09-01已施行等）
10. **第五批原话（2026-09-26，不可遗忘）**：老板要求"首先，全面仔细检查一下现在的项目是否真的可以实现制作好莱坞真人专业影视团队的成片"，并重申全部原有要求（现实剧组视角+全方位调整优化新增删减精简合并+全覆盖调研+本地开源与API混合+专业对口+超多模态全覆盖+API多元化协作+agent技术(skill/tool/mcp/Function Calling)全查+市场调研+前景规划+避免PPT级廉价效果+**开始前先做全面规划、避免边做边想边调整**）；要求"再全面深入一点，不着急，慢慢来，不慌"；并明确**组织分工是基础但要能不加岗就不加岗**。授权：**只读**访问 MCP 工作区之外的文件，**禁止**删除/修改/新建工作区之外任何文件。

---

## 4. 诚实的能力评估（2026-09-26，AI自查）

**问题：现在的项目真的能实现"好莱坞真人专业影视团队级成片"吗？**

### 4.1 已实测验证的能力（有产出物为证）
| 能力 | 工具 | 实测证据 |
|---|---|---|
| 写实生图+角色锁定 | SDXL+ControlNet+三视图/CharacterLock | 全片静图资产、粗剪v4（output\雨夜寻猫_粗剪_v4.mp4，14.9MB） |
| 图生视频（本地开源） | Wan2.2 TI2V 5B（ComfyUI 0.37.2） | 3-3绿眼/4-1归途视频镜头（shots\内4个mp4） |
| BGM生成（本地开源） | ACE-Step v1.5 | acestep_00001.flac（48kHz立体声30s） |
| 对白TTS | edge-tts | v4粗剪全部对白音轨 |
| 环境音/音效 | 程序合成（gen_ambient/gen_sfx） | 雨声/雷声等已入mix |
| 转写（字幕轴） | faster-whisper 1.2.1 | 台词转写吻合，SRT+JSON双输出 |
| VLM质检（一致性） | Qwen3-VL-4B | 锚点vs生成帧比对verdict=pass |
| 口型同步（本地开源） | MuseTalk 1.5 | 双任务85帧端到端，口型时序正确、人脸无崩坏 |
| 剪辑混音 | ffmpeg管线（build_mix.py） | 粗剪v1→v4迭代4轮 |
| 调度平台 | api_server+handoff机制 | 8190常驻运行中 |

### 4.2 差距清单（尚未建成/未验证——按序补齐）
| # | 差距 | 影响项 | 补齐动作 | 阻塞点 |
|---|---|---|---|---|
| 1 | 云端引擎（可灵/H3）未接入 | 实拍感主力（与本地有代差） | D2客户端开发+联调 | **等老板两Key** |
| 2 | 86%镜头仍是静图 | PPT感根源 | D4-D6打样+阶段1全片视频化 | 差距1 |
| 3 | 4个岗位SOUL.md未建 | 19岗位未满编（作曲/服装造型师/道具师/调色师） | 批2/批3重写（阶段1前） | 无 |
| 4 | 引擎拍板未做 | 主力引擎选择 | D7盲选评审 | 差距2 |
| 5 | 超分/补帧未部署 | 视效师工具链（FlashVSR/RIFE） | P1部署 | 无 |
| 6 | 换装试穿未部署 | 服装岗工具（CatVTON，注意CC BY-NC非商用红灯） | P1部署 | 无 |
| 7 | AI标识合规未实装 | 2025-09-01已施行法规，全片强制 | **从"阶段1交付时实装"提前到 P0**：显式片头+元数据双标写进 qc_media/导出模板；clearance 台账建档（判例已认留痕=确权） | 无 |
| 7.1 | **引擎名与价格失真** | D2 会 404 / 预算误判 | 写 adapter 前查百炼控制台模型列表；**国内主站是 wan2.6 / wan2.7 不是 "Wan3.0"**，价格签约前逐项回查 | 无 |
| 8 | FLUX商用许可红灯 | 阶段3商单 | 商用前锚点图换商用模型 | 阶段3 |
| 9 | 长叙事一致性 | 行业公认"无模型彻底解决跨镜漂移"，生产环境必须**资产库+锚帧+人筛**三件套兜底；不存在"一键整剧" | 多候选+VLM质检+按镜选引擎缓解（并把"锚帧+人筛"制度化：见§12 全模态矩阵缺口行） | 持续 |
| 10 | **交付确定性（P0）** | 无技术门、无血缘、无幂等、无工时账本 | 审计件§4.1 P-0：jobs/qc_media/dit_ingest + 24fps/48kHz/-14LUFS 闭环 | 无（不等Key、不花钱，可立即开工） |
| 11 | **平台无视频/语音通道（P0）** | 工作台只能抽静图，静图比例失控 | 审计件§4.1 S5：`video_engine`/`tts` 节点 + `POST /api/jobs` | 无 |
> 【第五批复核】上表9条差距**仍然成立但优先级需重排**，且漏了更致命的4条：交付确定性无技术门、素材血缘不锁、异步作业无幂等、工作台只能生静图（是"86%静图"的上游结构原因）。另建议**撤销差距5里的 FlashVSR**（公开实测为云端A100级推理，本地价值不清）。详见 `docs/阶段0体检审计报告与规划修订v6.0.md` §2/§4.1。

### 4.3 结论（一句话）
**架构与路线已完备且经四批调研验证（19岗位全覆盖好莱坞职能+零返工手册v5.0），本地工具链四件套2026-09-26刚收官；当前状态还产出不了好莱坞级成片——差的是D2-D7打样执行+阶段1全片视频化，预计完成上述差距清单后达成目标。** 本地开源引擎（Wan2.2 5B）在写实人物特写上有客观天花板，已用"按镜选引擎（云端闭源主力+本地兜底）"策略对冲——这正是D7盲选拍板要验证的事。

---

## 5. 硬件与网络环境

| 项 | 值 |
|---|---|
| GPU | NVIDIA RTX 5070 12GB（Blackwell，需CUDA 12.8+；实测可跑：Wan2.2 5B视频/SDXL生图/MuseTalk fp16/Qwen3-VL-4B bf16全量） |
| 系统 | Windows 11 Home China ｜ Shell=PowerShell 5.1（**不支持`&&`**，链命令用`;`） |
| 项目盘 | `D:\ai_film_projects\`（剩余468GB，够用） |
| 记忆盘 | `c:\Users\LZH\.trae-cn\memory\` |
| 网络 | 国内网络，GitHub/HuggingFace直连不稳定。**稳定通道**：git→`https://ghfast.top/https://github.com/...`镜像；zip→`codeload.github.com`；模型→`hf-mirror.com`；pip→清华/阿里镜像（阿里对aria2多段Range会403，大文件用curl单连接+`--retry 100 -C -`；必要时hosts文件固定IP） |
| ffmpeg完整版 | `C:\Users\LZH\AppData\Local\Microsoft\WinGet\Packages\Gyan.FFmpeg.Shared_Microsoft.Winget.Source_8wekyb3d8bbwe\ffmpeg-8.1.2-full_build-shared\bin`（PATH里有TRAE自带的裁剪版ffmpeg，优先用Gyan版） |
| 基础Python | uv管理的CPython 3.11.15：`C:\Users\LZH\AppData\Roaming\uv\python\cpython-3.11-windows-x86_64-none\python.exe`（建venv用它） |

---

## 6. 目录结构地图（只列关键）

```
D:\ai_film_projects\
├─ start_server.bat            # 启动平台api_server（8190）
├─ start_comfyui.bat           # 启动ComfyUI（8188）
├─ start_账号注册向导.bat       # 已发给老板的账号注册向导（D0交接件）
├─ docs\                       # 全部规划文档（11份，见9.3文档索引）
│   ├─ 阶段0体检审计报告与规划修订v6.0.md   # 【第五批】手册v5.0的审计+修订件，接手必读
│   └─ （§9.3文档索引列全13份）
│   └─ AI交接全息文档.md        # ← 本文档
├─ roles\                      # 19岗位中15个已建文件夹+SOUL.md（缺composer/costume/props/colorist）
├─ tools\                      # 工具脚本（python，见9.2工具表）
│   └─ venv\                   # faster-whisper独立venv
├─ projects\雨夜寻猫\           # 当前唯一项目
│   ├─ screenplay\ storyboard\ shots\（4个mp4视频镜头+静图）
│   ├─ assets\ character_lock\ scene_lock\ k13_locked\
│   ├─ audio\（dialogue/bgm/ambient/sfx/voice_test各子目录）
│   └─ output\（雨夜寻猫_粗剪_v4.mp4=当前最新成片）
├─ comfyui\ComfyUI_windows_portable\
│   ├─ python_embeded\         # ComfyUI嵌入python（transformers 5.14.1+torch 2.13+cu130）——Qwen3-VL运行时
│   ├─ ComfyUI\output\audio\   # ACE-Step产出位置
│   └─ ComfyUI\custom_nodes\   # AnimateDiff-Evolved+VideoHelperSuite（Qwen3-VL节点包未装）
├─ musetalk\
│   ├─ venv\                   # MuseTalk独立venv（torch 2.8.0+cu128+transformers 4.39.2）
│   └─ code\MuseTalk-main\     # 已修复的MuseTalk代码（models\下权重齐、results\v15\冒烟产出）
├─ models\                     # Qwen3-VL-4B 已就位（8B 为P2候选，需实测16GB内存）
├─ tools\engines\(建中)        # D2 引擎 adapter 注册表：wan26/kling/h3 + mock
├─ web\                        # 平台前端（React）
└─ logs\ handoffs\ complete\ course\ skills\ tests\ assets\
```

---

## 7. 运行中的服务与启动方式

| 服务 | 端口 | 启动 | 说明 |
|---|---|---|---|
| ComfyUI 0.37.2 | 8188 | `start_comfyui.bat` | 生成主力；**实测2026-09-26在线，GPU占用186MiB/12231MiB** |
| 平台api_server | 8190 | `start_server.bat` | 岗位调度/handoff机制 |
| （2026-09-26第五批实测） | — | — | 8188 **在线**；8190 **离线**；GPU 186MiB/12231MiB、util 18%；`.env` 不存在（两Key未到）；仓库179项未提交 |
| （2026-09-27 A接手实测） | — | — | ⚠️ **8188 也已离线**（curl system_stats → http_code=000）；8190 离线；`.env` 仍不存在；仓库**196**项未提交（179→196）；`hermes\profiles` 实存 **9**；`tools\*.py` 内 `vram_scheduler` 引用 **0** 处 |

接手时先访问两个端口确认在线；不在线就双击bat（老板偏好GUI/双击，不喜欢命令行）。

---

## 8. 19岗位架构与SOUL.md状态

**组织图**（v4.0定稿+导演岗，2026-09-26拍板生效）：
```
【决策组】制片人 ─ 统筹/执行制片
【创作组】导演(第19岗新增) ─ 编剧 ─ 艺术总监 ─ 分镜师 ─ 作曲*
【美术资产组】角色设计师 ─ 服装造型师* ─ 置景设计师 ─ 道具师
【摄影生成组】摄影指导 ─ 灯光师 ─ 动画师
【后期技术组】视效师* ─ 调色师 ─ 剪辑师
【声音组】声音设计师
【全流程质控】场记/质检
```
（*=v4.0新增岗位）

**SOUL.md进度**：批1已完成9份新模板重写（导演/统筹/摄影指导/灯光/视效/场记/动画/艺术总监/编剧，六节结构：身份边界/职责/工具/交接物/质检自检/异常处理，对齐Anthropic Agent Skills规范）。**缺4个岗位文件夹**：composer（作曲）、costume（服装造型师）、props（道具师）、colorist（调色师）——计划批2/批3在阶段1前补齐，模板见手册第4.1节。

**主工序链**：编剧→(艺术总监风格审)→分镜师→[摄影指导开拍单+灯光师布光+美术组参考资产]→动画师生成→视效师技术增强→调色师→剪辑师→场记质检全程→统筹调度全程。声音支线：编剧台词→作曲BGM+声音设计师对白/音效/环境→终混→剪辑师合入。

**岗位边界要点**：导演管创意总指挥（导演阐述/Dailies初筛/试映反馈整合/表演方向），**老板保留最终剪辑权+绿灯决策**；角色设计师管"人长什么样"，服装造型师管"穿什么妆发"；作曲管"音乐"，声音设计师管"声音世界+终混"。

---

## 9. 工具链实测状态

### 9.1 已部署验证（四件套+基础层，全部2026-09-26实测）
| 工具 | 调用方式 | 运行时 |
|---|---|---|
| ACE-Step v1.5（BGM） | ComfyUI 8188原生节点（模板audio_ace_step_1_5）或tools\acestep_client.py | ComfyUI |
| faster-whisper 1.2.1（转写） | `& "D:\ai_film_projects\tools\venv\Scripts\python.exe" D:\ai_film_projects\tools\whisper_transcribe.py <音频> --model small --lang zh --outdir <目录>` | tools\venv（纯CPU） |
| Qwen3-VL-4B（质检） | `& "D:\ai_film_projects\comfyui\ComfyUI_windows_portable\python_embeded\python.exe" D:\ai_film_projects\tools\vlm_check.py <图...> --preset consistency --anchor <锚点图> --out <json>` | ComfyUI嵌入python |
| MuseTalk 1.5（口型） | 设`$env:PYTHONPATH="D:\ai_film_projects\musetalk\code\MuseTalk-main"`，cwd=该目录，`& "...\musetalk\venv\Scripts\python.exe" scripts\inference.py --unet_config ./models/musetalkV15/musetalk.json --inference_config configs\inference\<yaml> --use_float16` | musetalk\venv |
| Wan2.2 TI2V 5B（视频） | tools\wan22_client.py / wan22_shots_33_41.py | ComfyUI |
| SDXL生图/三视图/锁链 | tools\three_view_client.py / character_lock_writer.py 等 | ComfyUI |
| 【第五批复核】四件套可用，但**未接入生产闭环**：无逐镜头批跑、无阈值门、不进handoff、`tools` 内无任何云端适配器与显存锁引用 → 是"能力已具备、流程未通电" |

### 9.2 主要工具脚本（tools\，共30+个）
生成类：comfyui_client.py（ComfyUI通用客户端，**D2要扩多引擎版**）、wan22_client.py、three_view_client.py、tts_generator.py（edge-tts）、gen_bgm/gen_ambient/gen_sfx.py（程序合成音频）、acestep_client.py
处理类：build_mix.py（混音剪辑）、whisper_transcribe.py、vlm_check.py（质检）
管理类：api_server.py（8190平台）、handoff_manager.py、asset_manager.py、budget_manager.py（预算账本）、director_intent.py（导演意图）、scene_lock_writer/character_lock_writer.py、k13_version_tree.py（K13版本树）
维护类：d1_model_queue.py（模型下载队列，幂等可重启）

### 9.3 文档索引（docs\，全部保持最新）
| 文档 | 作用 |
|---|---|
| 好莱坞大片级对标与全阶段零返工执行手册.md | **执行总纲**（拍板15项+v5.0冻结+D0-D7序列+阶段1-3 SOP+合规清单） |
| 现实剧组对标v3.0总体规划.md | 策略层 |
| 团队架构v4.0-18岗位定稿与Agent技术栈升级方案.md | 组织层+Agent技术栈结论 |
| 阶段0体检审计报告与规划修订v6.0.md | **【第五批·必读·与手册冲突以此为准】**实测体检+修订路线+§13拍板十条 |
| v3.0技术附录-部署与接入手册.md | 工具细节
| 复刻OiiOii-技术选型与功能对标规划.md | 平台对标 |
| 团队架构重组v2.0 | 历史版本 |
| AI影视团队工作平台方案.md（36KB） | 平台原始方案 |
| 使用说明书.md / project_memory.md(旧) / 优化意见 | 早期文档 |
| 阶段0-账号注册交接指引.md | 老板注册指引 |
| 阶段0体检审计报告与规划修订v6.0.md | **【第五批·必读】**实测体检+职能/引擎/市场/合规/Agent技术审计+阶段路线修订+拍板单。与手册v5.0冲突处以此为准 |

---

## 10. 关键踩坑速查（Windows特有，全量见project_memory踩坑板块）

1. **mmcv/mmpose在Windows装不上**（无torch2.8+cu128预编译轮子）→ rtmlib+ONNX替代（MuseTalk的DWPose）
2. **face_detection包**：1adrianb原仓库已删除；PyPI同名包是错的 → 用Wav2Lip仓库内嵌模块+sfd.pth
3. **torch 2.6+**：torch.load默认weights_only=True，legacy权重报错 → 补weights_only=False
4. **qwen_vl_utils的file://**：Windows盘符路径会留前导斜杠 → content传裸路径
5. **中文路径**：cv2.imread读不了 → cv2.imdecode+np.fromfile；尽量整体用ASCII路径
6. **HF下载**：huggingface_hub 1.x默认xet协议绕过hf-mirror → 环境变量HF_HUB_DISABLE_XET=1
7. **pip镜像**：清华/阿里镜像可能缺新包 → 官方源`-i https://pypi.org/simple/`兜底
8. **aria2对阿里镜像**多段Range 403 → curl单连接+hosts固定IP
9. **PowerShell 5.1**：不支持`&&`；把stderr当日志打印属正常（NativeCommandError非真错误）
10. **ComfyUI升级**：git回退锚点=commit+pip freeze快照（已有备份机制）

---

## 11. 记忆文件体系（双轨，都要维护）

| 文件 | 路径 | 用途 |
|---|---|---|
| project_memory.md | `c:\Users\LZH\.trae-cn\memory\projects\-c-Users-LZH-AppData-Local-hermes--p2-95933d038ffd3d514624\project_memory.md` | 项目级：TODO板块+踩坑记录+进度（每轮对话更新） |
| user_profile.md | `c:\Users\LZH\.trae-cn\memory\user_profile.md` | 用户级：偏好/背景（有新偏好才追加） |
| 【第五批】**工作区镜像轨** | `D:\ai_film_projects\logs\_mem_mirror\` ：`project_memory.snapshot.md`(35.9KB/86行) + `user_profile.snapshot.md`(3.5KB/29行) + `HANDOFF_FROM_MCP_20260926.md`(接手快照) + `PENDING_MEMORY_APPENDS.md`(13条待回写) | 无C盘写权限时的替代轨（2026-09-26 只读复制）。**约定**：读以快照为准；写由有权限方回写C盘真文件后再刷新快照；快照未刷新前接手AI必须提醒老板"记忆与文档已分歧" |
| 本文档 | `D:\ai_film_projects\docs\AI交接全息文档.md` | 跨AI交接中枢（每轮对话按0.2契约更新） |

**注意**：记忆文件在AI运行环境里，老板看不到；本文档老板会拿在手里传递。**接手AI每次对话后两边都更新，内容保持一致。**

---

## 12. 当前待办（按优先级）

### 阻塞项（等老板）
### 【第五批新增·最高优先】P-0 确定性四件套（不花钱、不等Key、不动素材）
- [x] P-0a `tools/jobs.py`：异步作业账本（job_handle + prompt_id + **idempotency_key** + UNKNOWN态 + attempt）；断网重启先对账不发新任务 — ✅**已建成**（09-26 21:49，`idem` UNIQUE 约束 + 8 态含 unknown + `recover()` 对账 + selftest；`pipeline/jobs.db` 已生成）
- [x] P-0b `tools/qc_media.py`：技术门（黑帧/冻结/闪白/帧率漂移/**光流静止检测**/两遍loudnorm/真峰/分辨率码率/字幕安全区/AI标识元数据）→ **不过不得进老板预览** — ⚠️**部分建成**（09-26 23:52，阈值全读 `delivery_spec.json`；**已实现**帧率/分辨率/码率/采样率/声道/集成响度/真峰/LRA/黑帧/冻结/AIGC元数据/显式标识/血缘kind；**未实现**闪白、帧率漂移(仅容差)、字幕安全区；**光流静止被明确否决**（改由 dit_ingest 的 kind 判定）。另有 GBK 控制台打印 ✓/✗ 必崩的 bug（见 `logs/qc_v4_run.log`）待修）
- [x] P-0c `tools/dit_ingest.py`：素材血缘（引擎·模型版本·seed·prompt哈希·**参考图哈希**·产物sha256·光流分·质检分·花费）+ K13 一致性自校（现 `k13_locked` 有5条文件已删仍被引用） — ⚠️**部分建成**（09-26 22:40，已产出 `ditmap/file_index.jsonl`+`lineage.jsonl`+`summary.json`，能报 zero_byte/broken_refs/unreferenced；**实记字段少于文档宣称**：仅 sha256/bytes/kind/referenced_by + 镜头级 kind/clip/engine，**未落账**模型版本/seed/prompt哈希/参考图哈希/光流分/质检分/花费，且引用按**文件名**匹配而非哈希）
- [ ] P-0d 显存锁落地到脚本入口（独占创建 .lock + 心跳续租 + TTL），替换"插件装了但没人调"
- [ ] P-0e 平台加 `POST /api/jobs` + `GET /api/jobs/<id>`，**不要**再往 `/api/generate`（180s阻塞壳）塞长任务
- [ ] P-0f 三份开拍单按审计件§3.2补齐字段（导演5问：前中后景/光源四要素/动机运镜/视线跨轴/画内声点）
- [ ] **唯一前置事项：等老板回 §13 十项建议**

### 阻塞项（等老板）
- [ ] **老板账号注册**（阿里云+MiniMax，拿两个API Key）→ Key回来后AI写.env+最小调用验证——云引擎联调的前置条件

### 立即可做（不依赖Key）
- [ ] D2：**排在 P-0a 之后**。`tools/engines/` 注册表 + adapter 契约表（输入=开拍单字段全量；输出=产物+sha256+血缘+实际花费+**handle+幂等键**），**mock引擎可离线测试（零Key即可推进约70%工作量）**；真实模型别名以控制台列表为准（wan2.6/wan2.7，非"Wan 3.0"）
- [ ] 【第五批修正】D2 写 adapter 前必须先查控制台模型列表：国内百炼主站现役是 **wan2.6 / wan2.7**（wan2.6-i2v-flash 0.15-0.20元/秒无声），**文档里的"Wan 3.0"是国际站口径**；按别名硬编码会首调404
- [ ] **D3**：资产准备（三视图/锚点/Prop Sheet核对）+3-3/4-1/2-1开拍单三份定稿
- [ ] 批2 SOUL.md（服装造型师/道具师/作曲——阶段1前必须）
- [ ] 批3 SOUL.md（调色师+其余）
- [ ] 【第五批更优先】6份"空骨架"SOUL.md（director/cinematographer/gaffer/vfx_artist/script_supervisor/production_coordinator 目录内**只有SOUL.md**，无工具映射与工作流）→ 各出最小工具映射
- [ ] 【第五批降级】批2/批3 SOUL.md（composer/costume/props/colorist）：从阶段0前置**降级到阶段1前**。理由：运行层真实只有 **9个bot**（`hermes\profiles`），19岗其中10岗仍是文档，勿按19岗承诺产能

### 后续序列（阶段0收尾→阶段1）
- [ ] D4：3-3×三引擎生成+场记质检+MuseTalk口型（本地对照）
- [ ] D5：4-1×两引擎+2-1×两引擎
- [ ] D6：对比样片拼制（每引擎串烧+本地对照）+质检报告
- [ ] D7：老板盲选评审会→引擎拍板（实拍感35%/一致性30%/音轨15%/成本20%）
- [ ] 阶段1：全片v5逐镜头生成（86%静图→视频化，19岗位全员）
- [ ] 阶段2：调度器+质检流水线 ｜ 阶段3：商业化
- [ ] 清理项：k13_locked 0字节png（暂缓）；musetalk\models\_raw*冗余权重约4.6GB（队列重复下载所致，可删）

---

## 13. AI接手标准工作流（每轮对话执行）

1. 读本文档（接手首轮）→ 读 `docs/阶段0体检审计报告与规划修订v6.0.md` §0+§2 → 读两份记忆文件（读不到就读 `logs/_mem_mirror/` 副本+PENDING清单，并提醒老板回写）→ 检查8188/8190服务 → **跑 §5.0 只读体检**
2. 确认本轮任务（查第12节待办+老板最新指示）
3. 执行：技术不确定先验证再动手；长任务后台跑（模型下载/生成）并记录job日志路径
4. 完成后：更新project_memory.md+user_profile.md（如有新偏好）+**本文档第14节会话日志和第12节待办**
5. 回复末尾输出进度概览（第2.2节格式）

**红线**：不删历史记录；不跳过记忆读取直接干活；不确定不瞎猜（验证或问老板）；不烧钱（云API只按开拍单调用）；不改拍板结论（要改先请示老板）。**【第五批增补】红线四条**：①降级交付必须事前报备——**静图当真动算事故**（PPT感就是这么来的）；②账本必须能回答"这一镜花了多少现金、废了几个候选、返没返工"，答不出等于没账；③"已部署"只算到冒烟、冒烟只算到接入：**没进任务闭环的能力不得计入产能**；④工作区之外只读，任何跨区写入先请示。
**红线补充（第五批·MCP远程接手适用）**：①工作区之外**只读**——禁止在 `D:\ai_film_projects\` 之外创建/修改/删除任何文件；②未经老板同意不 commit/push、不改 `AGENTS.md`/`MEMORY.md`/`USER.md`/`config.yaml`、不删根目录 `.md`；③每次外部价格/模型名/许可结论在写入交付物或报价前必须回查一手来源（文档里已有3条过时项）；④降级交付（静图当真动用）算事故，必须先报备。

---

## 14. 会话日志（滚动追加区，接手AI每次对话后追加一行）

| 日期 | 会话内容与结论 |
|---|---|
| 2026-09-26 | **D1-P0四件套收官**：ACE-Step BGM（flac 48kHz 30s）/faster-whisper转写（台词吻合）/Qwen3-VL质检（verdict=pass）/MuseTalk口型端到端（双任务85帧，口型时序+人脸质量通过）全部实测通过；修MuseTalk三坑（face_detection包来源/torch.load权重/qwen_vl_utils路径）；手册D0-D7序列+技术附录A.1更新实测状态；创建本文档v1.0。阶段0完成度约75%，下一里程碑=D2多引擎客户端（等老板两Key）。 |
| （接手AI在这里追加） | |
| 2026-09-26 第五批（MCP远程接手·QwenWork） | 老板要求"先全面体检再推进"。产出：**5路外部调研 + 15条工作区内实测取证（全程只读、零素材改动、零花费）→ 新文档《docs/阶段0体检审计报告与规划修订v6.0.md》**（一页结论/证据表/职能审计/交付确定性10项/引擎市场现实/合规/工具链P0-P2/实拍感数值判据/Agent技术层/阶段路线修订v6.0/纠正假设11条/来源）。**核心结论：今天做不出好莱坞级成片，卡点是"静图交付+交付确定性缺失"，不是岗位不够；再加岗位不解决任何一条实测问题。** 关键实测：①18镜中16静图=88.9% ②交付体 720p/30fps/1.567Mbps/44.1kHz，低于自定审片档，24fps源被塞进30fps时间线（judder是隐性廉价来源）③`tools` 内 dashscope/minimax/kling/vram_scheduler **0命中**；④只有 `/api/generate`→SDXL(180s阻塞)，**工作台结构上只能生静图**；⑤运行层9个bot/1个GPU空转18%；⑥budget.json currency=CNY 实为无费率依据点数、spent 595 含测试夹具；⑦handoff 27条中16条为 seed_data 夹具。**⚠️纠正既有假设11条**（最要命：百炼国内是 wan2.6/2.7 不是 Wan3.0；FLUX.2 klein-4B虽Apache但13GB起、量化到12GB非零成本；H3开源33B需~64GB内存卸载-本机16GB不可行；edge-tts商用黄+限速→换CosyVoice3/Qwen-TTS；FlashVSR建议撤销；"-18~-24LUFS"应为-14 LUFS；"零返工"与"19岗=差异化"两句改口径；全片v5按实测价约¥114-135，旧记60-120偏低）。**阶段路线修订**：P-0确定性四件套(3-5天,零现金) → D2-D7打样(¥30内) → 阶段0.5 30-45秒高密度**动态**重制版(证明一次不像PPT) → 阶段1'全80秒 → 阶段2/3；LLM 不进生成链。**市场侧**：低端承制已崩到300-800元/分钟、纯AI片分账上限≈真人60%、<720p限流、TikTok保底500元/分钟需月产1000分钟(单人不可行)、爆款率0.47%——故建议阶段3走企业/政务定制(1000-3000元/分钟)+出海译制(25-80元/分钟)，并先投5-10个真实询价。**待老板回审计件§13十项**；记忆双轨因无C盘写权限改走 `logs/_mem_mirror/` 镜像轨并留 PENDING 回写清单13条（含 wan2.6 模型名、24fps/48kHz/-14LUFS 定稿、三件必用工具、光流静止判据、LLM不进生成链、许可红绿灯、市场单价、合规硬门槛、授权边界）。 |
| 2026-09-27（A接手·只读盘点轮·SeniorDeveloper） | **接手准备完毕（全程只读、零改动、零花费）**。老板下达十项交接指令，正式确立路线表述为「**Blender 白模占位（相机/灯光/动作/时间轴全定死并渲染）+ 大模型后期写实化（只执行不决定）**」。产出 7 份报告于 `logs/_handoff_A_20260927/`。**关键实测更正**：①**8188 也已离线**（旧记"在线"，curl→000）②在库变更 **196**（旧记179）③夜间已落地 **P-0a/b/c**（`tools/jobs.py`幂等账本 / `qc_media.py`技术门 / `dit_ingest.py`血缘）+ `pipeline/delivery_spec.json` v1.7（24fps/48kHz/-14LUFS）+ `timeline/master_v2.json`（19轨契约、**0条签核、647条阻塞**）+ `output/tech_v5/`（1080p 24fps 母版 + 48k 混音 + mkv）④`ditmap/summary.json` 自动实测 still_fallback **16/18**、dynamic **0.111**、zero_byte **6**、broken_refs **5** ⑤Blender 5.2.2 已解压但**白模零渲染**。**三张对照表**：对照A 22条=落实7/部分9/未落实5/改口径1（"没落实"全指向云引擎0接入+全片仍是静图）；对照B 20条=一致5/误导6/不一致9（最危险三条：手册§6.1与delivery_spec**两套交付口径**、§12待办未勾已完成项、文档组织架构与`contract_owners`新命名**两套并存**）；对照C=**量级差为主（约7成：源分辨率2.1×、码率5.1×、响度6.8 LU、真动比6.3×）+ 审美差3成且须独立补**。待替换词 4 处（工作区内3处 + C盘记忆1处）。**三项待拍板未执行**（合并/目录整理/待替换词）；**调研 R1 未达标**（9项未验证）→ 下轮先做 R2：12GB 白模→写实化实机实测 + 云引擎参数逐字核实 + 成本/许可补齐。 |
| 2026-09-27（A接手·拍板执行轮） | 老板答复「**确认**」→ 按 A1/A3/A4 方案执行，**全程可回滚、只新增不删除**。①**Checkpoint commit `183bace`**（222 文件入库，仓库 12M→39M）；执行前必须的处置：`.gitignore` 排除 `blender/`(1.3G)+`models/`(8.3G)+`musetalk/`+`projects/**/output|assets`+媒体文件（否则会吞 9.6GB），并对 `logs/` 开例外让交接报告与记忆镜像入库。②**合并**：`D:\AI影视团队\`→`_archive/legacy_20260727/`（robocopy /E 只新增，25 文件，排除 venv；重名 config/README/.gitignore 改名，**主目录同名文件未被覆盖**已验证）；原目录保留未动。③**目录整理**：探针 15 个→`tools/_probes/`；旧文档 5 份→`docs/_archive/`（现役 **8** 份）；旧日志→`logs/_archive/`；根遗留（vram_scheduler.py + handoffs + complete）→`_archive/root_legacy/`；output 旧产物 8 项→`output/_archive/`；ffmpeg 报错 8 个→`logs/ffmpeg_err/`；08-22 夹具 20 条→`projects/雨夜寻猫/handoffs/_fixtures/`（现役交接单剩 7）。④**待替换词归一**：工作区 3 处已改，`grep` 复查**归零**；C 盘记忆 1 处需老板代劳。⑤**明确未执行**：任何删除（根 `.md` / assets 空目录 / 0 字节日志 / `__pycache__`）一律未动，待二次确认；`web/workspace/` 因 `tools/api_server.py:188` 引用其 `workspace.html`（动它会破 `/workspace` 路由）**暂停移动**。详见 `logs/_handoff_A_20260927/A6_执行报告.md`。 |
| 2026-09-27（A接手·第三轮执行） | 老板下发七条裁决，全部执行完并**逐项带探针回显**。①**删除类 4 项已清**（根 `.md` 先备份至 `_archive/root_legacy/` 再删；assets 四空目录；0 字节日志；根 `__pycache__` 因沙箱禁止删除改为移出）②**`web/workspace/` 判定"仍在用"→ 不动**（四条证据：`api_server.py:185-188` 路由启用 + 运行时 `/workspace` http_code=200 + `start_server.bat:17` + showcase 三处链接）③C 盘记忆：PENDING 补至 **15 条**，待老板回写 ④**§13 十项落地清单已出**（`A7`，未改文档）⑤**R2 调研达标**：修正 R1 九处（可灵音频参数名=`audio`、元素参考=`refer`；Seedance 有 `generate_audio`；Wan2.6 未开源；fal 定价 $0.0024075/MP；Higgsfield 需 Blender 5.1+ 而本机 5.2.2 达标；3DREAL LoRA=other；即梦官方确认白模控制），仍缺 7 项（均标注原因）⑥**本机 12GB 实测**：Wan2.2 5B 跑通（832×480/49帧/127.1s/峰值 10596MiB/util 100%），**VACE 1.3B 跑不通**（权重仅 196MB/应 4.3GB）；页面文件峰值未采集 ⑦**免请示 7 项全做**：8188+8190 已起（均 200）、qc_media GBK 崩溃经复跑**证伪**（旧证据过时，已更正）、**P-0d 显存锁落地**（`tools/vram_lock.py` 6/6 自检通过，已包进 wan22_client）、15/15 SOUL 补 frontmatter、6 空骨架岗各补岗位卡、**audio_mix 两处真 bug 修复**（缺 `-y` 致母带停留旧版单声道；`alimiter` 缺 `level=disabled` 致响度被抬到 -12.28）→ 修复后母带 **-14.00 LUFS / TP -1.70 / 48kHz / 2ch / 80.000s 四项全达标**、**Blender 白模首次跑通**（48帧 960×540 24fps 2.000s，SSIM 首末帧 0.9856 证明相机动了；修 slotted-action 与无 FFMPEG 编码器两坑）。提交 `cc7899d`/`6053f53`/`beb58e3`。详见 `A8_第三轮执行报告.md`。 |

---

*本文档由Trae AI助手创建于2026-09-26。传递时请连同整个`D:\ai_film_projects\docs\`目录语境交接；老板持有最终解释权。*
