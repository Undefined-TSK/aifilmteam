# 调研 · R2 板块①b —— 质检链 × 音频链

> 调研员：`research-qc-audio`｜日期：2026-09-27（全文访问日期均为此日）｜仅外部公开资料，未读写项目、未生成、零花费
> 口径：证据等级分**一手 / 二手 / 未验证**；许可三态 🟢可商用 / 🟡有条件 / 🔴非商用，**代码许可与权重许可分开标**；成本统一折算（积分一律折元，禁止积分横比）

---

## 〇、调研员如实自评覆盖度（先看这个）

| 状态 | 子题 |
|---|---|
| ✅ **已实际检索**（21 项） | 光流 Farneback 参数 / DIS·RAFT·GMFlow 可行性 / 光流阈值出处 / freezedetect / signalstats / ebur128+loudnorm 两遍 / alimiter / ArcFace 阈值出处 / NIST FRVT / Qwen3-VL 节点与失败模式 / SyncNet LSE-C 出处 / DeepEval·promptfoo / TTS 三家许可 / edge-tts 条款与限速 / 豆包价格与条款 / MiniMax 价格 / Stable Audio·MMAudio·AudioLDM2 / ACE-Step 许可 / Demucs·UVR5 / `afir` / 环境三层法 / 免费素材库许可 |
| ❌ **未检索（一律不作结论）** | ① `mpdecimate` 的 `hi/lo/frac` 具体参数 ② **IR 素材来源（OpenAIR / EchoThief）** ③ **Suno / Udio 价格与商用条款** |

> 上一版我只用了 1 分 43 秒就交了"看起来完整"的报告，被我自己退回重做。这一版每条都带出处，未检索项明确标"未验证"。

---

## 1. 光流探针（"真动 vs 静图"的判据）

| 结论 | 等级 | 出处 | 反方证据 | 处置 |
|---|---|---|---|---|
| Farneback 起手参：`pyr_scale=0.5, levels=3~5, winsize=15~21, iterations=3, poly_n=5, poly_sigma=1.1~1.2, flags=0` | 一手(OpenCV)+二手 | thelinuxcode.com/opencv-dense-optical-flow | **亮度恒定假设：闪白/曝光跳变使光流失真**；无纹理区出噪声 | ✅ 但**先做亮度归一化** |
| 12GB 可行性：Farneback 纯 CPU ✅ / DIS ✅ / RAFT ≈8.2GB(720p) ⚠️需降采样 / GMFlow ✅ | 一手(MathWorks、princeton-vl/raft)+二手 | mathworks.com/help/vision/ref/opticalflowraft.html | RAFT 官方基于 torch1.6/cuda10.1，有兼容债 | ✅ 主 Farneback，GMFlow 交叉校验 |
| **⭐「背景光流中位速 ≥2 px/帧」在业界无任何出处** | **未能验证**（已搜 Google / arXiv / CSDN / 知乎） | — | 近邻做法是 GMFlow 的 `S_Move`(>0.5 才保留) 与 EPE 指标；**"像素/帧"非尺度不变**，业界建议按帧对角线归一化 | ❓ **缺本机分辨率的 golden 基线，必须自建标定** |

---

## 2. ffmpeg 检测项（可直接复制，实测于 ffmpeg 8.1）

```bash
# 冻结检测（本项目判"无 >0.5s 冻结"，故 d=0.5；默认是 2s）
ffmpeg -i in.mp4 -vf "freezedetect=n=-60dB:d=0.5" -map 0:v:0 -f null - 2>&1 | grep freezedetect

# 闪白：只抽样中心区 + 落 CSV（signalstats 极慢，切勿全片）
ffmpeg -i in.mp4 -vf "crop=iw/2:ih/2:iw/4:ih/4,signalstats,metadata=mode=print:file=stats.csv" -f null -

# ebur128 测量（I / TP / LRA / thresh），Summary 段即结果
ffmpeg -i in.wav -filter_complex ebur128=peak=true -f null - 2>&1 | sed -n '/Summary/,$p'

# loudnorm 两遍法 · 第一遍（拿 measured_*）
ffmpeg -i in.wav -af "loudnorm=I=-14.0:TP=-1.5:LRA=8:print_format=json" -f null -

# loudnorm 两遍法 · 第二遍（把第一遍的 measured_* 填进来）
ffmpeg -i in.wav -af "loudnorm=I=-14.0:TP=-1.5:LRA=8:measured_I=X:measured_TP=Y:measured_LRA=Z:measured_thresh=W:offset=O:linear=true:print_format=summary" -ar 48000 -c:a pcm_s24le out.wav

# 限制器（防二次抬电平）
alimiter=level_in=1:level_out=1:limit=0.84:attack=5:release=50:level=disabled
```

