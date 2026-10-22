#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
K13 版本树 - Python API 调用示例

展示如何在Python代码中使用K13版本管理功能。
"""

import sys
import os
import tempfile
from pathlib import Path

# 把scripts目录加入路径
sys.path.insert(0, str(Path(__file__).parent.parent / "scripts"))

from k13 import (
    init_k13,
    save_version,
    list_versions,
    get_version,
    compare_versions,
    create_branch,
    delete_version
)


def main():
    # 创建一个临时项目用于演示
    with tempfile.TemporaryDirectory() as tmpdir:
        project_path = tmpdir
        print(f"=== 演示项目: {project_path} ===")
        print()
        
        # ==========================================
        #  1. 初始化 K13
        # ==========================================
        print("--- 1. 初始化 K13 ---")
        result = init_k13(project_path)
        print(f"  状态: {result['status']}")
        print(f"  消息: {result['message']}")
        print()
        
        # 创建一个假的生成文件（模拟AI生成的图片）
        test_file = Path(tmpdir) / "generated_v1.png"
        test_file.write_bytes(b"fake image data v1")
        
        # ==========================================
        #  2. 保存第一个版本
        # ==========================================
        print("--- 2. 保存第一个版本 ---")
        result = save_version(
            project_path=project_path,
            asset_type="character",
            asset_name="林月",
            file_path=str(test_file),
            params={
                "model": "SDXL",
                "prompt": "cyberpunk girl, short hair, neon jacket",
                "negative_prompt": "ugly, blurry",
                "seed": 12345,
                "steps": 20,
                "width": 1024,
                "height": 1024
            },
            note="初版，赛博朋克女主角"
        )
        print(f"  状态: {result['status']}")
        print(f"  版本: {result['version']} ({result['uuid']})")
        v1_uuid = result['uuid']
        print()
        
        # ==========================================
        #  3. 保存第二个版本（在v1基础上修改）
        # ==========================================
        print("--- 3. 保存第二个版本（从v1分支）---")
        
        test_file_v2 = Path(tmpdir) / "generated_v2.png"
        test_file_v2.write_bytes(b"fake image data v2 - long hair")
        
        result = save_version(
            project_path=project_path,
            asset_type="character",
            asset_name="林月",
            file_path=str(test_file_v2),
            params={
                "model": "SDXL",
                "prompt": "cyberpunk girl, LONG hair, neon jacket",
                "negative_prompt": "ugly, blurry, short hair",
                "seed": 12345,
                "steps": 25,
                "width": 1024,
                "height": 1024
            },
            note="试试长发版",
            parent_uuid=v1_uuid
        )
        print(f"  状态: {result['status']}")
        print(f"  版本: {result['version']} ({result['uuid']})")
        v2_uuid = result['uuid']
        print()
        
        # ==========================================
        #  4. 保存第三个版本（另一个方向）
        # ==========================================
        print("--- 4. 保存第三个版本（从v1分支，另一个方向）---")
        
        test_file_v3 = Path(tmpdir) / "generated_v3.png"
        test_file_v3.write_bytes(b"fake image data v3 - blue neon")
        
        result = save_version(
            project_path=project_path,
            asset_type="character",
            asset_name="林月",
            file_path=str(test_file_v3),
            params={
                "model": "SDXL",
                "prompt": "cyberpunk girl, short hair, BLUE neon jacket",
                "negative_prompt": "ugly, blurry",
                "seed": 67890,
                "steps": 20,
                "width": 1024,
                "height": 1024
            },
            note="换个seed，蓝色霓虹夹克",
            parent_uuid=v1_uuid
        )
        print(f"  状态: {result['status']}")
        print(f"  版本: {result['version']} ({result['uuid']})")
        v3_uuid = result['uuid']
        print()
        
        # ==========================================
        #  5. 列出所有版本（树状）
        # ==========================================
        print("--- 5. 版本树 ---")
        result = list_versions(project_path, "character", "林月")
        print(f"  总版本数: {result['count']}")
        print(f"  已锁定: {result['locked_count']}")
        print(f"  最新版本UUID: {result['latest_uuid']}")
        print()
        print("  版本树结构:")
        for v in result['versions']:
            indent = "  " * v['depth']
            locked_icon = "🔒" if v.get('locked') else "🔓"
            print(f"  {indent}{locked_icon} {v['version']} ({v['uuid']}) - {v.get('note', '无备注')}")
        print()
        
        # ==========================================
        #  6. 查看单个版本详情
        # ==========================================
        print("--- 6. 查看 v1 详情 ---")
        result = get_version(project_path, "character", "林月", v1_uuid)
        v = result['version']
        print(f"  版本: {v['version']}")
        print(f"  UUID: {v['uuid']}")
        print(f"  创建时间: {v['created_at']}")
        print(f"  文件: {v['file']}")
        print(f"  参数数量: {len(v['params'])} 个")
        print(f"  备注: {v.get('note', '')}")
        print()
        
        # ==========================================
        #  7. 对比两个版本
        # ==========================================
        print("--- 7. 对比 v1 和 v2 ---")
        result = compare_versions(project_path, "character", "林月", v1_uuid, v2_uuid)
        print(f"  相同参数: {result['same_count']} 个")
        print(f"  不同参数: {result['different_count']} 个")
        print()
        print("  不同的参数:")
        for key, vals in result['different'].items():
            print(f"    {key}:")
            print(f"      v1: {vals['v1']}")
            print(f"      v2: {vals['v2']}")
        print()
        
        if result['only_in_a']:
            print("  只在v1有的参数:", list(result['only_in_a'].keys()))
        if result['only_in_b']:
            print("  只在v2有的参数:", list(result['only_in_b'].keys()))
        
        print()
        print("=== 演示完成 ===")


if __name__ == "__main__":
    main()
