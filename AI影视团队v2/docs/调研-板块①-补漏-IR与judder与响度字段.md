# 调研 · 板块① 补漏 —— IR 素材 / judder 检测 / loudnorm 字段

> 调研员：`fix-ir-sources`｜日期：2026-09-27（全文 URL 访问日期均为此日）
> 证据等级：一手 = 官方站/官方仓库/LICENSE；二手 = 媒体/博客/论坛/学术列表；未验证 = 写明原因
> 任务来源：板块① 验收时老板拍「补 IR 素材来源；`mpdecimate` 参数直接实测」

---

## ① IR（脉冲响应）可商用来源

### 1.1 库对照表

| 库 | URL | 许可三态 | 商用 | 署名 | 类型 | 格式/采样率 | 体量 | 等级 |
|---|---|---|---|---|---|---|---|---|
| **OpenAIR** | `openairlib.net`；镜像 `www.openair.hosted.york.ac.uk`（**2026-09-27 实测两个域均返回 "Account Suspended"**） | 🟡 CC BY（列表记 4.0） | 允许（须署名） | **必须** | 教堂/大厅/仓库/隧道/峡谷/森林/楼梯，含室外 | Ambisonic B-format / stereo / 5.1，WAV | >500 IR，47 数据集 | 一手（站点挂起）+二手 |
| **EchoThief** | `echothief.com/downloads` | 🔴 **无任何 CC/授权条款**，站点仅标 "copyright 2013–2026 Dr. Chris Warren" | **未获授权 → 不可** | 未定义 | 洞穴/天桥/楼梯井/混凝土管/冰川/堡垒/潜艇/教堂穹顶 | WAV | >100 空间 | 一手（站点无许可）+二手（SDSU 报道称已授权 Sony / Bethesda → 说明属**需单独授权**） |
| **BUT Reverb DB** | 经 Graphi07 列表链接 | 🟢/🟡 **CC BY 4.0** | 允许 | **必须** | 8 个房间（含小房间），偏语音/ASR | mono WAV，16/48kHz | 1300+ RIR | 二手 |
| MIT IR Survey | 经 Graphi07 列表链接 | ⚠️ 许可 "Unspecified" | **未能验证** | 未能验证 | 271 个真实场所 | mono WAV | 271 RIR | 二手 |
| **C4DM RIR** | 经 Graphi07 列表链接 | 🔴 **CC BY-NC-SA** | **禁止** | — | 3 个大空间 | mono / B-format | 468 RIR | 二手 |
| ACE Challenge | 经 Graphi07 列表链接 | 🟡 CC BY-ND 4.0（**禁演绎**） | 允许但有风险 | 必须 | 7 房间 1/2/3/5/8/32 通道 | 多通道 | 少量 | 二手 |
| **MeshRIR** | `github.com/sh01k/MeshRIR` | 🟢/🟡 CC BY 4.0 | 允许 | 必须 | **单一中等混响房间**密网格 | WAV/mat，48kHz | ~200,000 RIR | 一手（仓库 LICENSE/README） |
| Aachen IR DB | `openslr.org/20` 镜像 | ⚠️ **冲突**：Graphi07 记 "MIT"，OpenSLR 镜像页标 "Not stated in the download" | 未能验证 | 未能验证 | 5 环境含小房间/教堂，344 双耳 | 双耳 WAV | 344 RIR | 二手（两条互斥来源） |
| **Freesound（CC0 过滤）** | `freesound.org`（筛 CC0） | 🟢 **CC0** | 允许 | **无需** | 用户上传的房间/街道/楼梯等 | 多为 WAV | 需筛 | 二手（多来源一致） |
| Zenodo 学术 IR（Aalto 耦合房间 / ISOBEL / OK5） | `zenodo.org` | 多为 CC BY（**未逐条核实**） | 未能验证 | 未能验证 | 办公/会议室/厨房/楼梯/礼堂 | SOFA/WAV，48kHz | 数 GB–数十 GB | **未验证**（未逐一打开许可字段） |

### 1.2 三类场景适配（给我们三个场景用）

| 我们的场景 | 可用 IR | 备注 |
|---|---|---|
| **雨夜街道（中雨）** | ⚠️ **免费库中"城市街道专用 IR 稀缺"**（未找到明确 CC0 城市街道库）。可用 OpenAIR 室外类 `Troller's Gill`（石灰岩峡谷，RT60≈0.4s @1kHz）、`Koli National Park`（森林）——均属**自然环境非城市街** | ⭐ **正确做法：IR 只负责空间，雨声作为独立环境层叠加——不要把雨录进 IR** |
| **窄巷（有混响）** | OpenAIR `Innocent Railway Tunnel`、`Stairway, University of York`；EchoThief `concrete tube / underpass / Echo Bridge`（**受其许可限制，不可用**）；Aachen 含楼梯 | — |
| **出租屋室内（小空间、闷）** | **BUT Reverb DB（8 房间）**、Aachen（含小房间）、ISOBEL（4 房间）、MIT IR Survey、Freesound CC0 房间 IR | — |