| 结论 | 等级 | 出处 | 反方证据 | 处置 |
|---|---|---|---|---|
| `freezedetect` 元数据 `freeze_start/duration/end`；**`d` 默认 2s，必须改 0.5** | 一手 | ffmpeg-cvslog 2018-11 | 基于全帧 MAFD，**整幅缓变可能漏判** | ✅ |
| `signalstats` 给 YMIN/YAVG/YHIGH/YMAX/SATAVG | 一手 | FFmpeg `vf_signalstats.c` | **实测 1080p30/120s 耗 29.56s——比一次完整编码还慢** | ⚠️ **必须抽样** |
| **`alimiter` 必须 `level=disabled`** | 一手 | stackoverflow.com/q/41255197 | 默认 enable 会把电平抬回 0dB | ✅ |
| **`loudnorm` 的 `linear=true` 会因缺 measured / 超 TP / LRA 超限而静默回退 dynamic** | 一手（8.1 实测） | ffmpeg-cookbook.com | 回退后动态压缩改变听感，且**不报警** | ✅ 第二遍加 `print_format=summary` **复核实际模式** |
| ebur128 两遍：先测、再 `loudnorm` + `measured_*` 线性归一 | 一手 | salivity.github.io | **少写 `-ar 48000` 会因内部 192k 上采样改变采样率** | ✅ **强制 `-ar 48000`** |
| `mpdecimate` 参数 `hi/lo/frac` | **未能验证（未检索）** | — | — | ❓ |

---

## 3. 人脸一致性

| 结论 | 等级 | 出处 | 反方证据 | 处置 |
|---|---|---|---|---|
| InsightFace `buffalo_l`（RetinaFace + ArcFace R50，512d），12GB 可跑，`det_size=(640,640)` | 一手(repo)+二手 | cloud.baidu.com/article/3636180 | 需 `onnxruntime-gpu`，依赖链长 | ✅ |
| **⭐「余弦 ≥0.75」无行业基准**；InsightFace buffalo_l 在 LFW 的**官方推荐阈值是 0.363** | 二手+一手 | geek-blogs.com/blog/insightface-linux | **NIST FRVT Part3：固定阈值不通用，假拒率跨人群差 10–100 倍** | ⚠️ **当作"内容一致性严阈值"可以，但必须自证标定，不能声称是行业标准** |
| 侧脸/遮挡：**仅 |yaw| < 45° 且有检出的帧参与，多帧取最高** | 二手（kahma 实验室） | **ArcFace seed 方差 σ≈0.09，相邻 seed 跨 0.18–0.42 → 单帧完全不可信** | ✅ **必须多帧投票** |

---

## 4. VLM 质检（Qwen3-VL-4B）

| 结论 | 等级 | 出处 | 反方证据 | 处置 |
|---|---|---|---|---|
| 节点包：`ComfyUI-Qwen3-VL`(xuchenxu168)、`ComfyUI-QwenVL`(aistudynow)、`ComfyUI-GGUF-VLM`(walke2019)、**`ComfyUI-QwenVL-MultiImage`（多图对比首选）** | 一手 | deepwiki.com/xuchenxu168/ComfyUI_Qwen3-VL/4-user-guide | 部分包需 `transformers>=4.57.1` + `flash-attn`，**Win 下编译慢** | ✅ |
| 显存：4B-FP16 ≈8GB / 4B-FP8 ≈4GB / 8B-FP8 ≈8GB / **8B-FP16 ≈16GB（超 12GB）** | 一手（README 表） | 同上 | 8B 需 offload 到内存，**与其它模型抢 16GB 内存** | ⚠️ **4B 为主**；8B 仅 FP8 + 降 max_pixels |
| **失败模式**：视觉标签误判 + CoT 与输出矛盾；**遮挡/空间推理弱**（"树在前"8B/30B 同错）；**高密度计数 exact = 0%**；**语言先验覆盖视觉** | 一手（arXiv 2607.06420 / CVPR2026） | arxiv.org/html/2607.06420 | 8B"过度推理"反比非推理模式错更多 | ⚠️ **只做二值判读** |
| 适用：**"同一只猫吗 / 有无未声明第三人 / 道具状态" ✅**；"视线跨轴 / 光源方向变" ⚠️ | 同上 | hf.co/posts/EpsilonGreedyAI | 4B 的遮挡与坐标推理同样不可靠 | ✅ **强约束 JSON + 多帧 + 人工抽检** |

