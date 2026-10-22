> 基线：../00-基线报告/项目基线报告.md ｜ 规约：../_执行须知.md ｜ 导航：../索引.html

# 维度 2 · crew_bus 事件流图（事件类型 × 消费者关系）

> 事实源：`AI影视团队v2/tools/crew_bus.py`（R8-C-1 契约五要素）、`docs/03-规划与调研/R0-执行计划.md` §3 T1。禁用 `<br>`，用「·」分隔。

---

## 1. 事件总线机制（五要素）

```mermaid
flowchart LR
    P["publish(event_type, aggregate_id, payload, idem_key)"] --> L1["① SQLite 落档 events 表"]
    L1 --> L2["② 单写者串行写 · RLock + WAL + busy_timeout=5000"]
    L2 --> L3["③ 先落档后广播 · 事务提交后才回调订阅者"]
    L3 --> L4["④ 启动重放 replay_unconsumed · 水位表 consumers.last_seq"]
    L4 --> L5["⑤ 真实下游接线 · jobs.py 发 job.* 事件"]

    classDef step fill:#16213e,stroke:#533483,color:#e8eaf0;
    class P,L1,L2,L3,L4,L5 step;
```

---

## 2. 事件类型 × 消费者关系图

```mermaid
flowchart TD
    subgraph 发布者
        JOBS["tools/jobs.py<br/>作业状态变更"]
        HANDOFF["handoff_manager<br/>交接动作（规划接线）"]
        OP["操作员节点<br/>N1~N5（C3 规划）"]
    end
    subgraph 事件总线["crew_bus · SQLite WAL"]
        E1["job.submitted<br/>作业已提交"]
        E2["job.* 状态变更<br/>完成/失败"]
        E3["handoff.* 交接事件<br/>规划中"]
        E4["shot.* 镜次事件<br/>规划中"]
        E5["cost.* 成本事件<br/>规划中"]
        E6["alert.* 告警事件<br/>规划中"]
    end
    subgraph 消费者
        C1["订阅者回调<br/>subscribe(callback)"]
        C2["剧场双出口<br/>工作台 / ntfy 告警"]
        C3["账本 cost_ledger<br/>成本记账"]
        C4["重放消费者<br/>replay_unconsumed"]
    end
    JOBS --> E1
    JOBS --> E2
    HANDOFF -.-> E3
    OP -.-> E4
    OP -.-> E5
    OP -.-> E6
    E1 --> C1
    E2 --> C1
    E3 --> C1
    E4 --> C1
    E4 --> C2
    E5 --> C3
    E6 --> C2
    C1 --> C4

    classDef impl fill:#16213e,stroke:#3fb950,color:#e8eaf0;
    classDef plan fill:#1a1a2e,stroke:#e94560,stroke-dasharray:5 5,color:#e8eaf0;
    class E1,E2,C1,C4 impl;
    class E3,E4,E5,E6,C2,C3 plan;
```

---

## 3. 事件类型现状表

| 事件类型 | 发布者 | 消费者 | 状态 |
|---|---|---|---|
| job.submitted | tools/jobs.py | 订阅者回调 | 已实现（真实接线，消「零引用」） |
| job.*（完成/失败） | tools/jobs.py | 订阅者回调 | 已实现 |
| test.tick / test.crash / test.order / test.wm | test_crew_bus.py | 测试订阅者 | 已实现（自测） |
| handoff.* | handoff_manager | 剧场出口 | 规划中（交接动作应发事件） |
| shot.* | 操作员 N1~N5 | 剧场出口 | 规划中（C3 剧场数据源） |
| cost.* | 记账层 | cost_ledger | 规划中 |
| alert.* | 熔断/告警 | ntfy / 工作台 | 规划中 |

---

## 4. 契约五要素核对

| 要素 | 实现 | 证据 |
|---|---|---|
| ① SQLite 落档 | events(seq, ts, type, aggregate_id, payload_json, idem_key) | crew_bus.py `_SCHEMA` |
| ② 单写者串行 | 进程内 RLock + WAL + busy_timeout=5000 | crew_bus.py `__init__` |
| ③ 先落档后广播 | publish 先 INSERT+commit 再回调 | crew_bus.py docstring 要素 3 |
| ④ 启动重放 | replay_unconsumed + 水位表 consumers | crew_bus.py docstring 要素 4 |
| ⑤ 真实下游 | jobs.py 状态变更 hook 发 job.* | crew_bus.py docstring 要素 5 |

---

## 5. 结论

1. **机制成熟、事件面窄**：总线本身五要素全绿（800 事件不丢，跨重启零重复），但实际接线只有 `job.*` 一类，`shot.*`/`cost.*`/`alert.*` 均待 C3 M4/M5 落地。
2. **幂等是硬契约**：idem_key 唯一索引 + 订阅者幂等要求，保证「先投递后推进水位」崩溃窗口可兜底。
3. **剧场出口待接**：事件总线是「多 Agent 剧场式可观赏协作」的数据源（业界空白），须由 C3 工作台/ntfy 双出口消费。