# -*- coding: utf-8 -*-
"""jobs_events — jobs.py 状态变更 → crew_bus `job.*` 事件适配层（T1 接线验证）

R0 计划 T1 步骤 5 要求至少接 1 个真实下游发布 `job.*` 事件，消除
R-SCALE-CB "crew_bus 代码零引用"空心阻断。jobs.py 是单文件 CLI 账本，
为保持其最小侵入（R0 计划 T1 步骤 4：jobs.py 的 WAL 机制保持不动），
本模块把"作业状态变更 → 事件发布"的细节收敛于此：

- 事件类型：`job.<state>`（submitted / running / succeeded / failed /
  cancelled / unknown），aggregate_id = 作业 id；
- idem_key = `job:<id>:<state>:<updated_ts>`：同一作业同一次状态迁移
  （同一 updated 时间戳）重复发布幂等命中，跨状态/跨迁移互不冲突；
- 失败安全：任何 crew_bus 异常只打警告，绝不影响 jobs.py 落账主流程。

jobs.py 在各状态变更点 commit 之后调用 emit_job_event()（先落账后发事件，
顺序语义与 crew_bus "先落档后广播"一致）。
"""
import os
import sys

_TOOLS_DIR = os.path.dirname(os.path.abspath(__file__))
if _TOOLS_DIR not in sys.path:
    sys.path.insert(0, _TOOLS_DIR)


def emit_job_event(jid, state, updated_ts, extra=None):
    """发布 `job.<state>` 事件。

    参数：
        jid: 作业 id（aggregate_id）
        state: 迁移后的状态字符串
        updated_ts: 该次状态迁移写入 jobs.updated 的时间戳（进 idem_key）
        extra: 附加业务字段（engine/shot/reason 等），并入 payload
    返回：
        crew_bus.publish() 的 seq（int）；发布失败返回 None。
    """
    try:
        import crew_bus
        payload = {"job_id": jid, "state": state}
        if extra:
            payload.update(extra)
        return crew_bus.publish(
            f"job.{state}", str(jid), payload,
            idem_key=f"job:{jid}:{state}:{updated_ts}")
    except Exception as exc:  # 事件层故障不得影响作业账本
        print(f"[jobs_events] job.{state} 事件发布失败（不影响作业账本）: {exc}")
        return None