---

## 5. 口型同步

| 结论 | 等级 | 出处 | 反方证据 | 处置 |
|---|---|---|---|---|
| 指标 **LSE-C（=Sync-C，越高越好）/ LSE-D（越低越好）**，由 SyncNet 5 帧窗口计算 | 一手（Wav2Lip 论文） | purehost.bath.ac.uk/.../Wav2Lip_ACMMM_20_camera_ready_2_.pdf | **SyncNet 公开权重仅英语训练** | ⚠️ **中文需自建基线** |
| 基准：**真人同步 LSE-C ≈ 6.7–8.8；Wav2Lip+GAN ≈ 7.2–7.8；随机/未同步 ≈ 0.9–2.5** | 一手（同论文 Table 1/2） | 同上 | 数字随 LRW/LRS2/LRS3 数据集波动 | ✅ |
| **⭐「阈值 ≥5」无官方定义**，它落在"随机 2 / 真人 7"之间 | **未能验证**（已搜 arXiv 与 Wav2Lip repo） | — | LSE-C 对极端姿态/压缩不敏感 | ⚠️ **自标定** |
| 本地：`joonson/syncnet_python`，12GB 可跑 | 一手 | github.com/joonson/syncnet_python | 需 S3FD 检测器，装链长 | ✅ |

---

## 6. 回归机制

| 结论 | 等级 | 出处 | 反方证据 | 处置 |
|---|---|---|---|---|
| DeepEval `GEval`（自然语言 rubric）+ `assert_test`，pytest 原生 | 一手 | deepeval.com | **GEval 非确定性，单次分数无意义** | ✅ |
| promptfoo：YAML + `llm-rubric`，适合小团队 | 二手 | birjob.com | 同样有 judge 抖动 | ✅ 备选 |
| golden 集建法：真实失败 20 例 → 3–5 维度 → 每维独立 judge → **多次采样** → 与人工对齐（<80% 一致就改 rubric） | 二手（Anthropic 建议转述） | 同上 | upfront 设计的价值低于"真实失败累积" | ✅ |

---

## 7. 对白 TTS

| 候选 | 代码许可 | 权重许可 | 12GB+16GB | 成本口径 | 中文情感 | 处置 |
|---|---|---|---|---|---|---|
| **CosyVoice 3**（公开 checkpoint = **0.5B**） | 🟢 Apache-2.0 | 🟢 **Apache-2.0（含权重）** | 0.5B 需 6–8GB | 自托管 ≈ 0 | 指令控制情绪/哭腔，**18 方言** | ✅ **首选** |
| **GPT-SoVITS** | 🟢 MIT | 🟢 **MIT** | 8GB+ | ≈ 0 | 5s 样本克隆 80–95% 相似；自然度稍弱 | ✅ **备用** |
| F5-TTS 330M | 🟢 MIT | 🔴 **CC-BY-NC（多源冲突，需核）** | 6GB+ | ≈ 0 | 无显式情感控制，长文本偶发"核嗓" | ❌ 权重存疑 |
| Fish Speech 1.6 | 🟢 BSD-3 | 🔴 CC-BY-NC-SA-4.0 | 6GB+ | ≈ 0 | 有情感 tag，但偶带底噪 | ❌ |
| IndexTTS2（B站） | 🟡/🔴 **许可源冲突** | 同左 | FP16 ≈7.8GB | ≈ 0 | 7 类情感独立控制 + 时长控制 | ⚠️ 先核许可 |
| 火山/豆包语音合成 2.0 | 🟢（服务） | — | 云端 | **0.3 元/千字符** | 9.2/10，指令控情绪 | ⚠️ **商用需书面许可** |
| MiniMax `speech-2.8-hd` | 🟡 | — | 云端 | **0.72 元/千字符** | 32 语言，情感 tag | ⚠️ |
| ElevenLabs | 🟡（付费层可商用） | — | 云端 | **0.45 元/千字符** | 中文 8.8/10 | ⚠️ 需代理 |
| **edge-tts** | 🔴 | — | 本地免费 | 0 | — | ❌ |

