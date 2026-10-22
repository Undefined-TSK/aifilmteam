#!/usr/bin/env python3
"""
K13 版本树管理工具
锁定版本 = 冻结，不可修改，只能新建分支

用法：
  python k13.py list <project_path>                    # 列出所有锁定版本
  python k13.py lock <project_path> <asset_type> <asset_name> <file_path> <params_json>  # 锁定一个版本
  python k13.py get <project_path> <version_uuid>      # 获取版本详情
  python k13.py history <project_path> <asset_name>    # 查看某资产的版本历史
  python k13.py branch <project_path> <version_uuid> <branch_name>  # 从某版本新建分支
"""

import sys
import os
import json
import uuid
import shutil
from datetime import datetime
from pathlib import Path

K13_DIR = "k13_locked"
INDEX_FILE = "versions.json"


def get_k13_dir(project_path):
    return Path(project_path) / K13_DIR


def get_index_path(project_path):
    return get_k13_dir(project_path) / INDEX_FILE


def load_index(project_path):
    """加载版本索引"""
    index_path = get_index_path(project_path)
    if not index_path.exists():
        return {"versions": [], "assets": {}}
    with open(index_path, "r", encoding="utf-8") as f:
        return json.load(f)


def save_index(project_path, index):
    """保存版本索引"""
    index_path = get_index_path(project_path)
    index_path.parent.mkdir(parents=True, exist_ok=True)
    with open(index_path, "w", encoding="utf-8") as f:
        json.dump(index, f, ensure_ascii=False, indent=2)


def list_versions(project_path):
    """列出所有锁定版本"""
    index = load_index(project_path)
    versions = index.get("versions", [])
    
    result = {
        "total": len(versions),
        "versions": [
            {
                "uuid": v["uuid"],
                "asset_type": v["asset_type"],
                "asset_name": v["asset_name"],
                "locked_at": v["locked_at"],
                "branch": v.get("branch", "main"),
                "parent": v.get("parent_uuid", "root"),
                # file_path/params 供前端版本树渲染缩略图与种子等元信息
                "file_path": v.get("file_path"),
                "params": v.get("params", {}),
            }
            for v in versions
        ]
    }
    print(json.dumps(result, ensure_ascii=False, indent=2))


def lock_version(project_path, asset_type, asset_name, file_path, params_json):
    """
    锁定一个版本
    - 复制文件到 k13_locked 目录
    - 生成 UUID
    - 记录参数快照
    """
    k13_dir = get_k13_dir(project_path)
    k13_dir.mkdir(parents=True, exist_ok=True)
    
    src_file = Path(file_path)
    if not src_file.exists():
        print(json.dumps({"status": "error", "message": f"文件不存在: {file_path}"}, ensure_ascii=False))
        return
    
    # 生成版本 UUID
    version_uuid = str(uuid.uuid4())[:8]  # 短UUID，够用了
    
    # 解析参数
    try:
        params = json.loads(params_json) if params_json else {}
    except json.JSONDecodeError:
        params = {"raw_params": params_json}
    
    # 目标目录：按资产类型/资产名/版本号组织
    dest_dir = k13_dir / asset_type / asset_name / version_uuid
    dest_dir.mkdir(parents=True, exist_ok=True)
    
    # 复制文件
    dest_file = dest_dir / src_file.name
    shutil.copy2(src_file, dest_file)
    
    # 记录版本信息
    version_info = {
        "uuid": version_uuid,
        "asset_type": asset_type,
        "asset_name": asset_name,
        "file_name": src_file.name,
        "file_path": str(dest_file),
        "locked_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "params": params,
        "branch": "main",
        "parent_uuid": None,
        "locked": True
    }
    
    # 更新索引
    index = load_index(project_path)
    index["versions"].append(version_info)
    
    # 更新资产索引
    asset_key = f"{asset_type}/{asset_name}"
    if asset_key not in index["assets"]:
        index["assets"][asset_key] = {
            "asset_type": asset_type,
            "asset_name": asset_name,
            "version_count": 0,
            "latest_version": None,
            "versions": []
        }
    
    index["assets"][asset_key]["version_count"] += 1
    index["assets"][asset_key]["latest_version"] = version_uuid
    index["assets"][asset_key]["versions"].append(version_uuid)
    
    save_index(project_path, index)
    
    print(json.dumps({
        "status": "locked",
        "uuid": version_uuid,
        "asset_type": asset_type,
        "asset_name": asset_name,
        "file": str(dest_file),
        "locked_at": version_info["locked_at"]
    }, ensure_ascii=False, indent=2))


