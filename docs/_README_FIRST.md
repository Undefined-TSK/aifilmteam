# _README_FIRST · 全项目文档库唯一入口

> 建立日期：2026-10-03（普查+重组执行日）｜ 维护人：team-lead
> 本文件是全项目文档系统的**唯一入口**：任何新会话/新成员/老板查阅，从这里开始。

---

## 1. 一图看懂项目结构（代际 + 分区）

```
D:\aifilmteam\
├── AI影视团队v2\          【当前代·活动根·原地不动】spec/agents/projects/docs/logs/_legacy_*
├── docs\                  【活动文档库】决策系统 + 主设计 + 索引身份 + 逆向审计（本库）
├── _legacy_projects\      【历史归档·只移不删】
│   ├── v1-prototype\        ← 原 AI影视团队\（v1 原型，2026-10-03 整体迁入）
│   └── v2-intermediate\     ← 原 ai_film_projects\（中间代，2026-10-03 整体迁入）
├── config\                【配置区】scalability_config.json + REGISTRY.md（三份同名 config 的代际登记）
├── outputs\               【输出区】成片与交付包
├── runtime\               【运行时区·全部 gitignore】日志/缓存/生成物
└── .workbuddy\ 等          工具运行时（忽略，不删）
```

**代际链**：v1-prototype（CrewAI+FastAPI 文本 MVP）→ v2-intermediate（Hermes 15 岗体系+雨夜寻猫）→ **AI影视团队v2（当前权威线）**。
**决策线**：`三.md`（124KB 主设计，下一代 C3/v3 立项材料）+ `docs/02-决策/` 15 轮协商 + DECISIONS.md ——属 **C3/v3**，不与 v2 spec 直接对账（v2 真实管线决策收口在 `AI影视团队v2/docs/调研-板块②d-待闭合项决议.md`，4/4 闭合）。

## 2. docs/ 目录地图（00~09 大类）

| 目录 | 性质 | 内容 |
|---|---|---|
| `00-索引-状态-身份\` | 活动登记 | project_memory.md、user_profile.md、VERSION.md、STATUS_MATRIX.md |
| `01-主设计\` | 活动纲领 | 三.md（C3 主设计）、一.md、二.md |
| `02-决策\` | **唯一决策事实源** | DECISIONS.md + NEGOTIATION_PROGRESS.md + 15 轮稿 + 支撑件（00-emergency / 00-impact / 03a-research / 03-one-size-fits-all-audit（改名自04-）/ 05b-reflection（改名自05-）/ 支撑-五点升级报告（改名自P1-））+ 普查复审六件套（06~11） |
| `03-规划与调研\` | 索引 + 新规划 | R0-执行计划.md（新）；v2 的 24 篇规划调研**保留在 v2/docs/ 原位**（运行时引用，不外迁），经本行索引 |
| `04-契约spec\` | 索引 | v2 `spec/`（delivery_spec / qc_rubric / shot_spec.schema）与 `pipeline/` 契约**保留 v2 原位**；注意 pipeline 的 delivery_spec.json 待改 tech_ 前缀（R0 任务） |
| `05-岗位卡\` | 索引 | v2 `agents/` 7 个当前 SKILL 原位；15 个退役岗在 `v2/agents/_legacy_roles/` 与 `_legacy_projects/v2-intermediate/roles/` |
| `06-项目资料\` | 索引 | 雨夜寻猫权威副本在 `AI影视团队v2\projects\雨夜寻猫\`；中间代旧份在 `_legacy_projects/v2-intermediate/projects/` |
| `07-交接与日志\` | 索引 | 当前交接落 v2 `logs/`；历史交接在 v2 `docs/_legacy_handoff/` 与中间代归档 |
| `08-学习方法论\` | 索引 | course 全套在 `_legacy_projects/v2-intermediate/course/`（单一物理副本，红线：禁跨代重复） |
| `09-逆向与审计\` | 活动 | 三版本逆向分析报告.html + `普查工作区-2026-10/`（4 份 findings） |

## 3. 阅读顺序（按角色）

- **老板**：本文件 → `01-主设计/三.md` → `02-决策/NEGOTIATION_PROGRESS.md`（15 轮全 ✅ 收官）→ `02-决策/11-development-readiness-report.md`（开工准备度）
- **开发**：本文件 → `AI影视团队v2\PROJECT_STATE.md` → v2 `spec/` 三契约 → `03-规划与调研/R0-执行计划.md`（开工第一周任务）
- **新人**：本文件 → `01-主设计/三.md` → `02-决策/DECISIONS.md` → course 方法论（§2 索引）
- **审计**：`02-决策/06-full-project-audit.md` → `09-逆向与审计/普查工作区-2026-10/` 4 份 findings → 07/08/09/10 复审裁定链

## 4. 红线（摘要，全文见 02-决策/07 §E.6）

1. **零删除**：核心三文件夹（现 v1-prototype / v2-intermediate / AI影视团队v2）只移不删，含一切 `_legacy_*`。
2. **禁止同名不同义**：`delivery_spec.json` 双份待 tech_ 前缀消歧；config.yaml 三份按代际目录消歧（见 config/REGISTRY.md）。
3. **禁止跨代重复**：单一权威副本 + 索引引用，不再另存。
4. **引用必须相对路径**：禁止 `C:\Users\...` 硬编码。
5. **引用决策编号必带轮次**（如 R8-C-1），禁裸编号。
6. **实测断言必须附命令回显**，无回显的"不存在/已查"结论无效。
7. **单一事实源**：决策=02-决策/DECISIONS.md；v2 状态=PROJECT_STATE.md；文档版本=00-索引/VERSION.md。

## 5. 2026-10-03 重组执行记录（摘要）

v1+中间代整体迁入 `_legacy_projects/`（mv 原位重命名，零删除）；negotiation 29 份迁入 `docs/02-决策/`；根级 5 文档归位；审计件三连改名落地；findings 迁入 09/普查工作区。方案依据：`02-决策/07-document-reorganization-plan.md` + `08-project-restructure-plan.md`，裁定记录见 `02-决策/10-team-collaboration-log.md`（R-1~R-5）。
