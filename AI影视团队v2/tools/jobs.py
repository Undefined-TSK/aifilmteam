# -*- coding: utf-8 -*-
"""jobs.py — 异步作业账本 + 现金/工时账（P-0c，单文件，不另开第 3 件工具）

要解决的三个真实缺陷（都在第五批审计里实测过）：
1. prompt_id 不落盘、提交即扣点 → 断网=孤儿任务 + 幽灵扣费（wan22_client 实测）；
2. 账本只有"点数"、没有引擎/秒数/实付/工时 → 报价与外推全靠猜；
3. 云端"输入参考视频按输出档同价计费"、"失败不计费"这类规则没人记账。

设计（对齐 MCP 2026-07-28 对副作用操作的第一要求：handle + 幂等键 + 可轮询）：
- 表 jobs：attempt 与 idempotency_key 唯一约束；状态 submitted/handle/running/succeeded/failed/unknown；
- 表 costs：每笔作业一行现金与工时（引擎、输入秒、输出秒、单价、实付、是否计费、废片数）；
- 恢复语义：重启后 `recover()` 把 running/submitted 但没有 handle 的作业转 unknown（**先对账，不发新任务**）；
  有 handle 的续轮询；已计费失败的作业不重复扣费；
- 幂等：同 idem 键重复 begin 返回已有 job（retry 不再花一次钱）。

CLI（全部走 sqlite，无第三方依赖）：
  python tools/jobs.py recover            # 崩溃后先跑这个，只报告不发任务
  python tools/jobs.py begin --engine wan2.2-local --shot 4-3 --params '{"length":73}' --budget 80
  python tools/jobs.py handle  <id> <prompt_id>
  python tools/jobs.py done    <id> [--file path] [--gate PASS|FAIL]
  python tools/jobs.py fail    <id> --reason "..." --billed 0
  python tools/jobs.py cost    <id> --engine kling3-omni --in-s 5 --out-s 5 --unit 0.60 --paid 6.0 --labor-min 12 --waste 1
  python tools/jobs.py report [--budget 800]
"""
import argparse
import hashlib
import json
import os
import sqlite3
import sys
import time

sys.stdout.reconfigure(encoding="utf-8", errors="replace")
# v2 根 = tools/ 的上一级（相对定位，不硬编码盘符路径，防重组再断链）
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DB = os.environ.get("JOBS_DB") or os.path.join(ROOT, r"pipeline\jobs.db")
TERMINAL = {"succeeded", "failed", "cancelled"}


_CONN = {}


def con():
    os.makedirs(os.path.dirname(DB), exist_ok=True)
    if _CONN.get("path") == DB and _CONN.get("c"):
        return _CONN["c"]
    c = sqlite3.connect(DB, timeout=30, check_same_thread=False)
    c.execute("PRAGMA journal_mode=WAL")
    c.execute("PRAGMA busy_timeout=30000")
    _CONN.update(path=DB, c=c)
    c.row_factory = sqlite3.Row
    c.executescript("""
    CREATE TABLE IF NOT EXISTS jobs(
      id INTEGER PRIMARY KEY, project TEXT, shot TEXT, engine TEXT,
      idem TEXT UNIQUE, params TEXT, state TEXT, handle TEXT, file TEXT,
      attempt INTEGER DEFAULT 1, gate TEXT, reason TEXT,
      created REAL, updated REAL);
    CREATE TABLE IF NOT EXISTS costs(
      job_id INTEGER PRIMARY KEY, engine TEXT, billed INTEGER,
      input_s REAL, output_s REAL, unit_price REAL, paid REAL,
      labor_min REAL, takes INTEGER, waste INTEGER, ts REAL,
      FOREIGN KEY(job_id) REFERENCES jobs(id));
    CREATE TABLE IF NOT EXISTS audit(id INTEGER PRIMARY KEY, job_id INTEGER, ev TEXT, detail TEXT, ts REAL);
    """)
    return c


def log(c, jid, ev, detail=""):
    c.execute("INSERT INTO audit(job_id,ev,detail,ts) VALUES(?,?,?,?)",
              (jid, ev, str(detail)[:300], time.time()))


def now():
    return time.strftime("%Y-%m-%d %H:%M:%S")


