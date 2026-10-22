# -*- coding: utf-8 -*-
"""test_crew_bus — T1 验收断言自测（R0 计划 §3 T1 A1~A4，真实运行）

运行：C:\\Users\\LZH\\.workbuddy\\binaries\\python\\3.13.12\\python.exe tools\\test_crew_bus.py
退出码：0 = 全绿；非 0 = 有断言失败。

说明：
- A1 直接对正式落档库 runtime/crew_bus.db 验证 PRAGMA（journal_mode=wal 持久、
  busy_timeout 由 crew_bus.connect() 设置 ≥5000）；
- A2/A3 使用独立测试库 runtime/crew_bus_test_a2.db / _a3.db，避免 800+ 条
  测试事件污染正式事件账本（正式库只做 A1 的 PRAGMA 验证）；
- A4 以 os.walk 扫描 tools/ 与 pipeline/ 的 .py 文件统计含 "crew_bus" 的文件数；
- A5 水位表跨进程：以 --replay-child 子命令起独立 python 进程执行
  replay_unconsumed，验证 consumers.last_seq 持久化跨进程生效（增量语义）。
"""
import multiprocessing as mp
import os
import sqlite3
import subprocess
import sys
import time

TOOLS_DIR = os.path.dirname(os.path.abspath(__file__))
ROOT_DIR = os.path.dirname(TOOLS_DIR)
RUNTIME_DIR = os.path.join(ROOT_DIR, "runtime")
REAL_DB = os.path.join(RUNTIME_DIR, "crew_bus.db")
A2_DB = os.path.join(RUNTIME_DIR, "crew_bus_test_a2.db")
A3_DB = os.path.join(RUNTIME_DIR, "crew_bus_test_a3.db")

if TOOLS_DIR not in sys.path:
    sys.path.insert(0, TOOLS_DIR)

RESULTS = []


def check(name, ok, detail=""):
    RESULTS.append((name, bool(ok)))
    print(f"  {'✓' if ok else '✗'} {name}" + (f"  [{detail}]" if detail else ""))


def _rm_db(path):
    for suf in ("", "-wal", "-shm"):
        p = path + suf
        if os.path.exists(p):
            try:
                os.remove(p)
            except OSError:
                pass


# ---------- A2 子进程：并发写者（必须顶层定义，Windows spawn 可 pickle）----------

def _writer_proc(proc_id, db_path, n):
    sys.path.insert(0, TOOLS_DIR)
    import crew_bus
    bus = crew_bus.CrewBus(db_path)
    for i in range(n):
        bus.publish("test.tick", f"p{proc_id}", {"i": i},
                    idem_key=f"p{proc_id}:{i}")


def _slow_writer_proc(db_path, n, delay):
    """慢速写者：模拟被 kill -9 的进程（每条 commit 后 sleep）。"""
    sys.path.insert(0, TOOLS_DIR)
    import crew_bus
    bus = crew_bus.CrewBus(db_path)
    for i in range(n):
        bus.publish("test.crash", "killed-proc", {"i": i},
                    idem_key=f"crash:{i}")
        time.sleep(delay)


# ---------- 各断言 ----------

def a1_pragma():
    print("\nA1 · PRAGMA 验证（正式库 runtime/crew_bus.db）")
    import crew_bus
    bus = crew_bus.CrewBus(REAL_DB)  # 经正式 connect() 路径建连
    conn = bus.connect()
    jm = conn.execute("PRAGMA journal_mode").fetchone()[0]
    bt = conn.execute("PRAGMA busy_timeout").fetchone()[0]
    print(f"  journal_mode={jm} busy_timeout={bt}")
    check("A1 journal_mode == wal", jm == "wal", f"journal_mode={jm}")
    check("A1 busy_timeout >= 5000", bt >= 5000, f"busy_timeout={bt}")
    # 独立只读连接复核 journal_mode 持久性
    ro = sqlite3.connect(REAL_DB)
    jm2 = ro.execute("PRAGMA journal_mode").fetchone()[0]
    ro.close()
    check("A1 独立连接复核 journal_mode == wal", jm2 == "wal", f"journal_mode={jm2}")
    bus.close()


