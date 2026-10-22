# R0-T6 · GPU 引擎入口清单（vram_lock 全引擎接入）

> 落地：R0 轮 T6（R4-T19 缺口修复 / R10-OK8 全引擎裁定），2026-10-03，工程师寇豆码。
> 断言 A1（R0 计划）：对本清单"运行时 GPU 入口"逐文件 `grep -L "vram_lock"` 返回**空集**。
> 锁实现：`tools/vram_lock.py`（文件锁 O_CREAT|O_EXCL 原子创建 + TTL 1800s + 心跳 60s + 原子接管，上下文管理器异常自动释放）。

## 一、运行时 GPU 入口（必须接锁，A1 检查对象）

| # | 入口文件 | 引擎/用途 | 锁 owner | 接入方式 |
|---|---|---|---|---|
| 1 | `tools/wan22_client.py` | Wan2.2 TI2V 5B 视频生成（ComfyUI API） | `wan22` | 原有（generate 全程持锁，本次未改） |
| 2 | `tools/comfyui_client.py` | SDXL 图像 / AnimateDiff 视频（提交总闸） | `comfyui-sdxl` | generate() 内 submit→poll 全程持锁 |
| 3 | `tools/comfyui_generator.py` | 通用 ComfyUI 图像生成（资产岗） | `comfyui-gen` | generate() 内 queue→wait 全程持锁 |
| 4 | `tools/acestep_client.py` | ACE-Step 1.5 BGM（经 ComfyUI 推理） | `acestep` | generate_music() 内 submit→poll 持锁 |
| 5 | `tools/vlm_check.py` | Qwen3-VL-4B 本地 CUDA 质检（约10GB） | `qwen3-vl` | main() 内模型加载+推理持锁 |
| 6 | `tools/blockout_min_v1.py` | Blender 白模渲染（blender -b -P 执行） | `blender-blockout` | 渲染调用点持锁，sys.path 注入 tools/ |
| 7 | `tools/_probes/blender_blockout_min.py` | Blender 白模渲染（probe 版） | `blender-blockout` | 同上 |
| 8 | `tools/wan22_shots_33_41.py` | Wan2.2 关键镜批量重生成 | （经 #1） | generate_video 内部持锁；文件内注明 |
| 9 | `tools/comfyui_start.py` | 归档区 ComfyUI 启动包装 | —（不持锁） | 启动前打印锁状态，提示 D23 错峰；非 GPU 计算入口 |

A1 自验命令（PowerShell/bash 逐文件）：
```
grep -L "vram_lock" tools/wan22_client.py tools/comfyui_client.py tools/comfyui_generator.py \
  tools/acestep_client.py tools/vlm_check.py tools/blockout_min_v1.py \
  tools/_probes/blender_blockout_min.py tools/wan22_shots_33_41.py tools/comfyui_start.py
# 期望：无输出（空集）
```

## 二、排除名单（不接锁，注明理由）

| 文件/引擎 | 理由 |
|---|---|
| 云引擎调用（fal / 即梦 / kling 等） | 云端推理不占本地 VRAM（R7-B9 四条件门内使用），不接锁 |
| `tools/tts_generator.py` | edge-tts 微软云端合成，无本地 GPU |
| `tools/whisper_transcribe.py` | faster-whisper（CTranslate2）**本地 CPU** 推理（docstring 明示），不占显存 |
| `tools/gen_bgm.py` / `gen_sfx.py` / `gen_ambient.py` / `build_mix.py` | 程序合成 + ffmpeg，CPU |
| `tools/d1_model_queue.py` | 模型下载队列（网络 IO），非 GPU 运行时（注意：其内仍硬编码旧根路径，属 v1 遗留工具，挂待修不阻塞本项） |
| `tools/p0_setup.py` | 一次性 P0 环境安装脚本（下载/解压），非运行时 GPU 入口 |
| `_legacy_projects/` 内全部脚本 | 冻结区只读，仅 ComfyUI/blender 可执行体被只读调用（启动经 `tools/comfyui_start.py` 包装） |

