#!/usr/bin/env python3
"""只读视觉取证：确认节点图连线真的是贝塞尔曲线。

判定不靠肉眼：贝塞尔边的 path d 里含三次命令 "C"，smoothstep 是 "L"/"A"。
本脚本只截图 + 读 DOM，绝不删除或改写 graph.json。
"""
import json
import re
import sys
from pathlib import Path
from playwright.sync_api import sync_playwright

ROOT = Path(r"D:\ai_film_projects")
URL = "http://127.0.0.1:8190/react/"
SHOT = ROOT / "tests" / "evidence" / "edge_curve_verify.png"
GRAPH = ROOT / "projects" / "雨夜寻猫" / "graph.json"

graph_before = GRAPH.read_bytes() if GRAPH.exists() else None

console_errors = []
with sync_playwright() as p:
    browser = p.chromium.launch(headless=True)
    page = browser.new_page(viewport={"width": 1680, "height": 950})
    page.on("console", lambda m: console_errors.append(m.text) if m.type == "error" else None)
    page.on("pageerror", lambda e: console_errors.append("pageerror: " + str(e)))
    page.goto(URL, wait_until="networkidle")
    page.wait_for_selector(".react-flow__edge", timeout=15000)
    page.wait_for_timeout(1500)

    paths = page.eval_on_selector_all(
        ".react-flow__edge-path", "els => els.map(e => e.getAttribute('d'))"
    )
    nodes = page.locator(".react-flow__node").count()
    SHOT.parent.mkdir(parents=True, exist_ok=True)
    page.screenshot(path=str(SHOT))
    browser.close()

stat = {"cubic_C": 0, "polyline_L": 0, "arc_A": 0, "empty": 0}
samples = []
for d in paths:
    if not d:
        stat["empty"] += 1
        continue
    if re.search(r"[CR]", d):
        stat["cubic_C"] += 1
    if " L " in d or d.count("L") > 0:
        stat["polyline_L"] += 1
    if "A" in d:
        stat["arc_A"] += 1
    if len(samples) < 2:
        samples.append(d[:150])

graph_after = GRAPH.read_bytes() if GRAPH.exists() else None

print(json.dumps({
    "nodes_rendered": nodes,
    "edges_rendered": len(paths),
    "path_stats": stat,
    "path_samples": samples,
    "screenshot": str(SHOT),
    "console_errors": console_errors[:6],
    "graph_file_untouched": graph_before == graph_after,
}, ensure_ascii=False, indent=2))

ok = stat["cubic_C"] == len(paths) and len(paths) > 0 and not console_errors
print("VERDICT=" + ("BEZIER_OK" if ok else "CHECK_MANUALLY"))
sys.exit(0 if ok else 3)