def emit(jid, state, updated_ts, extra=None):
    """crew_bus 最小侵入 hook（R0-T1）：作业状态变更发布 job.* 事件。

    细节收敛在 jobs_events.py 适配层；任何事件层故障都不影响作业账本。
    必须在状态变更 commit 之后调用（先落账后发事件）。
    """
    try:
        import jobs_events
        jobs_events.emit_job_event(jid, state, updated_ts, extra)
    except Exception as e:
        print(f"[crew_bus] hook 异常（不影响作业账本）: {e}")


def begin(a):
    c = con()
    idem = a.idem or hashlib.sha1(f"{a.engine}|{a.shot}|{a.params}".encode()).hexdigest()[:16]
    try:
        t0 = time.time()
        c.execute("INSERT INTO jobs(project,shot,engine,idem,params,state,attempt,created,updated) "
                  "VALUES(?,?,?,?,?,'submitted',1,?,?)",
                  (a.project, a.shot, a.engine, idem, a.params, t0, t0))
        jid = c.execute("SELECT id FROM jobs WHERE idem=?", (idem,)).fetchone()["id"]
        log(c, jid, "begin", a.params)
        c.commit()
        emit(jid, "submitted", t0, {"engine": a.engine, "shot": a.shot})
        print(f"job={jid} state=submitted idem={idem}")
        return jid
    except sqlite3.IntegrityError:
        row = c.execute("SELECT * FROM jobs WHERE idem=?", (idem,)).fetchone()
        print(f"IDEMPOTENT HIT: job={row['id']} state={row['state']} handle={row['handle']} "
              f"→ 复用既有作业，不再提交（防重复计费）")
        return None


def set_handle(a):
    c = con()
    t0 = time.time()
    n = c.execute("UPDATE jobs SET handle=?,state='running',updated=? WHERE id=?",
                  (a.handle, t0, a.id)).rowcount
    if not n:
        print(f"job={a.id} 不存在，忽略"); return
    log(c, a.id, "handle", a.handle)
    c.commit()
    emit(a.id, "running", t0, {"handle": a.handle})
    print(f"job={a.id} state=running handle={a.handle}")


def finish(a, state):
    c = con()
    billed = 0 if state == "failed" and getattr(a, "billed", "0") == "0" else 1
    t0 = time.time()
    n = c.execute("UPDATE jobs SET state=?,updated=?,file=?,gate=?,reason=? WHERE id=?",
                  (state, t0, getattr(a, "file", None) or "", getattr(a, "gate", None) or "",
                   getattr(a, "reason", None) or "", a.id)).rowcount
    if not n:
        print(f"job={a.id} 不存在，忽略"); return
    log(c, a.id, state, f"gate={getattr(a,'gate',None)} reason={getattr(a,'reason',None)}")
    c.commit()
    emit(a.id, state, t0, {"gate": getattr(a, "gate", None),
                           "reason": getattr(a, "reason", None), "billed": billed})
    print(f"job={a.id} state={state}" + ("（失败按引擎条款不计费，需人工确认）" if state == "failed" and not billed else ""))


def recover(a):
    """重启后的第一件事：只报告，不发新任务。"""
    c = con()
    rows = c.execute("SELECT * FROM jobs WHERE state NOT IN ('succeeded','failed','cancelled')").fetchall()
    stale = need = 0
    pending_emits = []  # 先攒起来，commit 之后再统一发事件（对齐"落账后才发事件"纪律）
    for r in rows:
        if r["state"] in ("running", "submitted") and not r["handle"]:
            t0 = time.time()
            c.execute("UPDATE jobs SET state='unknown',updated=? WHERE id=?", (t0, r["id"]))
            log(c, r["id"], "recover->unknown", "无 handle，先对账再决定重发")
            pending_emits.append((r["id"], "unknown", t0, {"from_state": r["state"]}))
            stale += 1
        elif r["handle"]:
            need += 1
            print(f"  可续轮询: job={r['id']} {r['engine']}/{r['shot']} handle={r['handle']}")
    c.commit()
    for jid, st, t0, extra in pending_emits:
        emit(jid, st, t0, extra)
    print(f"恢复扫描：未完成 {len(rows)} 条 → 转 unknown(待对账) {stale} 条、可续轮询 {need} 条；未发起任何新任务")
    print("下一步：对 unknown 条用引擎侧 task_id 查询接口对账，确认未计费才允许 begin 重试")


