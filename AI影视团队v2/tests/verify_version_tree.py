"""版本树视图验证：缩略图加载 + 林小雨资产组可见 + 种子元信息"""
from playwright.sync_api import sync_playwright

with sync_playwright() as p:
    browser = p.chromium.launch(headless=True)
    page = browser.new_page(viewport={"width": 1600, "height": 950})
    page.goto("http://localhost:5173/react/", wait_until="networkidle")

    page.click('.topbar-tab:has-text("版本树")')
    page.wait_for_timeout(1500)

    # 滚到列表底部找林小雨资产组
    groups = page.locator(".vt-asset-group")
    n = groups.count()
    print(f"资产组数: {n}")
    target = None
    for i in range(n):
        name = groups.nth(i).locator(".vt-asset-name").inner_text()
        print(f"  [{i}] {name}")
        if "林小雨" in name:
            target = groups.nth(i)
    assert target, "未找到林小雨资产组"
    target.scroll_into_view_if_needed()
    page.wait_for_timeout(800)

    # 检查林小雨组内缩略图是否真实加载（naturalWidth>0）
    thumbs = target.locator("img.vt-v-thumb")
    loaded = 0
    for i in range(thumbs.count()):
        w = thumbs.nth(i).evaluate("el => el.naturalWidth")
        if w > 0:
            loaded += 1
    print(f"林小雨缩略图: {loaded}/{thumbs.count()} 张已加载")
    assert loaded == thumbs.count() and loaded > 0, "缩略图未全部加载"

    # 检查最新版本的种子元信息（不再是 —）
    metas = target.locator(".vt-v-meta")
    last_meta = metas.nth(metas.count() - 1).inner_text()
    print(f"最新版本元信息: {last_meta}")
    assert "seed:—" not in last_meta, "种子仍为占位符 —"

    page.screenshot(path="tests/e2e_version_tree_fixed.png")
    browser.close()

print("PASS: 版本树缩略图与元信息验证通过")
