# -*- coding: utf-8 -*-
"""crew_bus — AI 影视团队 v2 事件总线（R8-C-1 契约五要素，纯标准库实现）

实现 R8-C-1 五要素（事实源：docs/03-规划与调研/R0-执行计划.md §3 T1）：
  1. SQLite 落档：events(seq, ts, type, aggregate_id, payload_json, idem_key)，
     连接设 PRAGMA journal_mode=WAL + PRAGMA busy_timeout=5000；
     idem_key 建唯一索引（同键重复 publish 幂等命中：不重复落档、不重复广播）。
  2. 单写者串行写：进程内一把可重入锁（threading.RLock）保证同进程串行；
     跨进程由 WAL + busy_timeout 保证写事务串行。
     dispatcher 单实例语义（R8-争议③）：本模块的 dispatcher = 连接 + 订阅者注册表
     + 已投递 idem 集合，同进程内只经 get_bus() 取单例；多进程各自持有独立
     dispatcher——落档层共享同一 SQLite 库（天然一致），广播/重放仅作用于本进程
     订阅者（本地语义）。禁止在同进程内 new 多个 CrewBus 写同一库。
  3. 先落档后广播：publish() 先 INSERT 并 commit，事务提交成功后才逐个回调
     订阅者；任一回调异常被捕获记录，绝不影响落档（R8-P1 QA 顺序断言）。
  4. 启动重放（水位表方案）：replay_unconsumed(consumer=...) 只重放
     consumers.last_seq 之后的增量（seq 升序），投递成功后推进水位。
     零丢失零重复（R0-O17）现为**跨重启成立**的两层保障：
       第一层 水位表（持久化）：挡跨重启——last_seq 之前的区间永不重放；
       第二层 _delivered_idems（进程内会话集合）：挡单会话——同会话内
         同一 idem_key 最多投递一次（含 publish 已广播过的事件）。
     崩溃窗口说明：采用"先投递后推进水位"（水位先行会丢事件），
     崩溃于"投递完成、水位未推进"之间时，最坏情况是重启后重放已投递
     的区间——由订阅者按 idem_key 幂等兜底（R8 契约：订阅者必须幂等）。
  5. 真实下游接线：tools/jobs.py 状态变更处经最小侵入 hook 发布 job.* 事件
     （消 R-SCALE-CB"代码零引用"空心阻断）。

数据库落 <v2>/runtime/crew_bus.db（可用环境变量
CREW_BUS_DB 覆盖；目录不存在自动创建）。与 tools/jobs.py 的 WAL 机制互不
干扰，crew_bus 为独立事件层（R0 计划 T1 步骤 4）。

用法：
  import crew_bus
  crew_bus.subscribe(lambda ev: print(ev["type"], ev["payload"]))
  seq = crew_bus.publish("job.submitted", "42", {"state": "submitted"},
                         idem_key="job:42:submitted:1730000000")
  crew_bus.replay_unconsumed()   # 进程启动时调用一次
"""
import hashlib
import json
import os
import sqlite3
import sys
import threading
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DB_PATH = os.environ.get("CREW_BUS_DB") or str(ROOT / "runtime" / "crew_bus.db")

_SCHEMA = """
CREATE TABLE IF NOT EXISTS events(
  seq INTEGER PRIMARY KEY AUTOINCREMENT,
  ts TEXT,
  type TEXT,
  aggregate_id TEXT,
  payload_json TEXT,
  idem_key TEXT);
CREATE UNIQUE INDEX IF NOT EXISTS idx_events_idem ON events(idem_key);
CREATE TABLE IF NOT EXISTS consumers(
  name TEXT PRIMARY KEY,
  last_seq INTEGER NOT NULL DEFAULT 0);
"""


