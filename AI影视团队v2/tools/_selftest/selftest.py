#!/usr/bin/env python3
"""隔离环境下的持久化修复单测（不碰 D:\\ai_film_projects\\projects 真实存档）。

api_server.py 用 __file__ 的上上级推导 PROJECT_ROOT，所以把打过补丁的
api_server.py 放进 _selftest/tools/ 下 import，它看到的项目根就是 _selftest/，
所有读写都落在 _selftest/projects/雨夜寻猫/ 里。

覆盖：
  T1 原子写生效（无 .tmp 残留、JSON 可解析、counts 正确）
  T2 存档损坏时 corrupt=True 且保留原文件（不再与"不存在"混为一谈）
  T3 重置 = rename 备份，可从 .deleted 回滚
  T4 存档本就不存在时重置幂等
  T5 文件被占用时 rename 失败 → reset_failed / restored:False / 500，绝不 unlink
  T6 tmp 写失败时正式文件保持不变（原子性的反面验证）
"""
import asyncio
import glob
import io
import json
import os
import shutil
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, "tools"))

for d in ("web/showcase/assets", "web/workspace", "web/react-workspace"):
    os.makedirs(os.path.join(HERE, d), exist_ok=True)
PROJ = os.path.join(HERE, "projects", "雨夜寻猫")
os.makedirs(PROJ, exist_ok=True)

import api_server  # noqa: E402

GRAPH = os.path.join(PROJ, "graph.json")
PASS = []
FAIL = []


def check(name, cond, detail=""):
    (PASS if cond else FAIL).append(name)
    print(("  PASS  " if cond else "  FAIL  ") + name + (("  | " + str(detail)[:150]) if detail else ""))


def fresh(nodes=2, edges=1):
    if os.path.exists(GRAPH):
        os.remove(GRAPH)
    payload = {
        "nodes": [{"id": "n%d" % i, "type": "cineast", "position": {"x": i, "y": 0},
                   "data": {"title": "T%d" % i}} for i in range(nodes)],
        "edges": [{"id": "e1", "source": "n0", "target": "n1", "type": "default"}][:edges],
    }
    return api_server.write_graph(payload)


print("api_server PROJECT_ROOT =", api_server.PROJECT_ROOT)
check("隔离生效：项目根指向 _selftest", "_selftest" in str(api_server.PROJECT_ROOT), api_server.PROJECT_ROOT)

print("T1 原子写")
r = fresh(3, 2)
check("write_graph status=saved", r.get("status") == "saved", r)
check("graph.json 可解析", os.path.exists(GRAPH) and json.load(io.open(GRAPH, encoding="utf-8"))["nodes"].__len__() == 3)
check("无 .tmp 残留", not os.path.exists(GRAPH + ".tmp"))
rt = api_server.read_graph()
check("read_graph exists=True 且 edges=2", rt.get("exists") and len(rt["edges"]) == 2, rt.get("edges"))

print("T2 损坏可区分")
backup_bytes = open(GRAPH, "rb").read()
with io.open(GRAPH, "w", encoding="utf-8", newline="") as f:
    f.write('{"nodes": [  truncated')
rc = api_server.read_graph()
check("corrupt=True", rc.get("corrupt") is True, rc)
check("损坏时 exists=False", rc.get("exists") is False)
check("带人工确认提示", bool(rc.get("message")), rc.get("message"))
check("损坏文件未被删（可人工救回）", os.path.exists(GRAPH))
with io.open(GRAPH, "wb") as f:
    f.write(backup_bytes)

print("T3 重置=可回滚备份")
res = asyncio.run(api_server.graph_reset())
check("restored=True", res.get("restored") is True, res)
check("exists=False", res.get("exists") is False)
check("graph.json 已移走", not os.path.exists(GRAPH))
dels = glob.glob(os.path.join(PROJ, "graph_*.deleted"))
check("生成了 .deleted 备份", len(dels) == 1, dels)
if dels:
    same = json.load(io.open(dels[0], encoding="utf-8"))["nodes"].__len__() == 3
    check("备份内容可回滚（3 节点）", same)

print("T4 幂等重置")
res2 = asyncio.run(api_server.graph_reset())
check("无存档时仍 restored=True", res2.get("restored") is True, res2)

print("T5 文件被占用")
fresh(2, 1)
still = open(GRAPH, "rb")          # Windows 下持有句柄会让 rename 抛 OSError
try:
    res3 = asyncio.run(api_server.graph_reset())
    code = getattr(res3, "status_code", None)
    body = json.loads(res3.body.decode("utf-8")) if hasattr(res3, "body") else res3
    check("返回 500", code == 500, code)
    check("restored=False（不再谎报成功）", body.get("restored") is False, body)
    check("exists=True（如实告知还在）", body.get("exists") is True)
    check("没有把存档删掉（unlink 未被调用）", os.path.exists(GRAPH))
finally:
    still.close()

print("T6 tmp 写失败不动正式文件")
fresh(2, 1)
before = open(GRAPH, "rb").read()
tmp = GRAPH + ".tmp"
os.makedirs(tmp, exist_ok=True)     # 让 tmp.write_text 必然失败
try:
    api_server.write_graph({"nodes": [{"id": "x", "data": {}}], "edges": []})
    check("write_graph 抛出异常（向上冒泡给路由）", False, "没有抛出")
except Exception as e:
    check("write_graph 抛出异常（向上冒泡给路由）", True, type(e).__name__)
check("正式存档保持原样", open(GRAPH, "rb").read() == before)
shutil.rmtree(tmp, ignore_errors=True)

for f in glob.glob(os.path.join(PROJ, "graph*")):
    try:
        os.remove(f)
    except OSError:
        pass
print("\nRESULT pass=%d fail=%d" % (len(PASS), len(FAIL)))
if FAIL:
    print("FAILED:", FAIL)
sys.exit(1 if FAIL else 0)