**豆包商用条款原文**：火山《语音服务》专用条款 2.2 授予"非排他、不可转让或再许可、有时间限制、可撤销、**仅特定国家/地区自行使用**"之权利；生成内容含火山授权内容（音色等）须"完整使用"，**不得单独使用或授权他人单独使用**。《豆包助手专区条款》2.2(1)：「如您就本服务进行商业使用或…获得收益，则您需要**事先获得火山引擎的书面许可**」→ 🟡 有条件。

**edge-tts 违规条款原文**：微软《可接受的使用政策》禁止「使用任何**自动化过程或服务**来访问或使用本服务，例如 BOT、蜘蛛程序或定期缓存 Microsoft 存储的信息」；《Microsoft Services Agreement》禁止「**web scraping, web harvesting, or web data extraction**」与「unreasonably large load… robots, spiders, scrapers or other automated means」。**限速**：无官方公布数值；实测同 IP 高频请求触发 **403**，社区缓解 = 并发改 1、每次暂停 5s。微软 Q&A 官方贡献者称**无公开商用文档**，需自行咨询法务。

---

## 8. SFX

| 候选 | 代码 | 权重 | 可行性 | 反方证据 | 处置 |
|---|---|---|---|---|---|
| Stable Audio Open 1.1B / Open Small 341M | 🟢 | 🟡 Stability AI Community License（**年营收 < $100 万免费商用**） | 44.1kHz stereo；Small 仅 11s | 超阈值需企业授权；**不支持真实人声** | ⚠️ 条件选 |
| MMAudio 157M（CVPR2025） | 🟢 MIT | 🔴 CC-BY-NC-4.0 | ≈6GB，8s/1.2s | 偶生不可懂人声；8s 固定 | ❌ 仅内部预览 |
| AudioLDM 2 | 🟢 | 🔴 CC-BY-NC-SA | 16kHz mono | **2024 起上游停更** | ❌ |
| ElevenLabs SFX | 🟡（付费层 royalty-free） | — | 云端 | 40 credits/秒，自动时长 200 credits/次 | ⚠️ 应急 |
| Freesound（**筛 CC0**）/ 99sounds / Mixkit / freesfx | 🟢 CC0 或免费商用免署名 | — | 本地 | **Freesound 是 CC0/CC-BY/CC-BY-NC 混合，误用即侵权** | ✅ 底库 |

---

## 9. BGM

| 结论 | 等级 | 出处 | 反方证据 | 处置 |
|---|---|---|---|---|
| **ACE-Step 1.5**：官方页 / ComfyUI Wiki / awesome 列表标 **Apache-2.0，代码+权重可商用** | 一手（官方页）+二手 | ace-step.github.io/ACE-Step-1.5 | ⚠️ **同项目 HF 权重卡写 "weights: MIT (same as upstream)"，与 Apache-2.0 不一致**；两者都宽松但**需项目方澄清** | ⚠️ 商用前**书面确认许可文本** |
| 显存：DiT **< 4GB**（可 CPU offload）；**LoRA 训练需 16GB VRAM** | 一手+二手 | nicolas-riquier.com | **16GB > 本机 12GB → LoRA 在本机不可行** | ⚠️ **只推理** |
| 变体 Base/Turbo/XL(5B DiT)，48kHz stereo | 一手（HF 模型卡） | huggingface.co/ACE-Step/acestep-v15-xl-base-diffusers | 社区评：**提示词遵循差、歌词对齐弱、中文 rap 弱、vocal 粗糙** | ✅ 需人工挑选 |
| Suno / Udio 价格与条款 | **未能验证（未检索）** | — | — | ❓ |

---

## 10. 音频后处理链