### 1.3 ⭐ 坑（本条最值钱）

**① CC BY 的署名义务是强制的**。CC BY 4.0 官方原文（一手）："You must give appropriate credit, provide a link to the license, and indicate if changes were made … **in any reasonable manner**"。
→ **CC BY 素材在交付影片里署名是强制义务**；片尾字幕或随片署名文件（"any reasonable manner"）均可。**CC0 无署名义务。**

**② 最典型的误认：EchoThief 被普遍当成"免费 IR"。**
production-expert、Reason Studios 博客、多个 KVR/Cakewalk 帖一律列为 "free IR"（二手），**但其站点无任何授权条款，仅声明版权** → **结论以官方站点为准：不可商用**。

**③ 其余红黄灯**：C4DM = **CC BY-NC-SA** 🔴 禁止商用；ACE = CC BY-ND，把 IR 卷积进成片是否构成"演绎"存在解释风险 🟡。

### 1.4 结论①

| 结论 | 处置 |
|---|---|
| **主库：BUT Reverb Database（CC BY 4.0）** | ⚠️ **条件用** —— 条件 = **片尾/随片署名 + 附许可链接 + 标注是否改动** |
| **备选：OpenAIR（CC BY）** | ⚠️ 条件用（同上署名义务）。**现实障碍：2026-09-27 主站与 York 镜像均 "Account Suspended"**，须另寻镜像或联系 York AudioLab |
| 需**零署名**时 | Freesound 按 **CC0** 过滤 → 🟢 可用 |
| **❌ 不可用** | **EchoThief**（除非单独授权）；**C4DM（BY-NC-SA）** |

**落地命令（承接 `afir` 方向）**：
```bash
ffmpeg -i dry.wav -i ir.wav -filter_complex "[0:a][1:a]afir=dry=10:wet=10" -c:a pcm_s24le out.wav
```

---

## ② judder / 错帧 检测的正确做法（独立验证了我们的 `mpdecimate` 结论）

根因认定：**`mpdecimate` 按像素差判重复，不测时间戳**；慢运镜下相邻帧天然相似 → 我们实测的 48→20 帧属**误删**，不是真重复帧。

### ✅ 推荐命令（完整可复制）

```bash
# 1) 帧率/时长/时间基
ffprobe -v error -select_streams v:0 \
 -show_entries stream=r_frame_rate,avg_frame_rate,time_base,nb_frames,duration \
 -of default=nw=1 input.mp4

# 2) 精确帧数（与 round(时长×fps) 对比）
ffprobe -v error -select_streams v:0 -count_frames \
 -show_entries stream=nb_read_frames -of csv=p=0 input.mp4

# 3) ⭐ 逐帧时间戳间隔分布（核心质量门）
ffprobe -v error -select_streams v:0 \
 -show_entries frame=best_effort_timestamp_time -of csv=p=0 input.mp4 \
| awk 'NR>1{d=$1-p; printf "%.6f\n",d} {p=$1}' | sort -n | uniq -c

# 4) PTS/DTS 一致性（B 帧/复用异常排查）
ffprobe -v error -select_streams v:0 \
 -show_entries frame=pkt_dts_time,best_effort_timestamp_time -of csv=p=0 input.mp4
```

**判读**：CFR 下相邻 `best_effort_timestamp_time` 间隔须**恒等于 1/fps**（24fps ≈ **0.0416667s**）；出现 0.5×/2× 或成对抖动 = 丢帧/重复；`r_frame_rate ≠ avg_frame_rate` 且非整倍 = VFR/漂移。旧容器无 `best_effort_timestamp_time` 时改用 `pts_time`。

**`fps_mode` / `vsync` 含义**：`passthrough`（原样）· `cfr`（重采样到固定帧率，会插/丢帧）· `vfr`（按时间戳输出，保时间轴）· `auto` · `drop`。
→ ⭐ **检测阶段绝对不加 `-fps_mode` / `-vsync`**，让 ffprobe 读原始时间戳。

### 分工表

| 场景 | 是否用 `mpdecimate` |
|---|---|
| 归档/录屏、真实静止或隔行冗余（**真重复帧压缩**） | ✅ 可用 |
| 慢速运镜 / 渐变 / 低对比白模 / 运动模糊 | ❌ **绝不可当质量门**（必误删） |
| **帧率漂移、judder、音画同步质量门** | ❌ 改用「**时间戳间隔分布 + 帧数校验**」 |

---

## ③ `ebur128` / `loudnorm` 字段对照表

### `loudnorm` `print_format=json` 字段

