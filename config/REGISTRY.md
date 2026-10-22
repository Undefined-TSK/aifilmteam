# config · 配置区登记表（REGISTRY）

> 目的：消除三份同名 `config.yaml` 的同名不同义碰撞（07 方案 C.6 / 08 方案 C 专项映射的落地）。
> 处置口径（按 R-1/R-3 裁定修正）：三份 config **随各自文件夹整体归位/保留原位，不拆分、不复制、不删**，以下表登记消歧。

| 配置文件（现路径） | 代际 | 用途 | 状态 |
|---|---|---|---|
| `D:\aifilmteam\config\scalability_config.json` | 跨代 | 根级扩展性配置参数（2589B） | 活动 |
| `_legacy_projects\v1-prototype\config.yaml` | v1 | CrewAI+FastAPI 应用配置（728B，Kimi API） | 已停用（随 v1 归档） |
| `_legacy_projects\v2-intermediate\config.yaml` | 中间代 | Hermes Agent Profile（814B，飞书+9岗+SDXL 时代） | 已退役（随中间代归档） |
| `AI影视团队v2\docs\_legacy_source\根配置\config.yaml` | 中间代镜像 | 逐字冻结副本（md5 SAME） | 有意归档，不复制不删 |

## 规则
1. **新增配置**放本目录，并在此表登记一行（文件/用途/owner/日期）。
2. **禁止再出现同名不同义配置**：同用途变体必须改名（如 `v2.runtime.yaml` / `tech_delivery_spec.json` 式前缀消歧）。
3. 归档代际的配置**只读**，如需恢复使用，先走正式迁移流程并在本表更新状态。