| 结论 | 等级 | 出处 | 反方证据 | 处置 |
|---|---|---|---|---|
| 母带：`loudnorm` 两遍 → `alimiter(level=disabled)` → `-ar 48000 -c:a pcm_s24le` | 一手（8.1 实测） | ffmpeg-cookbook.com | 顺序错会二次抬电平 | ✅ |
| **⭐ per-shot 混响改用 ffmpeg `afir` 卷积真 IR，替换旧的 `aecho`** | 一手（`af_afir.c`，LGPL） | github.com/FFmpeg/FFmpeg/blob/master/libavfilter/af_afir.c | **`aecho` 是固定延迟回声、不是空间混响 —— 这正是旧项目 8 条对白欠账的根因** | ✅ **强推** |
| Demucs v4 `htdemucs` | 🟢 MIT | 🟢 MIT（同 repo） | **只分 vocals/drums/bass/other，不匹配我们要的"对白/环境/SFX"四分离**；Meta 已归档、现仅 bugfix | ⚠️ **仅音乐轨** |
| UVR5 | 🟢 GUI 代码 MIT | ⚠️ **第三方模型许可各异，需逐个核** | 模型来源混杂（MDX/VR/Demucs） | ⚠️ |
| Demucs vs UVR5 的 SDR 对比 | 二手（**多源冲突**） | tsight.io vs hqwc.cn | 两数字量纲/测试集不同，**不可直接比** | ❓ 需自测 |
| IR 素材来源（OpenAIR / EchoThief） | **未能验证（未检索）** | — | — | ❓ |

---

## 11. 环境分层

| 结论 | 等级 | 出处 | 反方证据 | 处置 |
|---|---|---|---|---|
| 三层法 = **远景低鸣(bed/atmos) + 中景硬雨/动作(effects/mid) + 近场细节(foley/accent)**；"≥3 层"有充分行业依据 | 一手（Sound on Sound）+二手 | soundonsound.com/techniques/sound-design-visual-media | 空镜可只留 1 层；**层多 ≠ 好，重复铺底会糊** | ✅ 用于补旧项目 10 项缺失 |
| 可商用素材：Freesound(筛 CC0) / freesfx / 99sounds(24bit WAV 免署名商用) / Mixkit / Adobe SFX Pack | 二手 | linraw.com | 免费库质量参差需听筛 | ✅ |

---

## 【表一】决策建议汇总表

| 候选 | 能力 | 12GB+16GB | 成本 | 商用许可(代码/权重) | 集成难度 | 风险 | **建议** |
|---|---|---|---|---|---|---|---|
| Farneback 光流(CPU) | 中 | ✅ | 0 | 🟢/— | 低 | 阈值需自标 | ✅ |
| RAFT / GMFlow | 高 | ⚠️/✅ | 0 | 🟢/— | 中 | 显存/兼容 | ⚠️ 交叉校验 |
| ffmpeg 四件套 | 高 | ✅ | 0 | 🟢/— | 低 | signalstats 极慢 | ✅ |
| InsightFace buffalo_l | 高 | ✅ | 0 | 🟢/🟢 | 低 | 单帧不可信 | ✅ 多帧 |
| Qwen3-VL-4B | 中 | ✅ | 0 | 🟢/🟢 | 中 | 视觉推理误判 | ✅ 二值判读 |
| Qwen3-VL-8B-FP8 | 高 | ⚠️内存 | 0 | 🟢/🟢 | 中 | 抢内存 | ⚠️ 条件选 |
| SyncNet LSE-C | 中 | ✅ | 0 | 🟢/— | 中 | 中文偏置 | ⚠️ 自标定 |
| DeepEval GEval | 中 | ✅ | 0 | 🟢/— | 低 | 非确定性 | ✅ |
| **CosyVoice 3 (0.5B)** | 高(中文) | ✅ | 0 | 🟢/🟢 Apache-2.0 | 中 | 公开权重非 1.5B | ✅ **首选** |
| GPT-SoVITS | 高(克隆) | ✅ | 0 | 🟢/🟢 MIT | 中 | 参考音频合规 | ✅ 备用 |
| F5-TTS | 高 | ✅ | 0 | 🟢/🔴 权重存疑 | 低 | 许可冲突 | ⚠️ 先核权重 |
| 火山豆包 TTS | 高 | 云端 | 0.3 元/千字符 | 🟢服务/🟡**商用需书面许可** | 低 | 需授权 | ⚠️ 条件选 |
| MiniMax HD | 高 | 云端 | 0.72 元/千字符 | 🟡 | 低 | 异步队列 | ⚠️ |
| **edge-tts** | 中 | ✅ | 0 | 🔴 | 低 | **违反自动化访问条款** | ❌ |
| Fish Speech / AudioLDM2 / MMAudio | 高 | ✅ | 0 | 🟢/🔴 | 中 | 非商用 | ❌ |
| Stable Audio Open | 中高 | ✅ | 0 | 🟢/🟡(<$100万) | 中 | 收入门槛 | ⚠️ 条件选 |
| ACE-Step 1.5 | 高 | ✅(<4GB) | 0 | 🟢/🟢(文档 Apache2.0) | 中 | **许可文本不一致** | ⚠️ 先核许可 |
| **`afir` + CC0 IR** | 高 | ✅ | 0 | 🟢/⚠️ | 中 | IR 逐条核 CC | ✅ **强推（治旧欠账）** |
| Demucs v4 | 高(音乐) | ✅ | 0 | 🟢/🟢 MIT | 低 | 轨类型不匹配 | ⚠️ 仅音乐 |