def a2_concurrency_and_crash():
    print("\nA2 · 并发 8 进程 × 100 事件 + kill 中途强杀 + 启动重放（测试库）")
    import crew_bus
    _rm_db(A2_DB)
    n_procs, n_events = 8, 100
    procs = [mp.Process(target=_writer_proc, args=(p, A2_DB, n_events))
             for p in range(n_procs)]
    for p in procs:
        p.start()
    for p in procs:
        p.join(120)
    bus = crew_bus.CrewBus(A2_DB)
    conn = bus.connect()
    total = conn.execute("SELECT COUNT(*) c FROM events").fetchone()["c"]
    print(f"  并发落档计数 = {total}")
    check("A2 并发 8×100 → events = 800", total == n_procs * n_events, f"count={total}")
    bus.close()  # 关闭句柄后才能在 Windows 上删除测试库

    # --- kill 模拟：慢速写者写到一半被 terminate 强杀 ---
    _rm_db(A2_DB)
    victim = mp.Process(target=_slow_writer_proc, args=(A2_DB, 60, 0.03))
    victim.start()
    # 轮询等待 victim 真正开始写（Windows spawn 冷启动需数百 ms），确保强杀
    # 发生在"已 commit 若干条、尚有未写"的中间态
    reader = None
    killed_at = 0
    deadline = time.time() + 15
    while time.time() < deadline:
        try:
            if reader is None:
                reader = sqlite3.connect(A2_DB)
            killed_at = reader.execute(
                "SELECT COUNT(*) FROM events WHERE type='test.crash'").fetchone()[0]
            if killed_at >= 3:
                break
        except sqlite3.OperationalError:
            pass  # 库/表尚未建好，继续等
        time.sleep(0.05)
    victim.terminate()       # 强杀（Windows TerminateProcess ≈ kill -9）
    victim.join(10)
    if reader is not None:
        reader.close()
    print(f"  强杀前已落档 {killed_at} 条（<60 即证明确实中途强杀）")
    check("A2 强杀发生在写完之前（落档 <60）", 0 < killed_at < 60, f"killed_at={killed_at}")

    # --- 重启进程语义：新进程（本进程）重开 dispatcher 调用 replay_unconsumed() ---
    bus = crew_bus.CrewBus(A2_DB)
    conn = bus.connect()
    seen = set()
    dup_deliveries = [0]
    delivered_count = [0]

    def handler(ev):
        if ev["idem_key"] in seen:
            dup_deliveries[0] += 1
        seen.add(ev["idem_key"])
        delivered_count[0] += 1

    delivered, dups = bus.replay_unconsumed(handler=handler)
    db_count = conn.execute("SELECT COUNT(*) c FROM events").fetchone()["c"]
    wm = conn.execute("SELECT last_seq FROM consumers WHERE name='default'").fetchone()
    print(f"  重放：落档 {db_count} 条 → 广播投递 {delivered} 条，idem 重复跳过 {dups} 条，"
          f"水位 last_seq={wm[0] if wm else None}")
    check("A2 落档计数 == 广播去重后投递计数", db_count == delivered == delivered_count[0],
          f"db={db_count} delivered={delivered}")
    check("A2 重复投递 = 0", dups == 0 and dup_deliveries[0] == 0,
          f"replay_dups={dups} handler_dups={dup_deliveries[0]}")
    check("A2 水位推进到落档末位", wm is not None and wm[0] == db_count,
          f"last_seq={wm[0] if wm else None} db={db_count}")
    # 二次重放：水位已在末位 → 增量为空，零投递零跳过
    delivered2, dups2 = bus.replay_unconsumed(handler=handler)
    check("A2 二次重放零投递零跳过（水位增量语义）", delivered2 == 0 and dups2 == 0,
          f"delivered2={delivered2} dups2={dups2}")
    bus.close()


def a3_order_before_broadcast():
    print("\nA3 · 先落档后广播顺序断言（回调内 SELECT 该事件已存在，100 次）")
    import crew_bus
    _rm_db(A3_DB)
    bus = crew_bus.CrewBus(A3_DB)
    hits = [0]
    misses = []

    def checker(ev):
        # 回调内用独立只读连接查库：能查到本事件即证明 commit 先于广播
        c = sqlite3.connect(A3_DB)
        row = c.execute("SELECT 1 FROM events WHERE seq=?", (ev["seq"],)).fetchone()
        c.close()
        if row:
            hits[0] += 1
        else:
            misses.append(ev["seq"])

    bus.subscribe(checker)
    for i in range(100):
        bus.publish("test.order", f"agg-{i}", {"i": i}, idem_key=f"order:{i}")
    print(f"  回调内查到已落档事件 {hits[0]}/100 次")
    check("A3 100 次发布全部命中（先落档后广播）", hits[0] == 100 and not misses,
          f"hits={hits[0]} misses={len(misses)}")
    # 附带验证：广播回调异常不影响落档
    def bad_cb(ev):
        raise RuntimeError("故意异常")
    bus.subscribe(bad_cb)
    seq = bus.publish("test.order", "agg-x", {}, idem_key="order:bad-cb")
    ok = seq is not None and sqlite3.connect(A3_DB).execute(
        "SELECT 1 FROM events WHERE seq=?", (seq,)).fetchone() is not None
    check("A3+ 回调异常不影响落档", ok, f"seq={seq}")
    bus.close()


