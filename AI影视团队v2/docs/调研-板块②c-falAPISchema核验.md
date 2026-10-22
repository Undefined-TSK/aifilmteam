# 调研-板块②c fal 3DREAL API Schema 核验（一手）

**来源**：fal.ai 官方 `llms.txt`（`https://fal.ai/models/fal-ai/ltx-2.3-quality/render-to-real/llms.txt`），抓取其 Input Schema 原文。
**访问日期**：2026-09-27 ｜ **证据等级**：一手（官方 API schema / OpenAPI）｜ **核验人**：team-lead 亲自（子代理 LLM 通道 429 期间直取，避免等待重置）

---

## 一、待核 4 项（comp-commercial 遗留项）

### ① `resolution`（输出分辨率 / cap / 宽高比）
> "Output resolution (short side), preserving the source aspect ratio. The IC-LoRA control path caps the resolution x frames volume, so resolution trades against duration: 720p allows up to ~6s (sharper), 480p up to ~15s (softer but longer). A request above the budget is rejected with a clear error — pick 480p for longer clips. Output duration is num_frames / frames_per_second. Default value: '720p'. Options: '480p', '720p'."

- ✅ 短边定、保源宽高比 → 确认 `A-01`
- ✅ cap = resolution × frames 体积 → 确认 `B-13` / `D-07`
- ✅ 720p ~6s / 480p ~15s → 确认 `D-05` / `D-06`
- ✅ 超限拒绝 → 确认 `B-13`（博客写 422、schema 写 "clear error"，二者一致）
- ⚠️ 口径：官方仅给 480p / 720p 两档，无 1080p；清单 D 段未假设更高档，一致

### ② `num_frames`（帧数 / 8k+1 / 422）
> "Default value: 121. Range: 9 to 481." 且 "The IC-LoRA control budget caps the resolution x frames volume: roughly 6s at 720p or 15s at 480p; a request above it returns a 422 (lower num_frames, or use 480p)."

- ✅ 最小 9 → 确认 `D-03` ｜ ✅ 最大 481 → 确认 `D-07` ｜ ✅ 默认 121 → 确认 `D-05`
- ✅ 422 → 确认 `B-13` ｜ ✅ ~6s@720p / ~15s@480p → 确认 `D-05` / `D-06`
- ✅ 8k+1：schema 未重述，来源为官方博客（temporal autoencoder 8× + 1 anchor），仍计一手；range 9–481 与 8k+1 兼容（9=8×1+1，481=8×60+1）→ `D-01` 双引 blog+schema 正确

### ③ `frames_per_second`（fps）
> "Frames per second of the generated video. Default value: 24. Range: 1 to 60."

- ✅ 默认 24 → 确认 `A-02` / `B-04`
- ✅ `B-05` 结论成立：duration = num_frames / fps，fps 改回放速率、不改成本（成本 ∝ 宽×高×帧，与 fps 无关）

### ④ `image_url`（可选 / frame-0 锚）
> "Optional reference image used as the FIRST frame (image-to-video anchor), matching how the adapter was trained. It defines the photoreal look of frame 0; leave empty to let the render alone drive the result."

- ✅ 基线 = 不传 `image_url` → 确认 `B-01`（原文逐字支持）
- ✅ 多数投票（`B-02`）来自官方博客，schema 未重述，仍一手

---

## 二、衍生确认（顺带核验，强化板块① / 清单）

| 字段 | 官方原文要点 | 对清单影响 |
|---|---|---|
| `intensity` | 默认 `light`；选项 light/strong/strong-v2；strong-v2 = "better multi-scene coherence, audio, talking characters, higher quality" | ✅ `B-06`（联调 light / 终稿 strong-v2） |
| `enable_detail_refine` | 默认 false；"doubles the output width AND height (4x the pixels), so the request costs roughly 4X THE PRICE and is slower" | ✅ `B-12` / `E-03`（×4 逐字） |
| `detail_refine_strength` | 默认 0.75；"Higher regenerates more detail (and can drift further from the base)" | ✅ `B-12` 漂移警告逐字 |
| `prompt` | 默认 `"3DREAL. "`；"The 3DREAL trigger is always kept, even if you clear it or enable prompt expansion" | ✅ `B-07` / `B-09` |
| `enable_prompt_expansion` | 默认 false | ✅ `B-09` |
| `enable_safety_checker` | 默认 true | ✅ `B-10` |
| `video_quality` | 默认 `high`，选项 low/medium/high/maximum；schema **未提计价影响** | ⚠️ `B-11` "❓是否影响计价"维持未验证（不假设免费） |

---

## 三、结论

comp-commercial 待核 4 项**全部一手确认通过**；反向修正 **0 处**（清单与官方 schema 完全自洽）。

⚠️ **唯一新增须 R3 决**：`generate_audio` 默认 `true`（"When disabled, the final MP4 is returned without an audio track"）。引擎可自带音轨；我们音频走独立链（板块① qc-audio），须决定 `generate_audio` 开/关及音轨归属 → 记板块②商务点，R3 定。

> 另：`num_inference_steps` 默认 15（8–30）、`guidance_scale` 默认 1（1–20）为 R3 调参候选，未入清单 scope。
