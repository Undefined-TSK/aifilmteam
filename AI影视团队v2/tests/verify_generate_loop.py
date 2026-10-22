#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""MVP 生成闭环端到端验证：选中节点 → ComfyUI 渲染 → 预览 → K13 锁定 → 版本树

前置条件：ComfyUI(8188) 与 api_server(8190) 已运行，vite dev server 由 with_server.py 托管
运行：python "C:\\Users\\LZH\\.trae-cn\\skills\\webapp-testing\\scripts\\with_server.py" ^
        --server "cd /d D:\\ai_film_projects\\web\\react-workspace && npm run dev" --port 5173 ^
        -- python tests/verify_generate_loop.py
"""
import json
import sys
import urllib.request
from playwright.sync_api import sync_playwright

API = "http://127.0.0.1:8190"
APP = "http://localhost:5173/react/"
# 用法: python verify_generate_loop.py [节点ID] [资产名]
NODE_ID = sys.argv[1] if len(sys.argv) > 1 else "elem-linxy"
ASSET_NAME = sys.argv[2] if len(sys.argv) > 2 else "林小雨"


def api(path):
    return json.load(urllib.request.urlopen(API + path, timeout=10))


def main():
    budget_before = api("/api/budget/status")["remaining"]
    versions_before = len(api("/api/versions").get("versions", []))
    print(f"[前] 预算剩余 {budget_before} | K13 版本数 {versions_before}")

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page(viewport={"width": 1600, "height": 950})
        page.goto(APP, wait_until="networkidle")

        # 1. 选中生成节点，右侧出现 AI 渲染面板
        page.click(f'.react-flow__node[data-id="{NODE_ID}"]')
        page.wait_for_selector(".gen-panel", timeout=10000)
        prompt_val = page.input_value(".gen-prompt")
        assert prompt_val.strip(), "节点提示词为空，生成表单未初始化"
        stale_ver = ""
        if page.query_selector(".gen-preview-meta"):
            stale_ver = page.inner_text(".gen-preview-meta").split()[1]
        print(f"[1] 节点已选中，提示词 {len(prompt_val)} 字符"
              f"（旧预览版本 {stale_ver or '无'}）")

        # 2. 提交渲染
        page.click(".gen-panel button.gen-btn:not(.gen-lock-btn)")
        page.wait_for_selector("text=渲染中", timeout=10000)
        print("[2] 渲染已提交，等待 ComfyUI（SDXL 1024px）...")

        # 3. 等待渲染按钮恢复可用 = 生成完成（SDXL 需 30-120s）
        page.wait_for_selector(
            ".gen-panel button.gen-btn:not(.gen-lock-btn):not([disabled])",
            timeout=200000,
        )
        page.wait_for_timeout(500)
        page.screenshot(path="tests/e2e_preview.png")
        meta = page.inner_text(".gen-preview-meta")
        new_ver = meta.split()[1]
        assert new_ver != stale_ver, f"预览仍是旧版本 {stale_ver}，生成结果未写入"
        print(f"[3] 预览完成：{meta.strip().replace(chr(10), ' ')}")

        # 4. 锁定当前版本进 K13
        page.click(".gen-lock-btn")
        page.wait_for_selector("text=已冻结进 K13 版本树", timeout=15000)
        print("[4] K13 锁定成功")

        # 5. 切到版本树视图验证新版本
        page.click('.topbar-tab:has-text("版本树")')
        page.wait_for_timeout(1200)
        page.screenshot(path=f"tests/e2e_version_tree_{ASSET_NAME[:6]}.png")
        assert page.locator(f'.vt-asset-name:has-text("{ASSET_NAME}")').count() > 0, \
            f"版本树中未找到{ASSET_NAME}资产组"
        print(f"[5] 版本树已显示{ASSET_NAME}")

        browser.close()

    budget_after = api("/api/budget/status")["remaining"]
    versions_after = len(api("/api/versions").get("versions", []))
    print(
        f"[后] 预算剩余 {budget_after}（本次扣 {budget_before - budget_after}）"
        f" | K13 版本数 {versions_before} -> {versions_after}"
    )
    assert versions_after == versions_before + 1, "K13 版本数未增加，锁定未落盘"
    print()
    print("PASS: MVP 闭环（渲染->预览->锁定->版本树）全部通过")


if __name__ == "__main__":
    main()