| 字段 | 含义 | 单位 | 两遍法 |
|---|---|---|---|
| `input_i` | 输入整体响度 | LUFS | ⭐ **第一遍读** → 第二遍 `measured_I` |
| `input_tp` | 输入真峰值 | dBTP | ⭐ 第一遍读 → `measured_TP` |
| `input_lra` | 输入响度范围 | LU | ⭐ 第一遍读 → `measured_LRA` |
| `input_thresh` | 输入门限 | LUFS | ⭐ 第一遍读 → `measured_thresh` |
| `target_offset` | 达标所需增益偏移 | LU | ⭐ 第一遍读 → 第二遍 `offset` |
| `output_i` / `output_tp` / `output_lra` / `output_thresh` | 预计输出值 | — | ❌ **仅参考，忽略** |
| `normalization_type` | 实际用了动态还是线性 | 枚举 `dynamic`\|`linear` | ⭐ **必须回读校验** |

→ **第一遍只需读 5 个**：`input_i` / `input_tp` / `input_lra` / `input_thresh` / `target_offset`。
→ 第二遍填 `measured_I/TP/LRA/thresh + offset + linear=true`；**`output_*` 只作参考**。

### `ebur128` 原生 filter 字段（**名字与 loudnorm 不同**，`ebur128=peak=true`）

| 输出行 | 含义 | 单位 |
|---|---|---|
| `Integrated loudness: I` | 整体响度 | LUFS |
| `Threshold` | 门限 | LUFS |
| `Loudness range: LRA` | 响度范围 | LU |
| `LRA low` / `LRA high` | 范围下/上界 | LUFS |
| `True peak: Peak` | 真峰值 | dBTP |

```bash
# 只测量
ffmpeg -i in.wav -af ebur128=peak=true -f null -
# loudnorm 两遍 · 第一遍（tail -12 取 JSON）
ffmpeg -i in.mp4 -af loudnorm=I=-16:TP=-1.5:LRA=11:print_format=json -f null - 2>&1 | tail -12
# loudnorm 两遍 · 第二遍
ffmpeg -i in.mp4 -af "loudnorm=I=-16:TP=-1.5:LRA=11:measured_I=..:measured_TP=..:measured_LRA=..:measured_thresh=..:offset=..:linear=true" -c:v copy -ar 48000 out.mp4
```

### 坑
- `loudnorm` **内部升采样到 192kHz** → **必须显式 `-ar 48000`**
- 第二遍漏 `linear=true` → 退化为动态压缩
- 缺任一 `measured_*` → 回落 dynamic
- ⭐ **即使 `linear=true`，当增益会顶破 TP 或 `measured_LRA > 目标 LRA` 时仍会静默回退 dynamic** → **脚本必须回读 `normalization_type` 校验，不能盲信参数**

---

## 未验证清单

| # | 项 | 原因 |
|---|---|---|
| 1 | OpenAIR 的 CC 具体版本（3.0 vs 4.0）与**逐文件 LICENSE** | 主站 + 镜像均挂起（Account Suspended），无法核对 |
| 2 | Aachen IR DB 具体许可 | OpenSLR 标 "Not stated"，原 RWTH 页未打开 |
| 3 | Zenodo 各 IR 数据集逐条许可 | 未逐一打开许可字段 |
| 4 | EchoThief 是否存在另一份明示许可 | 站点与 SDSU 页均无 |
| 5 | **城市街道/巷弄专用免费 IR** | **未找到明确 CC0 的城市街景 IR 库** |

## 反方证据汇总

| 主题 | 反方证据 |
|---|---|
| IR 素材 | ① **EchoThief 被二手源普遍误列为"免费"**，官方站点其实无授权 ② OpenAIR 的 CC 版本来源不一致，且其库允许第三方上传、**部分藏品可能附带各自条款→须逐文件核对 LICENSE** ③ Aachen 两条来源许可互斥（MIT vs Not stated） |
| judder 检测 | ① `mpdecimate` 的 `hi/lo/frac/max/keep` 语义与默认值**跨 ffmpeg 版本表述不一**（`keep=0` 含义易混）② `-vsync` 自 ffmpeg 5.0 起被 `-fps_mode` 取代，旧脚本硬编码 `-vsync` 在新版可能告警或行为改变 |
| 响度 | ① loudnorm 单遍在部分文档中被称为"可直出"，与社区"必须两遍"共识相左 ② **`linear=true` 存在静默回退 dynamic 的已知行为** |

---

## 落到本项目的 4 条动作

1. **IR 主库 = BUT Reverb Database（CC BY 4.0）**，**必须在片尾/随片署名 + 附许可链接 + 标注改动** → **这一条要写进 `clearance` 台账**（新增一类"IR 署名"）；需零署名时改用 **Freesound 筛 CC0**。
2. **EchoThief 拉黑**（无授权条款）；**C4DM 拉黑**（BY-NC-SA）。
3. **IR 只管空间，雨声单独叠层**——不要把雨录进 IR。城市街道专用 IR 稀缺，用自然环境 IR + 独立雨层替代。
4. **judder 检测改用时间戳间隔分布 + 帧数校验**（4 条命令已就绪），**`-fps_mode`/`-vsync` 在检测阶段一律不加**；`mpdecimate` 仅保留"真重复帧压缩"用途。
5. **响度脚本必须回读 `normalization_type`** 校验是否真的走了 linear（即使传了 `linear=true` 也可能被静默回退）。