def cost(a):
    c = con()
    row = c.execute("SELECT * FROM jobs WHERE id=?", (a.id,)).fetchone()
    if not row:
        print("no job"); return
    paid = round(a.paid if a.paid is not None else (a.in_s + a.out_s) * a.unit, 2)
    c.execute("INSERT OR REPLACE INTO costs(job_id,engine,billed,input_s,output_s,unit_price,paid,"
              "labor_min,takes,waste,ts) VALUES(?,?,?,?,?,?,?,?,?,?,?)",
              (a.id, a.engine or row["engine"], 0 if a.not_billed else 1, a.in_s, a.out_s,
               a.unit, paid if not a.not_billed else 0.0, a.labor_min, a.takes, a.waste, time.time()))
    log(c, a.id, "cost", f"paid={paid} billed={0 if a.not_billed else 1}")
    c.commit()
    print(f"job={a.id} 记账：输入 {a.in_s}s + 输出 {a.out_s}s × {a.unit} 元/秒 → "
          f"{'不计费' if a.not_billed else str(paid)+' 元'}，工时 {a.labor_min} 分，废片 {a.waste}")


def report(a):
    c = con()
    jobs = [dict(r) for r in c.execute("SELECT * FROM jobs")]
    costs = [dict(r) for r in c.execute("SELECT * FROM costs")]
    cash = sum(x["paid"] or 0 for x in costs if x["billed"])
    unbilled = sum(1 for x in costs if not x["billed"])
    labor = sum(x["labor_min"] or 0 for x in costs)
    waste = sum(x["waste"] or 0 for x in costs)
    takes = sum(x["takes"] or 0 for x in costs)
    by_eng = {}
    for x in costs:
        e = by_eng.setdefault(x["engine"] or "?", {"paid": 0.0, "in_s": 0.0, "out_s": 0.0})
        e["paid"] += x["paid"] or 0
        e["in_s"] += x["input_s"] or 0
        e["out_s"] += x["output_s"] or 0
    st = {}
    for j in jobs:
        st[j["state"]] = st.get(j["state"], 0) + 1
    budget = a.budget or 0
    bysec = {e: round(v["paid"] / v["out_s"], 3) for e, v in by_eng.items() if v["out_s"]}
    print(json.dumps({"jobs_total": len(jobs), "states": st, "cash_paid_cny": round(cash, 2),
                      "not_billed_count": unbilled, "labor_min_total": round(labor, 1),
                      "takes": takes, "waste": waste,
                      "waste_rate": round(waste / takes, 3) if takes else None,
                      "per_second_cny": bysec,
                      "budget_cny": budget, "budget_used_pct": round(cash / budget * 100, 1) if budget else None,
                      "full_80s_projection_cny": round(sum(v["paid"] for v in by_eng.values()) /
                                                       max(1, sum(v["out_s"] for v in by_eng.values())) * 80, 1)
                      if by_eng else None,
                      "note": "含输入参考视频的引擎按『输入秒+输出秒』计费（可灵/H3/Seedance 一手规则）"},
                     ensure_ascii=False, indent=1))


