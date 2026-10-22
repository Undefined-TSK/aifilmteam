# AGENTS.md — AI 影视团队 v2 协作纪律（本文件为运行纪律单一事实源，R0 轮起）

> 登记：R0-T6（vram_lock 全引擎接入 + D23 分时纪律），2026-10-03，工程师落地。

## D23 · 分时纪律（GPU 错峰）

- **12GB 单卡（RTX 5070 Laptop）是全团队唯一共享资源**：任何本地 GPU 引擎
  （Wan2.2 / ComfyUI / Blender 渲染 / Qwen3-VL / ACE-Step 等）**submit 前必须
  经 `tools/vram_lock.py` 获取显存独占锁**，锁等待上限 1800s，禁止裸跑抢显存
  （R4-T19 缺口修复，R10-OK8 裁定全引擎接入）。
- **分时约定**：大模型生成（Wan2.2 5B，≥8GB）与渲染/质检类任务分时段排期，
  同一时段只允许一个 GPU 重任务持锁运行；轻任务（图生图、EEVEE 白模渲染）
  可在等待窗口排队，由 vram_lock wait 自动错峰。
- **云引擎豁免**：fal / 即梦等云端调用不占本地 VRAM，不接锁（见
  `docs/07-交接与日志/R0-T6-GPU引擎入口清单.md` 排除名单）。
- **锁语义**：TTL 1800s + 心跳 60s + 原子接管；锁文件 `logs/vram.lock`
  长期存在属正常现象（沙箱禁删，释放走 released 标记，见 vram_lock.py docstring）。
- **归档区 ComfyUI**：位于 `_legacy_projects/v2-intermediate/comfyui/`，
  只读运行不禁；启动一律走包装脚本 `python tools/comfyui_start.py`（最小侵入，
  不改归档区文件），12GB 卡跑 5B 模型建议 `--lowvram`。

## GPU 引擎接入索引

| 引擎 | 入口 | 锁 owner |
|---|---|---|
| Wan2.2 TI2V 5B | tools/wan22_client.py | wan22 |
| ComfyUI SDXL/AnimateDiff | tools/comfyui_client.py | comfyui-sdxl |
| ComfyUI 通用生成 | tools/comfyui_generator.py | comfyui-gen |
| ACE-Step BGM | tools/acestep_client.py（锁在 submit_workflow 层） | acestep |
| Qwen3-VL-4B 质检 | tools/vlm_check.py | qwen3-vl |
| Blender 渲染 | tools/blockout_min_v1.py、tools/_probes/blender_blockout_min.py | blender-blockout |
| ComfyUI 服务启动 | tools/comfyui_start.py（包装，不持锁，打印锁状态提示） | — |

完整清单与排除名单：`docs/07-交接与日志/R0-T6-GPU引擎入口清单.md`。
