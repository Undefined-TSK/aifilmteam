# B17D_ARCHIVE_LOG — 17d 盘点去向表·机械归档执行记录

> 执行：b17d-exec（工程师寇豆码）｜日期：2026-10-04｜依据：docs/02-决策/17d-全链路操作员架构-重构版.md §6/§7（B17d-2 采纳）
> 归档方式：mv（零删除）→ `_legacy_projects/v2-intermediate/tools_archive_b17d/`（新建目录）
> 归档前全根 grep（AI影视团队v2 + runtime + outputs + mcp_blender）引用检查，mcp_blender 目录当前不存在（#40 试点未落盘，无文件可检查）。

## 一、归档清单（10 件）

| # | 原路径 | 新路径 | 17d 依据 | 引用检查结果 |
|---|---|---|---|---|
| 1 | AI影视团队v2/tools/blockout_min_v1.py | _legacy_projects/v2-intermediate/tools_archive_b17d/blockout_min_v1.py | §7.2 废弃（归档）推荐 b | 活动 .py 零 import；文字引用见下「三」 |
| 2 | AI影视团队v2/tools/make_r4_l1_blockout.py | _legacy_projects/v2-intermediate/tools_archive_b17d/make_r4_l1_blockout.py | §7.2 废弃（归档）推荐 b | 活动 .py 零 import；blockout_batch_render.py docstring 提及（注释性，见三） |
| 3 | AI影视团队v2/tools/wan22_client.py | _legacy_projects/v2-intermediate/tools_archive_b17d/wan22_client.py | §7.2 废弃（归档 _legacy）推荐 b | 活动 .py 零 import；文字引用见下「三」 |
| 4 | AI影视团队v2/tools/wan22_shots_33_41.py | _legacy_projects/v2-intermediate/tools_archive_b17d/wan22_shots_33_41.py | §7.2 废弃（归档 _legacy）推荐 b | 仅 wan22_shots_33_41.py:12 `from wan22_client import generate_video`——指向同组归档件，两者同目录归档后 import 链路仍完整 |
| 5 | runtime/refimg_batch.py | _legacy_projects/v2-intermediate/tools_archive_b17d/refimg_batch.py | §7.2 提炼为 cloud_repaint 参数模板，原件归档（推荐 b） | 全根 grep 零引用 |
| 6 | runtime/i2v_task_submit.txt | _legacy_projects/v2-intermediate/tools_archive_b17d/i2v_task_submit.txt | 同上（VACE/Wan 请求实测样本） | 全根 grep 零引用 |
| 7 | runtime/video_task_submit.txt | _legacy_projects/v2-intermediate/tools_archive_b17d/video_task_submit.txt | 同上 | 全根 grep 零引用 |
| 8 | runtime/wan30_shot_task.txt | _legacy_projects/v2-intermediate/tools_archive_b17d/wan30_shot_task.txt | 同上 | 全根 grep 零引用 |
| 9 | runtime/img30_result.json | _legacy_projects/v2-intermediate/tools_archive_b17d/img30_result.json | 同上 | 全根 grep 零引用 |
| 10 | runtime/music_result.json | _legacy_projects/v2-intermediate/tools_archive_b17d/music_result.json | 同上 | 全根 grep 零引用 |

注：#5–#10 的 `runtime/` 指**项目根级** `D:\aifilmteam\runtime\`（17d 文档同路径写法的 runtime/llm_router.json 亦在此目录，一致）。该目录其余文件（llm_router.json、secrets/、dashscope_*、llm_local_test.py、ollama_warm.json、bailian_models_408.md、README.md）为 17d §7.1 保留件/保护件，未动。

## 二、暂缓项

**无暂缓项。** 全部 10 件归档前引用检查均未发现「保留为工具的活动 .py 对其的 import/调用链路」，未弄断任何在用链路。

## 三、遗留文字性引用（非执行链路，归档不阻断，登记备查）

