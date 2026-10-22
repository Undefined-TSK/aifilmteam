#!/usr/bin/env python3
"""端到端验证：节点图画布持久化闭环
改画布（双击添加节点）→ 防抖自动保存 graph.json → 刷新页面 → 节点恢复
"""
import json
import os
from playwright.sync_api import sync_playwright

GRAPH_JSON = r"D:\ai_film_projects\projects\雨夜寻猫\graph.json"
URL = "http://127.0.0.1:8190/react/"
SHOT = r"D:\ai_film_projects\tests\graph_persistence_verify.png"


def count_nodes(page):
    return page.locator(".react-flow__node").count()


def add_node_via_dblclick(page):
    """在多个空白位置尝试双击，直到节点数+1"""
    base = count_nodes(page)
    for x, y in [(1100, 480), (1250, 300), (900, 600), (1400, 700), (800, 700)]:
        page.mouse.dblclick(x, y)
        page.wait_for_timeout(400)
        if count_nodes(page) > base:
            return True
    return False


with sync_playwright() as p:
    browser = p.chromium.launch(headless=True)
    page = browser.new_page(viewport={"width": 1600, "height": 900})
    errors = []
    page.on("console", lambda m: errors.append(m.text) if m.type == "error" else None)

    page.goto(URL)
    page.wait_for_load_state("networkidle")
    page.wait_for_timeout(2000)

    # 清场：确保从初始 mock 状态开始
    if os.path.exists(GRAPH_JSON):
        os.remove(GRAPH_JSON)

    before = count_nodes(page)
    print(f"[1] 初始节点数: {before}")

    added = add_node_via_dblclick(page)
    after = count_nodes(page)
    print(f"[2] 双击添加: {'成功' if added else '失败'} → 节点数: {after}")

    # 等待防抖(800ms) + POST 保存
    page.wait_for_timeout(2500)
    saved = os.path.exists(GRAPH_JSON)
    print(f"[3] graph.json 自动保存: {'是' if saved else '否'}")
    if saved:
        data = json.load(open(GRAPH_JSON, encoding="utf-8"))
        print(f"    保存内容: {len(data['nodes'])} 节点 / {len(data['edges'])} 连线 @ {data['saved_at']}")
        status_text = page.locator(".bottombar-status").inner_text()
        print(f"    底栏状态: {status_text}")

    # 刷新页面验证恢复
    page.reload()
    page.wait_for_load_state("networkidle")
    page.wait_for_timeout(2000)
    reloaded = count_nodes(page)
    print(f"[4] 刷新后节点数: {reloaded}")

    page.screenshot(path=SHOT, full_page=False)
    if errors:
        print(f"[5] 控制台错误: {errors[:3]}")
    browser.close()

    ok = added and saved and (reloaded == after)
    print(f"\nRESULT: {'PASS ✅' if ok else 'FAIL ❌'}")
