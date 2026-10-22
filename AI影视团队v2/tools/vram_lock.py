# -*- coding: utf-8 -*-
"""vram_lock.py — 显存独占锁（P-0d）

背景（审计件 E9/D4）：Hermes 插件 `vram_scheduler.py` 已装，但 `tools/*.py` 内 **0 处引用**，
且其超时 1800s 恰等于 Wan2.2 poll 上限 → 对长任务是"误抢风险"，不是"自动管理"。

本模块提供**脚本侧强制**的显存独占：
  - 独占创建锁文件（O_CREAT|O_EXCL，原子）
  - 心跳续租（默认每 60s）
  - TTL（默认 1800s，超时视为过期锁，可被抢占）
  - 上下文管理器，异常/中断自动释放

⚠️ 实现约束（2026-09-27 实测得出）：**不使用 os.remove** —— 本机沙箱会拦截删除操作
（`safe-delete: windows-sandbox-recycle-bin-unavailable`），会让锁永远释放不掉。
因此全部释放/接管动作改用 **os.replace 原子替换内容**（"released" 标记），锁文件长期存在属正常现象。

用法：
  from vram_lock import vram_lock
  with vram_lock("wan22"):
      ...  # 独占跑生成模型

  python tools/vram_lock.py status
  python tools/vram_lock.py acquire <owner> [wait_sec]
  python tools/vram_lock.py release [owner]
"""
import contextlib
import json
import os
import threading
import time

# v2 根 = tools/ 的上一级（相对定位，不硬编码盘符路径，防重组再断链；R0-T6 修复）
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
LOCK = os.path.join(ROOT, "logs", "vram.lock")
DEFAULT_TTL = 1800      # 秒；超时视为过期锁
HEARTBEAT_SEC = 60      # 秒；心跳续租间隔
POLL_SEC = 5


class VramLockError(RuntimeError):
    pass


def _read():
    try:
        with open(LOCK, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception:
        return None


def _write_atomic(payload):
    """原子写：写临时文件后 os.replace 覆盖（**不删除**锁文件）。"""
    tmp = LOCK + ".tmp"
    with open(tmp, "w", encoding="utf-8") as f:
        json.dump(payload, f)
    os.replace(tmp, LOCK)          # Windows 上对已存在文件为原子替换


def _free(meta, ttl):
    """锁是否可被接管：无内容 / 已标记 released / 心跳超时。"""
    if meta is None:
        return False               # 文件在但读不出 → 保守视为被占用
    if meta.get("released"):
        return True
    return (time.time() - float(meta.get("heartbeat_at", 0))) > ttl


def _new_meta(owner, extra=None):
    now = time.time()
    m = {"owner": owner, "pid": os.getpid(),
         "acquired_at": now, "heartbeat_at": now}
    if extra:
        m.update(extra)
    return m


def acquire(owner, ttl=DEFAULT_TTL, wait_sec=0, poll=POLL_SEC):
    """独占获取。wait_sec=0 表示不等待（拿不到立刻抛错）。"""
    deadline = time.time() + max(0, wait_sec)
    while True:
        try:
            fd = os.open(LOCK, os.O_CREAT | os.O_EXCL | os.O_WRONLY)
            with os.fdopen(fd, "w", encoding="utf-8") as f:
                json.dump(_new_meta(owner), f)
            return True
        except FileExistsError:
            meta = _read()
            if _free(meta, ttl):
                try:
                    if meta and meta.get("released"):
                        # 正常释放后的重获（P2-1 语义修正）：非接管，显式标记
                        _write_atomic(_new_meta(owner, {
                            "acquired_normally": True,
                            "previous_owner": (meta or {}).get("owner")}))
                    else:
                        # 仅 TTL 过期强抢才记 took_over_from（真实接管语义）
                        _write_atomic(_new_meta(owner, {
                            "took_over_from": (meta or {}).get("owner")}))
                    return True
                except OSError:
                    pass
            if time.time() >= deadline:
                m = meta or {}
                age = time.time() - float(m.get("heartbeat_at", time.time()))
                raise VramLockError(
                    "显存锁被占用：owner=%s pid=%s 上次心跳 %.0fs 前（TTL=%ds）"
                    % (m.get("owner"), m.get("pid"), age, ttl))
            time.sleep(poll)


def release(owner=None):
    """释放：写 released 标记并原子替换（不删文件）。"""
    meta = _read()
    if owner and meta and meta.get("owner") not in (owner, None):
        return False
    m = dict(meta or {})
    m.setdefault("owner", owner)
    m["released"] = True
    m["released_at"] = time.time()
    try:
        _write_atomic(m)
        return True
    except OSError:
        return False


@contextlib.contextmanager
def vram_lock(owner, ttl=DEFAULT_TTL, wait_sec=0):
    acquire(owner, ttl, wait_sec)
    stop = threading.Event()

    def _beat():
        while not stop.wait(HEARTBEAT_SEC):
            meta = _read()
            if meta and meta.get("owner") == owner and not meta.get("released"):
                meta["heartbeat_at"] = time.time()
                try:
                    _write_atomic(meta)
                except OSError:
                    pass

    th = threading.Thread(target=_beat, name="vram-lock-heartbeat", daemon=True)
    th.start()
    try:
        yield
    finally:
        stop.set()
        release(owner)


def status():
    return {"lock_path": LOCK, "ttl_sec": DEFAULT_TTL,
            "heartbeat_sec": HEARTBEAT_SEC, "holder": _read()}


if __name__ == "__main__":
    import sys
    cmd = sys.argv[1] if len(sys.argv) > 1 else "status"
    if cmd == "status":
        print(json.dumps(status(), ensure_ascii=False, indent=1))
    elif cmd == "acquire":
        own = sys.argv[2] if len(sys.argv) > 2 else "manual"
        wait = int(sys.argv[3]) if len(sys.argv) > 3 else 0
        print(acquire(own, wait_sec=wait))
    elif cmd == "release":
        own = sys.argv[2] if len(sys.argv) > 2 else None
        print(release(own))
    else:
        print("usage: vram_lock.py [status|acquire <owner> [wait]|release [owner]]")
