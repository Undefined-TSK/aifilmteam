"""生产包冒烟测试：/react 页面加载 + 分镜节点渲染面板 + 版本树缩略图（走 FastAPI 8190）"""
import sys
from playwright.sync_api import sync_playwright

NODE_ID = sys.argv[1] if len(sys.argv) > 1 else "elem-linxy"
ASSET_NAME = sys.argv[2] if len(sys.argv) > 2 else "林小雨"

with sync_playwright() as p:
    browser = p.chromium.launch(headless=True)
    page = browser.new_page(viewport={"width": 1600, "height": 950})
    page.goto("http://127.0.0.1:8190/react/", wait_until="networkidle")
    page.wait_for_selector(".react-flow__node", timeout=10000)

    page.click(f'.react-flow__node[data-id="{NODE_ID}"]')
    page.wait_for_selector(".gen-panel", timeout=10000)
    print(f"[1] 生产版节点图 + {ASSET_NAME} 渲染面板 OK")

    page.click('.topbar-tab:has-text("版本树")')
    page.wait_for_timeout(1200)
    groups = page.locator(".vt-asset-group")
    found = False
    for i in range(groups.count()):
        name = groups.nth(i).locator(".vt-asset-name").inner_text()
        if ASSET_NAME in name:
            found = True
            thumbs = groups.nth(i).locator("img.vt-v-thumb")
            if thumbs.count() > 0:
                loaded = sum(
                    1 for j in range(thumbs.count())
                    if thumbs.nth(j).evaluate("el => el.naturalWidth") > 0
                )
                print(f"[2] {name} 缩略图 {loaded}/{thumbs.count()} 加载")
                assert loaded == thumbs.count()
            else:
                print(f"[2] {name} 暂无锁定版本（新资产）")
    assert found, f"版本树无{ASSET_NAME}"
    browser.close()

print("PASS: 生产包冒烟测试通过")
