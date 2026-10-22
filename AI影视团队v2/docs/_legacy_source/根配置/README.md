# CINEAST — AI影视团队工作平台

## 项目结构

```
D:\ai_film_projects\
│
├── docs/                        # 项目文档
│   ├── AI影视团队工作平台方案.md       # 总体方案
│   ├── AI影视团队工作平台方案-优化意见.md
│   ├── 使用说明书.md                  # Agent使用指南
│   └── project_memory.md             # 项目记忆（规则、进度、踩坑）
│
├── tools/                      # 核心工具脚本
│   ├── director_intent.py          # 导演意图文档管理
│   ├── asset_manager.py            # 资产管理
│   ├── budget_manager.py           # 预算管理（预警+熔断）
│   ├── k13_version_tree.py         # K13版本树（版本锁定）
│   └── handoff_manager.py          # Agent接力调度
│
├── roles/                      # Agent Profiles
│   ├── producer/                   # 制片人（已完善）
│   ├── character_designer/          # 角色设计师（已完善）
│   ├── scene_designer/             # 场景设计师
│   ├── storyboard_artist/          # 分镜师
│   ├── art_director/              # 艺术总监
│   ├── screenwriter/              # 编剧
│   ├── animator/                  # 动画师
│   ├── sound_engineer/            # 音效工程师
│   └── editor/                    # 剪辑师
│
├── web/                        # 前端
│   ├── showcase/                   # 产品官网（展示页）
│   │   ├── index.html
│   │   └── assets/
│   └── workspace/                  # 工作台（节点图应用）
│       └── workspace.html
│
├── projects/                   # 项目数据
│   ├── .template/                  # 项目模板
│   └── 雨夜寻猫/                   # 示例项目
│
├── handoffs/                   # Agent交接记录
├── tests/                      # 测试用例+证据
├── skills/                     # 可复用技能包
│   └── k13-version-tree/           # K13版本树Skill
│
├── course/                     # 课程学习材料（归档）
│   ├── 关卡6-交付自检清单.md
│   ├── 关卡7-上下游分析与连接判断.md
│   ├── 关卡8-Agent接力验证报告.md
│   ├── 关卡9-企业AI服务方案.md
│   └── methodology/               # 方法论技能包
│       ├── SKILL.md
│       ├── modules/                # 6大模块
│       └── checklists/             # 4个检查清单
│
├── comfyui/                    # ComfyUI安装（图片生成引擎）
│
├── assets/                     # 全局素材（字体/LUT/参考图/水印）
├── logs/                       # 运行日志
│
├── AGENTS.md                   # Agent框架配置
├── MEMORY.md                   # 记忆系统配置
├── USER.md                    # 用户配置
├── config.yaml                # 系统配置（KIMI K2.6）
└── vram_scheduler.py          # VRAM调度器（显存锁，防多Agent冲突）
```

## 分离原则

| 类型 | 位置 | 说明 |
|------|------|------|
| **正式项目代码** | `tools/` `roles/` `web/` | 核心开发产物 |
| **项目文档** | `docs/` | 方案、说明书、记忆 |
| **课程学习材料** | `course/` | 关卡产出物+方法论（归档参考） |
| **运行时数据** | `projects/` `handoffs/` | 项目实例和交接记录 |
| **基础设施** | `comfyui/` `config.yaml` | ComfyUI引擎和系统配置 |

## 后续新增文件规则

- 新Agent Profile → `roles/<agent_name>/`
- 新工具 → `tools/<tool_name>.py`
- 新前端页面 → `web/<page_name>/`
- 新项目文档 → `docs/`
- 测试文件 → `tests/`
