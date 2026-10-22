#!/usr/bin/env python3
"""二次验证：等画布渲染稳定后再断言，排除计数时序导致的误判。
验证闭环：清场→初始节点(N)→双击+1(N+1)→防抖保存 graph.json→刷新→恢复(N+1)
额外：直接读取磁盘 graph.json 的节点数，与刷新后画布节点数交叉校验。
"""
import json
import os
from playwright.sync_api import sync_playwright

GRAPH_JSON = r"D:\ai_film_projects\projects\雨夜寻猫\graph.json"
URL = "http://127.0.0.1:8190/react/"
SHOT = r"D:\ai_film_projects\tests\graph_persistence_stable.png"


def count_nodes(page):
    return page.locator(".react-flow__node").count()


def wait_stable(page, expect=None, timeout=8000):
    """轮询直到节点数稳定（连续两次相同），或达到 expect，或超时"""
    last = -1
    import time
    t0 = time.time()
    while time.time() - t0 < timeout / 1000:
        cur = count_nodes(page)
        if cur == last and cur > 0:
            return cur
        if expect is not None and cur == expect:
            # 再等一拍确认稳定
            page.wait_for_timeout(500)
            if count_nodes(page) == expect:
                return expect
        last = cur
        page.wait_for_timeout(300)
    return count_nodes(page)


def add_node_via_dblclick(page):
    base = count_nodes(page)
    for x, y in [(1100, 480), (1250, 300), (900, 600), (1400, 700), (800, 700)]:
        page.mouse.dblclick(x, y)
        page.wait_for_timeout(500)
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
    page.wait_for_timeout(3000)

    # 清场
    if os.path.exists(GRAPH_JSON):
        os.remove(GRAPH_JSON)
        page.reload()
        page.wait_for_load_state("networkidle")
        page.wait_for_timeout(3000)

    before = wait_stable(page)
    print(f"[1] 初始节点数(稳定): {before}")

    added = add_node_via_dblclick(page)
    after_stable = wait_stable(page, expect=before + 1 if added else None)
    # 给防抖保存留足时间
    page.wait_for_timeout(2500)
    print(f"[2] 双击添加: {'成功' if added else '失败'} → 节点数(稳定): {after_stable}")

    saved = os.path.exists(GRAPH_JSON)
    disk_n = None
    if saved:
        data = json.load(open(GRAPH_JSON, encoding="utf-8"))
        disk_n = len(data["nodes"])
        print(f"[3] graph.json 自动保存: 是（磁盘 {disk_n} 节点 / {len(data['edges'])} 连线 @ {data['saved_at']}）")
    else:
        print(f"[3] graph.json 自动保存: 否")

    page.reload()
    page.wait_for_load_state("networkidle")
    page.wait_for_timeout(3000)
    reloaded = wait_stable(page)
    print(f"[4] 刷新后节点数(稳定): {reloaded}")

    page.screenshot(path=SHOT, full_page=False)
    if errors:
        print(f"[5] 控制台错误: {errors[:3]}")
    browser.close()

    # 断言：双击生效、已保存、刷新恢复、磁盘与画布一致
    ok = added and saved and (reloaded == after_stable) and (disk_n == reloaded if disk_n else True)
    print(f"\nRESULT: {'PASS ✅' if ok else 'FAIL ❌'}")