def get_version(project_path, version_uuid):
    """获取版本详情"""
    index = load_index(project_path)
    
    for v in index["versions"]:
        if v["uuid"] == version_uuid:
            print(json.dumps(v, ensure_ascii=False, indent=2))
            return
    
    print(json.dumps({"status": "error", "message": f"版本不存在: {version_uuid}"}, ensure_ascii=False))


def asset_history(project_path, asset_name):
    """查看某资产的版本历史"""
    index = load_index(project_path)
    
    versions = [
        v for v in index["versions"]
        if v["asset_name"] == asset_name
    ]
    versions.sort(key=lambda x: x["locked_at"], reverse=True)
    
    print(json.dumps({
        "asset_name": asset_name,
        "version_count": len(versions),
        "versions": versions
    }, ensure_ascii=False, indent=2))


def create_branch(project_path, parent_uuid, branch_name):
    """从某个版本创建分支"""
    index = load_index(project_path)
    
    # 找到父版本
    parent = None
    for v in index["versions"]:
        if v["uuid"] == parent_uuid:
            parent = v
            break
    
    if not parent:
        print(json.dumps({"status": "error", "message": f"父版本不存在: {parent_uuid}"}, ensure_ascii=False))
        return
    
    # 新版本信息（继承父版本的文件和参数）
    new_uuid = str(uuid.uuid4())[:8]
    new_version = {
        "uuid": new_uuid,
        "asset_type": parent["asset_type"],
        "asset_name": f"{parent['asset_name']}_{branch_name}",
        "file_name": parent["file_name"],
        "file_path": parent["file_path"],
        "locked_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "params": parent.get("params", {}),
        "branch": branch_name,
        "parent_uuid": parent_uuid,
        "locked": False,  # 分支版本默认未锁定，需要用户确认后再锁
        "note": f"从版本 {parent_uuid} 分出的 {branch_name} 分支"
    }
    
    index["versions"].append(new_version)
    save_index(project_path, index)
    
    print(json.dumps({
        "status": "branched",
        "new_uuid": new_uuid,
        "parent_uuid": parent_uuid,
        "branch": branch_name
    }, ensure_ascii=False, indent=2))


def main():
    if len(sys.argv) < 3:
        print(__doc__)
        sys.exit(1)
    
    command = sys.argv[1]
    project_path = sys.argv[2]
    
    if command == "list":
        list_versions(project_path)
    elif command == "lock":
        if len(sys.argv) < 7:
            print("用法: lock <project_path> <asset_type> <asset_name> <file_path> <params_json>")
            sys.exit(1)
        lock_version(project_path, sys.argv[3], sys.argv[4], sys.argv[5], sys.argv[6])
    elif command == "get":
        if len(sys.argv) < 4:
            print("用法: get <project_path> <version_uuid>")
            sys.exit(1)
        get_version(project_path, sys.argv[3])
    elif command == "history":
        if len(sys.argv) < 4:
            print("用法: history <project_path> <asset_name>")
            sys.exit(1)
        asset_history(project_path, sys.argv[3])
    elif command == "branch":
        if len(sys.argv) < 5:
            print("用法: branch <project_path> <version_uuid> <branch_name>")
            sys.exit(1)
        create_branch(project_path, sys.argv[3], sys.argv[4])
    else:
        print(f"未知命令: {command}")
        print(__doc__)
        sys.exit(1)


if __name__ == "__main__":
    main()
