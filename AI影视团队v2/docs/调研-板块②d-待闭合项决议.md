# 调研-板块②d · 4 项待闭合决议（R2 收尾）

**作者**：主理人（齐活林）｜ **日期**：2026-09-27｜ **状态**：4/4 全部闭合
**背景**：板块② 验收页"六、待老板拍/待闭合"列 4 项。老板指令"你来解决这几个问题" → 由主理人取证并拍板，逐项落档。累计花费仍 ¥0。

---

## 决议 1 —— fal 3DREAL LoRA 商用条款

**原阻塞**（🔴）：HF `fal/LTX-2.3-3DREAL-LoRA` 仓库 `license: other` 无正文，"闭合前不得对外承诺商用"。

**取证结果（一手）**：
- fal 官方 FAQ 原文（fal.ai/docs，模型 API FAQ）：
  > "Can I use generated files for commercial purposes? **Each model has its own license. Most models on fal are available for commercial use and are marked with a Commercial use badge on the model page.** Models marked Research only are restricted to non-commercial use. Check the model's page for its specific license."
- fal `render-to-real` 模型页（fal-ai/ltx-2.3-quality/render-to-real）页头元信息含 **"Commercial use"** 标章（位于 Inference 之后、Schema 之前）。
- fal ToS（2026-09-08 更新）第 7(a) 条：Output Content 列为客户保密信息；第 4(c) 条：Company 明确不主张 Output Content 任何 IP 权利；第 4(a) 条：授予客户"personal or internal business use"使用权；第 4(b)(i)(C)：允许通过 Customer Solution 向终端用户提供。

**判定**：🔴 → 🟢（对**托管 API 路径**已闭合）。

**理由**：
1. 我们消费 3DREAL 的方式是**调用 fal 托管端点**，不是下载/自托管 LoRA 权重。商用权利来自 fal 模型页 "Commercial use" 标章 + fal ToS，而非 HF 仓库的 `other` 许可。
2. HF 仓库 `license: other` **仅约束自托管/再分发适配器权重**，不在我们路径内。
3. 客户义务（fal ToS 第 6(d)/15）：保证输入内容权利合法、就输出侵权索赔赔偿 fal——这是标准 SaaS 责任，不阻塞商用。

**边界（仍须遵守）**：
- ⚠️ 若未来要**自托管 3DREAL 权重**（如离线私有化部署），须先取得 fal / Lovis Odin(@OdinLovis) 对 `other` 许可的明确书面授权；当前不在此路径，不触碰。
- ⚠️ 对外交付时按 fal ToS 履行输入内容权利担保（我们的 blockout/参考图均为自产或 CC0，无第三方权利瑕疵）。

**结论**：可对外承诺商用（走 fal 托管端点）。

---

## 决议 2 —— LTX-2.3 权重许可原文

**原阻塞**（🟡）：二手源冲突（Apache-2.0 vs LTX-2 Community License + $10M）。

**取证结果（一手/权威二手交叉）**：
- **权威纠正源**（Hivebook，2026-09-01 重审）：
  > "Licence — corrected 2026-09-01. **No LTX checkpoint is Apache-2.0.** ... Read off each checkpoint's own card and LICENSE file, the chain is: ... LTX-2 and LTX-2.3 under the **LTX-2 Community License Agreement (dated 2026-01-05)**."
-  corroborated by CanIRun.ai 与 ltx23.app（均写 LTX-2 Community License，$10M ARR 阈值、衍生沿用、署名保留）。
- 冲突源（ltx23.video 等博客写 Apache-2.0）**已证伪**——属作者笔误，Hivebook 明确标注"was wrong at authoring"。
- 附加事实：LTX-2.5（2026-07/08）已成当前推荐版，LTX-2.3 被官方标 "Legacy"；但我们云路径经 fal 调用，不依赖自托管版本。
- 依赖链提示：LTX-2.3 文本编码器用 **Gemma 3 12B**（Google 条款），自托管时须叠加 Google ToS——但托管路径由 fal 承担。

**判定**：🟡 → 🟢（对**托管 API 路径**已闭合；自托管路径有约束但非当前阻塞）。

**LTX-2 Community License 要点（决策用）**：
1. 年营收 ≥ $10,000,000 的实体 = "Commercial Entity"，须向 Lightricks 购买商业许可。
2. 衍生权重须沿用同协议 + 向下游告知。
3. 再分发权重须保留署名。
4. < $10M 实体：可商用、免费、保留署名即可。