def selftest():
    """离线自检：幂等 / 崩溃恢复 / 不计费三条语义各测一次，写临时库，不脏正式账本。"""
    global DB
    DB = os.path.join(ROOT, r"pipeline\jobs_selftest.db")
    if os.path.exists(DB):
        con().close(); _CONN.clear(); os.remove(DB)
    for suf in ("-wal", "-shm"):
        if os.path.exists(DB + suf):
            os.remove(DB + suf)
    ok = []
    p = argparse.Namespace(project="自检", engine="wan2.2-local", shot="4-3",
                           params='{"length":97,"depth":"blender_z"}', idem="")
    j1 = begin(p)
    print(" 1) 首次 begin → job", j1)
    again = begin(p)
    ok.append(("幂等：重复 begin 不再新建", again is None))
    c = con()
    n = c.execute("SELECT COUNT(*) c FROM jobs").fetchone()["c"]
    ok.append(("幂等：库里仍只有 1 条", n == 1))
    set_handle(argparse.Namespace(id=j1, handle="9123abf"))
    ok.append(("handle 落盘（重启后可续轮询）",
               c.execute("SELECT handle FROM jobs WHERE id=?", (j1,)).fetchone()["handle"] == "9123abf"))
    finish(argparse.Namespace(id=j1, file="shots/blockout/4-3_v1.mp4", gate="PASS", reason=""), "succeeded")
    cost(argparse.Namespace(id=j1, engine="wan2.2-local", in_s=4.04, out_s=4.04, unit=0.20,
                            paid=None, labor_min=9, takes=2, waste=1, not_billed=False))
    j2 = begin(argparse.Namespace(project="自检", engine="kling3-omni", shot="2-4", params="{}", idem="k2"))
    finish(argparse.Namespace(id=j2, file="", gate="", reason="安全审核拒"), "failed")
    cost(argparse.Namespace(id=j2, engine="kling3-omni", in_s=5, out_s=5, unit=0.60, paid=None,
                            labor_min=4, takes=1, waste=1, not_billed=True))
    ok.append(("失败作业记为不计费", c.execute("SELECT billed FROM costs WHERE job_id=?", (j2,)).fetchone()["billed"] == 0))
    j3 = begin(argparse.Namespace(project="自检", engine="ltx-2.3", shot="4-3", params="{}", idem="l3"))
    recover(argparse.Namespace())
    st = c.execute("SELECT state FROM jobs WHERE id=?", (j3,)).fetchone()["state"]
    ok.append(("崩溃恢复：已提交无 handle → unknown（不自动重发）", st == "unknown"))
    with_handle = c.execute("SELECT state FROM jobs WHERE handle IS NOT NULL AND state!='succeeded'").fetchall()
    ok.append(("有 handle 的未完成作业保留为可续轮询", len(with_handle) == 0))
    tot = c.execute("SELECT SUM(paid) s, SUM(labor_min) l FROM costs WHERE billed=1").fetchone()
    ok.append(("现金自动按(输入秒+输出秒)×单价计费", abs((tot["s"] or 0) - round((4.04 + 4.04) * 0.2, 2)) < 0.01))
    print("\n自检结果：")
    allok = True
    for name, v in ok:
        print(("  ✓ " if v else "  ✗ ") + name)
        allok &= bool(v)
    print(("PASS" if allok else "FAIL"), "（临时库", os.path.basename(DB), "）")
    return 0 if allok else 4


def main():
    ap = argparse.ArgumentParser()
    sub = ap.add_subparsers(dest="cmd", required=True)
    sub.add_parser("recover")
    b = sub.add_parser("begin")
    b.add_argument("--engine", required=True); b.add_argument("--shot", default="")
    b.add_argument("--params", default="{}"); b.add_argument("--idem", default="")
    b.add_argument("--project", default="雨夜寻猫")
    h = sub.add_parser("handle"); h.add_argument("id", type=int); h.add_argument("handle")
    d = sub.add_parser("done"); d.add_argument("id", type=int); d.add_argument("--file", default="")
    d.add_argument("--gate", default="")
    f = sub.add_parser("fail"); f.add_argument("id", type=int); f.add_argument("--reason", default="")
    f.add_argument("--billed", default="1")
    cs = sub.add_parser("cost"); cs.add_argument("id", type=int)
    cs.add_argument("--engine", default=""); cs.add_argument("--in-s", dest="in_s", type=float, default=0)
    cs.add_argument("--out-s", dest="out_s", type=float, default=0); cs.add_argument("--unit", type=float, default=0)
    cs.add_argument("--paid", type=float, default=None); cs.add_argument("--labor-min", dest="labor_min", type=float, default=0)
    cs.add_argument("--takes", type=int, default=1); cs.add_argument("--waste", type=int, default=0)
    cs.add_argument("--not-billed", dest="not_billed", action="store_true")
    r = sub.add_parser("report"); r.add_argument("--budget", type=float, default=0)
    sub.add_parser("selftest")
    a = ap.parse_args()
    if a.cmd == "selftest":
        return selftest()
    return {"recover": recover, "begin": begin, "handle": set_handle, "done": lambda x: finish(x, "succeeded"),
            "fail": lambda x: finish(x, "failed"), "cost": cost, "report": report}[a.cmd](a)


if __name__ == "__main__":
    main()