def replay_child(db_path, consumer, out_path):
    """--replay-child 子命令：独立 python 进程执行一次 replay_unconsumed。

    用于验证水位表跨进程生效：本进程是全新 dispatcher（空的
    _delivered_idems），若仍只投递增量而非全量，唯一解释是水位持久化生效。
    结果 JSON 落 out_path：{"delivered": n, "dups": n}。
    """
    import json
    sys.path.insert(0, TOOLS_DIR)
    import crew_bus
    bus = crew_bus.CrewBus(db_path)
    delivered, dups = bus.replay_unconsumed(consumer=consumer)
    bus.close()
    with open(out_path, "w", encoding="utf-8") as f:
        json.dump({"delivered": delivered, "dups": dups}, f)


def a5_watermark_cross_process():
    print("\nA5 · 水位表跨进程生效（独立新进程执行 replay_unconsumed）")
    import json
    import crew_bus
    a5_db = os.path.join(RUNTIME_DIR, "crew_bus_test_a5.db")
    a5_out = a5_db + ".out.json"
    _rm_db(a5_db)
    consumer = "wtest"

    def run_child():
        r = subprocess.run(
            [sys.executable, os.path.abspath(__file__),
             "--replay-child", a5_db, consumer, a5_out],
            capture_output=True, text=True, timeout=120)
        if r.returncode != 0:
            print(f"  [子进程异常] {r.stderr[-500:]}")
        with open(a5_out, encoding="utf-8") as f:
            return json.load(f)

    bus = crew_bus.CrewBus(a5_db)
    for i in range(5):
        bus.publish("test.wm", f"a-{i}", {"i": i}, idem_key=f"wm1:{i}")
    res1 = run_child()
    print(f"  独立进程首轮重放：{res1}")
    check("A5 独立进程首轮重放 delivered=5 / dups=0",
          res1 == {"delivered": 5, "dups": 0}, f"res={res1}")
    # 父进程是另一个全新会话：若水位未持久化，这里会重放全部 5 条
    delivered2, dups2 = bus.replay_unconsumed(consumer=consumer)
    check("A5 水位跨进程生效：无增量时会话重放 delivered=0",
          delivered2 == 0 and dups2 == 0, f"delivered2={delivered2} dups2={dups2}")
    # 追加 3 条 → 任意新进程只重放增量
    for i in range(3):
        bus.publish("test.wm", f"b-{i}", {"i": i}, idem_key=f"wm2:{i}")
    res2 = run_child()
    print(f"  追加 3 条后独立进程重放：{res2}")
    check("A5 增量重放只投递新增 3 条", res2 == {"delivered": 3, "dups": 0},
          f"res={res2}")
    last = bus.connect().execute(
        "SELECT last_seq FROM consumers WHERE name=?", (consumer,)).fetchone()[0]
    check("A5 水位推进到 8", last == 8, f"last_seq={last}")
    bus.close()


def a4_real_callers():
    print("\nA4 · 消零引用：grep crew_bus 引用文件数（tools/ pipeline/）")
    hits = []
    for sub in ("tools", "pipeline"):
        d = os.path.join(ROOT_DIR, sub)
        if not os.path.isdir(d):
            continue
        for dirpath, _dirnames, filenames in os.walk(d):
            for fn in filenames:
                if fn.endswith(".py"):
                    p = os.path.join(dirpath, fn)
                    try:
                        with open(p, encoding="utf-8", errors="replace") as f:
                            if "crew_bus" in f.read():
                                hits.append(os.path.relpath(p, ROOT_DIR))
                    except OSError:
                        pass
    hits.sort()
    for h in hits:
        print(f"  {h}")
    check("A4 含 crew_bus 的 .py 文件数 >= 2", len(hits) >= 2, f"files={len(hits)}")
    # 复核至少有一个真实调用方（非 crew_bus 自身/测试）
    callers = [h for h in hits
               if os.path.basename(h) not in ("crew_bus.py", "test_crew_bus.py")]
    check("A4 存在真实下游调用方（jobs.py / jobs_events.py）", len(callers) >= 1,
          f"callers={callers}")
    return 2 if (len(hits) >= 2 and callers) else 0


def main():
    mp.freeze_support()
    # --replay-child <db> <consumer> <out_json>：独立进程重放模式（供 A5 调用）
    if len(sys.argv) >= 2 and sys.argv[1] == "--replay-child":
        replay_child(*sys.argv[2:5])
        return 0
    failures = 0
    a1_pragma()
    a2_concurrency_and_crash()
    a3_order_before_broadcast()
    a5_watermark_cross_process()
    n_hits = a4_real_callers()
    print("\n自检结果：")
    for name, ok in RESULTS:
        print(f"  {'✓' if ok else '✗'} {name}")
        if not ok:
            failures += 1
    print(("PASS" if failures == 0 else f"FAIL（{failures} 项未过）"),
          f"（A4 引用文件数={n_hits}）")
    return 0 if failures == 0 else 4


if __name__ == "__main__":
    sys.exit(main())