## 三、A2/A3 实测方案（12GB 卡并发串行化证明）

1. `python tools/comfyui_start.py --lowvram --wait` 起归档区 ComfyUI（只读运行）；
2. 提交一个 ComfyUI GPU workflow（经 comfyui_client，持锁 owner=comfyui-sdxl），
   同时另起 Blender EEVEE 渲染 121 帧 @832×480（经 blockout_min_v1，持锁 owner=blender-blockout）；
3. `nvidia-smi --query-gpu=memory.used --format=csv` 每 2s 采样，全程峰值 ≤12288 MiB，无 CUDA OOM（A2）；
4. 串行化证明（A3）：从 `logs/vram.lock` 内容读取两 owner 的 acquired_at/released_at，
   计算持锁时间窗交集 ≤ 1 个锁抖动周期（心跳 60s / poll 5s 量级）。

实测执行记录见本文件末尾附录（若环境卡点则如实登记）。

## 四、实测附录（2026-10-03 执行记录）

- **状态：已完成**（ComfyUI 0.37.2 归档区实起 + Blender 5.2.2 归档区实渲）
- 标定：Blender EEVEE 121 帧 @832×480（owner=blender-blockout）与 ComfyUI SD1.5
  文生图（owner=comfyui-gen）**同时提交**，经 vram_lock 争用串行化。
- **A2 峰值**：`nvidia-smi` 2s 采样全程 **峰值 11194 MiB ≤ 12288**（含系统基线约 2.0GB），
  全程无 CUDA OOM，两任务均成功产出（生成图 `runtime/vram_test/assets/scenes/vram_test_asset_v1.png`；
  渲染帧 121 张，落 `runtime/vram_test/blender_out3/frames/`）。
  **帧产出证据链（QA 补证令 P1，2026-10-03 登记原始事实）**：Blender 5.2.2 将相对 `--out`
  按**其自身启动 cwd（C:\）**解析（非调用方 shell 的 cwd），故三轮渲染帧原始落盘位置为
  `C:\runtime\vram_test\blender_out{,2,3}\frames\`（QA 在项目内 runtime 下查找故为空——
  目录不存在而非帧未产出）。日志级证据：第一轮 Blender stdout 明示
  `Saved: 'C:\runtime\vram_test\blender_out\frames\f_0121.png'` 与 `BLOCKOUT_FRAMES=121`。
  文件系统证据（实测）：三轮各 121 帧（f_0001.png~f_0121.png，约 323KB/帧），
  mtime 18:43/18:45/18:47，与三轮锁窗口逐一吻合。A3 竞争轮（round3）的 121 帧已于
  2026-10-03 原样 `mv` 迁移至本清单所述项目路径 `runtime/vram_test/blender_out3/frames/`
  （迁移非补跑，文件 mtime 18:47 保留，与锁窗口 18:47:51~18:48:08 一致）；
  round1/2 帧仍留在原始位置未动。
- **A3 串行化证明**（`runtime/vram_test/lock_history.log` 1s 采样 → `analyze_lock.py`）：
  ```
  owner=comfyui-gen        acquire=18:47:25 release=18:47:48
  owner=blender-blockout   acquire=18:47:51 release=18:48:08
  时间窗交集 = 0.0s（阈值 ≤ 5s 锁抖动周期）→ 串行化成立
  ```
  佐证：Blender 本轮总时长 44s（独占基线 19s），多出的 25s 即等锁时间——
  锁确实将后到提交端挡在窗口之外。
- 环境备注：ComfyUI 模型常驻显存（生成结束后仍占约 8.7GB 直至进程退出），
  属 ComfyUI 内存策略；锁纪律保证"提交端错峰"，服务侧建议 `--lowvram` 启动
  （`tools/comfyui_start.py --lowvram`）。测试后服务已停止（显存回落 1521MiB）。