**本项目适用**：个体/小团队（营收远低于 $10M）→ 商用无碍；我们以 fal 托管消费，不直接持 LTX-2.3 权重，故 Community License 不直接约束我们。仅当未来**自托管 LTX-2.3** 时需遵守（≥$10M 须采购、署名、衍生沿用）。

**结论**：当前路径已闭合；自托管约束写入 clearance 台账备查。

---

## 决议 3 —— 本机 12GB 本地路径锁定 Wan2.1-VACE-1.3B

**原状态**（🟢 已建议，待认）：本机 12GB 下本地路径锁定 Wan2.1-VACE-1.3B，不碰 LTX 本地。

**判定**：🟢 → ✅ **正式锁定**（写入 R3 架构基线）。

**理由（数据驱动）**：
- **Wan2.1-VACE-1.3B**：Apache-2.0；实测 VRAM ≈ 8.19GB（权重 F16=4.31GB + 推理开销），**低于本机 12GB**，可本地零成本跑通"白模锁结构"前提。权重残片 196MB→需补至 4.31GB（R4 施行）。
- **LTX-2.3 本地**：官方/社区一致口径本地生成需 **16GB+ VRAM**（FP8 量化可降但本机仍紧）；LTX-2.5 全 FP16 需 44GB。本机 12GB **不可行** → 排除本地路径。
- **战略顺序**：先 ¥0 本地 VACE 验证管线（R4 技术验证镜）→ 成立后再投 fal 云写实化。不与"先付费验证未验前提"冲突。

**结论**：本地零成本路径 = Wan2.1-VACE-1.3B（唯一候选）；云写实化 = fal 3DREAL（决议 1 已许可）。

---

## 决议 4 —— `generate_audio` 默认开：音频链归属

**原状态**（🟢 R3 定）：音频链归属（引擎音轨 vs 独立链）。

**判定**：🟢 → ✅ **音频 = 独立链，引擎 `generate_audio` 默认关**。

**理由（架构原则 + QC 契约）**：
1. **原则对齐**：项目铁律"大模型只执行不决定"。音频的创意/叙事决策（台词、空间感、响度）归我们，不交引擎随机生成。
2. **QC 契约硬指标**（qc_rubric）：48kHz/24bit/-14LUFS、LRA≥8LU、Sync-C≥5。引擎 `generate_audio`（LTX-2.3 基础音频 / 3DREAL Strong v2 的"talking scenes synced audio"）为环境/氛围级，**不达对话级 LUFS/LRA 精度**，不能当交付音轨。
3. **链路既定**：CosyVoice 3（Apache-2.0，替代 edge-tts）做台词 TTS → afir 卷积真 IR（EchoThief/BUT Reverb DB，CC BY 署名）做空间混响 → ebur128 两遍法压 -14LUFS → alimiter:level=disabled。该链由 blockout 的 shot_spec 脚本驱动，可控可复现。
4. **例外利用**：`generate_audio` 可**仅用于 previs/粗剪参考轨**（ pacing 参考），最终交付音轨一律由独立链产出后 mux。

**结论**：交付音轨 = 独立链（CosyVoice3+afir+ebur128）；`generate_audio` 默认 OFF，仅 previs 可选 ON。

---

## 汇总：4 项阻塞全部闭合

| # | 事项 | 原级 | 现级 | 决议 |
|---|---|---|---|---|
| 1 | fal 3DREAL LoRA 商用 | 🔴 | 🟢 | 托管端点带 Commercial use 标章，可对外商用；自托管权重仍须 fal 授权（不在路径） |
| 2 | LTX-2.3 权重许可 | 🟡 | 🟢 | 非 Apache-2.0，实为 LTX-2 Community License；托管路径不持权重，已闭合；自托管约束入台账 |
| 3 | 本地路径锁定 | 🟢 | ✅ | 锁定 Wan2.1-VACE-1.3B（12GB 可行）；LTX 本地排除 |
| 4 | 音频链归属 | 🟢 | ✅ | 独立链（CosyVoice3+afir+ebur128）；引擎 `generate_audio` 默认 OFF |

**唯一剩余硬阻塞已清零** → 板块② 无对外承诺法务障碍，可交付老板签字。

---

## 待 R3 落地的派生动作（不阻塞验收）

1. clearance 台账新增：fal ToS 输入权利担保义务、LTX-2 Community License 自托管约束、$10M 阈值预警。
2. R3 架构文档标注：本地=Wan VACE / 云=fal 3DREAL / 音频=独立链 三态定稿。
3. 自托管 3DREAL/LTX 路径标记为"future-gated"，非当前范围。