以下引用为注释、docstring、字符串内容或文档描述，非 import/调用，不构成执行链路，故不阻断归档；相关文档未改（docs/ 只读不动，AGENTS.md/PROJECT_STATE.md 属登记文档不在本任务改写范围）：

1. `AI影视团队v2/tools/blockout_batch_render.py:93`（docstring：「风格沿用 make_r4_l1_blockout.py 的占位几何体路线」）——该文件为保护对象，未改动。
2. `AI影视团队v2/tools/jobs.py:5`（docstring 提及「wan22_client 实测」）——历史教训描述，未改动。
3. `AI影视团队v2/tools/_probes/_tmp_wan22_handoff.py:25`（字符串中提及 wan22 两脚本）——探针件按 §7.4 保留，未改动。
4. `AI影视团队v2/AGENTS.md:26,31`（引擎入口清单列 wan22_client.py、blockout_min_v1.py）——登记文档，待后续按 17d §7 统一改写。
5. `AI影视团队v2/PROJECT_STATE.md:80,111`（目录树与进度描述提及归档件）——登记文档，待后续改写。
6. `AI影视团队v2/agents/blockout/SKILL.md:31`（提及 blockout_min_v1 为 blockout_build.py 的前身）——技能包按 §7.4 保留，未改动。
7. `AI影视团队v2/projects/雨夜寻猫/00_brief/` 下镜头清单与 handoff（EDIT-20260926-36DA.json 等）提及 wan22 两脚本可复用——**保护项目，全部未动**；引用为历史 handoff 记录。
8. docs/、_legacy/、_legacy_projects/ 下多处历史文档引用——历史记录，按纪律不动。

## 四、旧岗位卡（P2/P3/P5）核查结论

§6.3 第⑤项 P2 agent_scene_architect / P3 agent_blockout_builder+P4 agent_blockout_animator / P5 agent_blockout_qa 的旧岗位定义**仅存在于 17 号草案文档章节内**（docs/02-决策/17-baimo-intent-pipeline-draft.md），无以旧五岗命名的独立文件，故无独立文件可归档（文档是历史记录，按纪律不动）。

`AI影视团队v2/agents/` 下现有角色卡（director/blockout/previs/producer/realizer/screenwriter/script_supervisor）属 §7.6 / B17d-5「旧角色卡归档 _legacy_roles、新卡另建」范畴——其前提「新卡（五操作员角色卡）另建」尚未发生，且其中 blockout 技能包可能被 #40 MCP 试点在用，本任务不予归档，待 B17d-5 新卡建设时一并处理。

## 五、验证断言实测结果

| 断言 | 结果 |
|---|---|
| 1. 归档文件在新位置存在且原位置不存在 | **PASS**：10 件均在新目录存在（ls -la 确认），10 个原路径逐一经 `[ -e ]` 断言 GONE-OK |
| 2. grep 活动区对已归档文件的执行性引用 = 0 | **PASS**：活动区（tools/pipeline/blender/spec/config/web/runtime）.py 匹配仅 3 处，全部为 docstring/注释/字符串（见三），import 仅归档组内部互引（#4） |
| 3. 既有测试 | test_crew_bus.py **全 PASS**（含 A4/A5 全部断言）；test_schema_patch.py **17/17 全 PASS**（IS_PASS: YES，经 Python 3.12 运行，jsonschema 装于该解释器）；test_llm_gateway.py 2/4 PASS——T1 本地 chat / T2 本地 structured FAIL 原因为本地 ollama 服务离线（curl 127.0.0.1:11434 连接拒绝，error 10061），llm_gateway.py 与 runtime/llm_router.json 均未动、归档件与 gateway 零 import 关系，FAIL 与本此归档无关 |
| 4. 本日志完整 | PASS |

## 六、备注

- 归档零删除，回退方式：将文件 mv 回原路径即可。
- §7.2 #5–#10 按 17d 表格属「改写→提炼为 cloud_repaint 参数模板，**原件归档**」——提炼工作（cloud_repaint 参数模板）属 B17d-2 改写线，尚未执行；原件已入归档目录，提炼时可从新路径读取。此顺序偏差如实登记。