class CrewBus:
    """事件总线 dispatcher（单实例语义见模块 docstring，R8-争议③）。"""

    def __init__(self, db_path=None):
        # db_path 为 None 时用模块默认路径；测试可用独立库避免污染正式落档
        self.db_path = db_path or DB_PATH
        self._lock = threading.RLock()      # 进程内单写者锁（要素 2）
        self._conn = None                   # 单连接（同 dispatcher 内串行复用）
        self._subscribers = []              # 订阅者回调列表（广播目标）
        self._delivered_idems = set()       # 本进程已投递 idem_key（重放去重依据）

    # ---------- 连接与 schema ----------

    def connect(self):
        """惰性建连：WAL + busy_timeout=5000 + 建表/唯一索引（要素 1）。

        多进程并发冷启动时 DDL 是竞争热点：表已齐则跳过建表（含旧库
        补建 consumers 水位表）；仍遇锁竞争（OperationalError）则退避重试 4 次。
        """
        if self._conn is not None:
            return self._conn
        d = os.path.dirname(self.db_path)
        if d:
            os.makedirs(d, exist_ok=True)
        last_exc = None
        for attempt in range(4):
            c = None
            try:
                c = sqlite3.connect(self.db_path, timeout=10, check_same_thread=False)
                c.row_factory = sqlite3.Row
                c.execute("PRAGMA journal_mode=WAL")
                c.execute("PRAGMA busy_timeout=5000")
                # 多进程并发冷启动时 DDL 是竞争热点：两张表都存在则跳过
                # 建表（兼容既有旧库缺 consumers 表的情况，_SCHEMA 幂等）；
                # 仍遇锁竞争（OperationalError）则小步退避重试 4 次。
                missing = [t for t in ("events", "consumers") if not c.execute(
                    "SELECT 1 FROM sqlite_master WHERE type='table' AND name=?",
                    (t,)).fetchone()]
                if missing:
                    c.executescript(_SCHEMA)
                    c.commit()
                self._conn = c
                return c
            except sqlite3.OperationalError as exc:
                last_exc = exc
                if c is not None:
                    try:
                        c.close()
                    except sqlite3.Error:
                        pass
                time.sleep(0.15 * (attempt + 1))
        raise last_exc

    def close(self):
        with self._lock:
            if self._conn is not None:
                try:
                    self._conn.close()
                finally:
                    self._conn = None

    # ---------- 订阅 ----------

    def subscribe(self, callback):
        """注册广播回调。回调签名 callback(event: dict)，异常由总线吞掉并记录。"""
        if not callable(callback):
            raise TypeError("callback 必须可调用")
        with self._lock:
            if callback not in self._subscribers:
                self._subscribers.append(callback)
        return callback

    def unsubscribe(self, callback):
        with self._lock:
            if callback in self._subscribers:
                self._subscribers.remove(callback)

    # ---------- 发布（先落档后广播，要素 3）----------

    def publish(self, event_type, aggregate_id="", payload=None,
                idem_key=None, ts=None):
        """发布事件：先 INSERT+commit 落档，成功后逐个回调订阅者。

        返回落档 seq；idem_key 幂等命中（库里已有同键）时返回既有 seq 且
        不重复落档、不重复广播。回调异常只记录，不影响落档与后续订阅者。
        """
        if not isinstance(event_type, str) or not event_type:
            raise ValueError("event_type 必须为非空字符串")
        payload_json = json.dumps(payload if payload is not None else {},
                                  ensure_ascii=False, sort_keys=True)
        if idem_key is None:
            # 未显式给键时按内容定键（同内容重复发布幂等命中）
            idem_key = hashlib.sha1(
                f"{event_type}|{aggregate_id}|{payload_json}".encode("utf-8")
            ).hexdigest()
        ts_str = ts or time.strftime("%Y-%m-%dT%H:%M:%S", time.localtime())
        with self._lock:
            conn = self.connect()
            try:
                cur = conn.execute(
                    "INSERT INTO events(ts,type,aggregate_id,payload_json,idem_key) "
                    "VALUES(?,?,?,?,?)",
                    (ts_str, event_type, str(aggregate_id), payload_json, idem_key))
                conn.commit()
            except sqlite3.IntegrityError:
                conn.rollback()
                row = conn.execute("SELECT seq FROM events WHERE idem_key=?",
                                   (idem_key,)).fetchone()
                return row["seq"] if row else None
            seq = cur.lastrowid
            event = {"seq": seq, "ts": ts_str, "type": event_type,
                     "aggregate_id": str(aggregate_id),
                     "payload": json.loads(payload_json),
                     "payload_json": payload_json, "idem_key": idem_key}
            # 落档已 commit，标记本进程已投递（后续重放不会重复投给本进程订阅者）
            self._delivered_idems.add(idem_key)
            for cb in list(self._subscribers):
                try:
                    cb(event)
                except Exception as exc:  # 回调异常不得影响落档（要素 3）
                    print(f"[crew_bus] 订阅者回调异常（已忽略，落档不受影响）: {exc}",
                          file=sys.stderr)
        return seq

    # ---------- 启动重放（要素 4：水位表增量重放）----------

    def _get_last_seq(self, conn, consumer):
        row = conn.execute("SELECT last_seq FROM consumers WHERE name=?",
                           (consumer,)).fetchone()
        return row["last_seq"] if row else 0

    def _advance_watermark(self, conn, consumer, seq):
        """水位只进不退（并发/乱序安全）。"""
        conn.execute(
            "INSERT INTO consumers(name,last_seq) VALUES(?,?) "
            "ON CONFLICT(name) DO UPDATE SET last_seq=excluded.last_seq "
            "WHERE excluded.last_seq>consumers.last_seq",
            (consumer, seq))
        conn.commit()

    def replay_unconsumed(self, handler=None, consumer="default"):
        """按水位增量重放：只处理 seq > consumers.last_seq 的事件（seq 升序）。

        零丢失零重复（R0-O17）两层保障（语义详见模块 docstring 要素 4）：
        - 水位表（持久化）挡跨重启：last_seq 之前永不重放；
        - _delivered_idems（进程内）挡单会话：同会话内同一 idem_key 至多投递一次。
        推进策略为"先投递后推进水位"（逐条提交）：崩溃最坏重放已投递区间，
        由订阅者按 idem_key 幂等兜底（R8 契约）。

        参数：
            handler: 为 None 时投给已注册订阅者；否则只投给该 handler。
            consumer: 消费者名（水位键）；不同消费者各自独立水位。
        返回：
            (delivered, duplicates)：delivered=实际投递条数；
            duplicates=本会话已投递（idem 命中）被跳过条数（跳过时同样推进
            水位，保证幂等事件不阻塞水位前进）。
        """
        targets = [handler] if handler is not None else list(self._subscribers)
        delivered = duplicates = 0
        with self._lock:
            conn = self.connect()
            last_seq = self._get_last_seq(conn, consumer)
            rows = conn.execute(
                "SELECT seq,ts,type,aggregate_id,payload_json,idem_key FROM events "
                "WHERE seq>? ORDER BY seq ASC", (last_seq,)).fetchall()
            for r in rows:
                idem = r["idem_key"]
                if idem in self._delivered_idems:
                    duplicates += 1
                    self._advance_watermark(conn, consumer, r["seq"])
                    continue
                self._delivered_idems.add(idem)
                event = {"seq": r["seq"], "ts": r["ts"], "type": r["type"],
                         "aggregate_id": r["aggregate_id"],
                         "payload": json.loads(r["payload_json"] or "{}"),
                         "payload_json": r["payload_json"], "idem_key": idem}
                for cb in targets:
                    try:
                        cb(event)
                    except Exception as exc:  # 重放不因单条回调失败而中断
                        print(f"[crew_bus] 重放回调异常（已忽略）: {exc}",
                              file=sys.stderr)
                delivered += 1
                # 先投递后推进水位（见 docstring 崩溃窗口说明）
                self._advance_watermark(conn, consumer, r["seq"])
        return delivered, duplicates

    # ---------- 观测辅助 ----------

    def count(self):
        """events 总条数。"""
        with self._lock:
            return self.connect().execute("SELECT COUNT(*) c FROM events").fetchone()["c"]


# ---------- 进程内单例 dispatcher（R8-争议③）----------

_default_bus = None
_default_bus_lock = threading.Lock()


def get_bus(db_path=None):
    """取本进程默认 dispatcher（单实例）；首次调用可指定库路径。"""
    global _default_bus
    with _default_bus_lock:
        if _default_bus is None:
            _default_bus = CrewBus(db_path)
        return _default_bus


def subscribe(callback):
    return get_bus().subscribe(callback)


def unsubscribe(callback):
    get_bus().unsubscribe(callback)


def publish(event_type, aggregate_id="", payload=None, idem_key=None, ts=None):
    return get_bus().publish(event_type, aggregate_id, payload,
                             idem_key=idem_key, ts=ts)


def replay_unconsumed(handler=None, consumer="default"):
    return get_bus().replay_unconsumed(handler=handler, consumer=consumer)


def count():
    return get_bus().count()


if __name__ == "__main__":
    # 轻量观测入口：python crew_bus.py → 打印落档统计
    b = get_bus()
    print(f"db={b.db_path} events={b.count()}")