## 【表二】未验证清单

| 项 | 为什么没验 |
|---|---|
| **光流 2px/帧 判据** | 已搜 Google/arXiv/CSDN/知乎，**无任何出处**；缺本机分辨率 golden 基线 |
| **ArcFace 0.75** | 已搜官方与 NIST，**无行业基准**（官方推荐 0.363） |
| **口型 Sync-C ≥5** | 已搜 arXiv 与 Wav2Lip repo，**无官方定义**；缺中文对白基线 |
| `mpdecimate` 参数 hi/lo/frac | **未检索** |
| IR 素材来源（OpenAIR / EchoThief） | **未检索** |
| Suno / Udio 价格与商用条款 | **未检索** |
| F5-TTS 权重许可 | 多源冲突（MIT vs CC-BY-NC），需读官方 repo/LICENSE 逐字 |
| IndexTTS2 许可 | 源冲突（Apache2.0 vs Custom） |
| ACE-Step 许可文本 | 文档标 Apache2.0、HF 权重卡标 MIT，需项目方澄清 |
| 豆包商用书面许可的申请入口与是否收费 | 条款已读（需书面许可），未查申请流程 |

## 【表三】反方证据汇总

| 主题 | 反方证据 |
|---|---|
| Farneback | 亮度恒定假设在闪白下失效；像素/帧非尺度不变 |
| RAFT | 官方基于 torch1.6/cuda10.1；大图 OOM |
| signalstats | 实测比一次全编码还慢（1080p30/120s → 29.56s） |
| loudnorm | `linear` 会**静默回退** dynamic |
| alimiter | 默认 level 会二次抬电平 |
| ArcFace | NIST FRVT 固定阈值跨人群假拒率差 10–100×；seed 方差 σ≈0.09 |
| Qwen3-VL | CoT 与输出矛盾；遮挡/空间推理错；高密度计数 0%；越推理越错 |
| SyncNet | 仅英语训练；对极端姿态/压缩不敏感 |
| DeepEval GEval | 非确定性，单次无意义 |
| CosyVoice3 | 公开权重 0.5B ≠ 论文 1.5B；仓库多次换 org 致固定 URL 失效 |
| edge-tts | 违微软自动化访问条款；全球 403；定位无障碍功能，**无公开商用文档** |
| 豆包 | 专区条款要求商用**事先书面许可**；授权内容不得单独使用 |
| MMAudio / AudioLDM2 / FishSpeech | 权重非商用 |
| ACE-Step | Apache-2.0(文档) 与 MIT(权重卡) 不一致；质量波动大 |
| Stable Audio | 不支持真实人声；Open Small 仅 11s |
| Demucs | Meta 已归档、仅 bugfix；只分音乐 stem |
| UVR5 | 第三方模型许可各异 |
| Freesound | CC0/CC-BY/CC-BY-NC 混合，误用即侵权 |
| 环境层 | 层多 ≠ 好，重复铺底会糊 |
