#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
K13 版本树 - AI生成版本管理工具
从 AI影视制片人Agent 工作流中提炼的独立Skill

核心思想：AI生成像抽卡，满意的结果要"锁定"，锁定即冻结，永不被覆盖。
"""

import json
import uuid
import shutil
import sys
import os
from pathlib import Path
from datetime import datetime


# ============================================================
#  路径工具
# ============================================================

def get_k13_dir(project_path):
    """获取K13锁定目录路径"""
    return Path(project_path) / "k13_locked"


def get_versions_dir(project_path, asset_type, asset_name):
    """获取某个资产的版本目录"""
    return get_k13_dir(project_path) / asset_type / asset_name


def get_tree_path(project_path, asset_type, asset_name):
    """获取版本树JSON路径"""
    return get_versions_dir(project_path, asset_type, asset_name) / "versions.json"


def short_uuid():
    """生成8位短UUID（版本标识符）"""
    return uuid.uuid4().hex[:8]


# ============================================================
#  初始化
# ============================================================

def init_k13(project_path):
    """
    在项目中初始化K13版本管理
    创建 k13_locked/ 目录结构
    """
    k13_dir = get_k13_dir(project_path)
    
    if k13_dir.exists():
        return {"status": "ok", "message": "K13已初始化", "path": str(k13_dir)}
    
    k13_dir.mkdir(parents=True, exist_ok=True)
    
    # 创建说明文件
    readme = k13_dir / "README.md"
    readme.write_text("""# K13 版本树

这里存放所有已锁定的资产版本。

## 目录结构
```
k13_locked/
├── character/          # 角色资产
│   └── 林月/
│       ├── versions.json   # 版本树数据
│       └── <uuid>/         # 每个锁定版本一个目录
│           ├── result.png  # 结果文件
│           └── params.json # 参数快照
├── scene/              # 场景资产
├── storyboard/         # 分镜资产
└── animation/          # 动画资产
```

## 说明
- 锁定后的版本永不修改
- 每个版本有独立UUID
- 参数快照可用于复现
""", encoding="utf-8")
    
    return {"status": "ok", "message": "K13初始化完成", "path": str(k13_dir)}


# ============================================================
#  版本树读写
# ============================================================

def load_tree(project_path, asset_type, asset_name):
    """加载版本树数据"""
    tree_path = get_tree_path(project_path, asset_type, asset_name)
    
    if not tree_path.exists():
        return {
            "asset_type": asset_type,
            "asset_name": asset_name,
            "created_at": datetime.now().isoformat(),
            "versions": [],
            "latest_uuid": None
        }
    
    with open(tree_path, 'r', encoding='utf-8') as f:
        return json.load(f)


def save_tree(project_path, asset_type, asset_name, tree):
    """保存版本树数据"""
    tree_path = get_tree_path(project_path, asset_type, asset_name)
    tree_path.parent.mkdir(parents=True, exist_ok=True)
    
    with open(tree_path, 'w', encoding='utf-8') as f:
        json.dump(tree, f, ensure_ascii=False, indent=2)


# ============================================================
#  保存新版本
# ============================================================

def save_version(project_path, asset_type, asset_name, file_path, params=None, 
                 note="", parent_uuid=None):
    """
    保存一个新版本（锁定）
    
    Args:
        project_path: 项目路径
        asset_type: 资产类型 (character/scene/storyboard/animation)
        asset_name: 资产名称
        file_path: 要保存的结果文件路径
        params: 参数字典 (prompt, seed, model, steps...)
        note: 版本备注
        parent_uuid: 父版本UUID（用于建立版本树关系）
    
    Returns:
        dict: 包含版本信息的字典
    """
    # 确保K13已初始化
    init_k13(project_path)
    
    # 加载版本树
    tree = load_tree(project_path, asset_type, asset_name)
    
    # 生成新版本UUID
    new_uuid = short_uuid()
    
    # 确定版本号
    version_num = len(tree["versions"]) + 1
    
    # 创建版本目录
    version_dir = get_versions_dir(project_path, asset_type, asset_name) / new_uuid
    version_dir.mkdir(parents=True, exist_ok=True)
    
    # 复制结果文件
    src_file = Path(file_path)
    if not src_file.exists():
        return {"status": "error", "message": f"文件不存在: {file_path}"}
    
    dest_file = version_dir / f"result{src_file.suffix}"
    shutil.copy2(src_file, dest_file)
    
    # 保存参数快照
    params_snapshot = params or {}
    params_path = version_dir / "params.json"
    with open(params_path, 'w', encoding='utf-8') as f:
        json.dump(params_snapshot, f, ensure_ascii=False, indent=2)
    
    # 创建版本信息
    version_info = {
        "uuid": new_uuid,
        "version": f"v{version_num}",
        "asset_type": asset_type,
        "asset_name": asset_name,
        "locked": True,
        "created_at": datetime.now().isoformat(),
        "parent_uuid": parent_uuid,
        "note": note,
        "file": str(dest_file.relative_to(Path(project_path))),
        "params_file": str(params_path.relative_to(Path(project_path))),
        "params": params_snapshot
    }
    
    # 添加到版本树
    tree["versions"].append(version_info)
    tree["latest_uuid"] = new_uuid
    tree["updated_at"] = datetime.now().isoformat()
    
    # 保存版本树
    save_tree(project_path, asset_type, asset_name, tree)
    
    return {
        "status": "ok",
        "message": f"版本已锁定: v{version_num} ({new_uuid})",
        "uuid": new_uuid,
        "version": f"v{version_num}",
        "version_dir": str(version_dir),
        "info": version_info
    }


# ============================================================
#  查询版本
# ============================================================

def list_versions(project_path, asset_type, asset_name, tree_format=True):
    """
    列出所有版本
    
    Args:
        tree_format: 是否以树状格式输出（默认True）
    
    Returns:
        dict: 包含版本列表和统计信息
    """
    tree = load_tree(project_path, asset_type, asset_name)
    versions = tree.get("versions", [])
    
    if not versions:
        return {
            "status": "ok",
            "count": 0,
            "message": "暂无版本",
            "versions": []
        }
    
    # 构建树状结构
    tree_structure = []
    uuid_to_version = {v["uuid"]: v for v in versions}
    
    # 根节点（没有父版本的）
    roots = [v for v in versions if not v.get("parent_uuid")]
    
    def build_tree(version, depth=0):
        node = {
            **version,
            "depth": depth
        }
        tree_structure.append(node)
        
        # 找子节点
        children = [v for v in versions if v.get("parent_uuid") == version["uuid"]]
        for child in children:
            build_tree(child, depth + 1)
    
    for root in roots:
        build_tree(root)
    
    # 统计
    locked_count = sum(1 for v in versions if v.get("locked"))
    
    return {
        "status": "ok",
        "count": len(versions),
        "locked_count": locked_count,
        "latest_uuid": tree.get("latest_uuid"),
        "versions": tree_structure if tree_format else versions,
        "asset_name": asset_name,
        "asset_type": asset_type
    }


def get_version(project_path, asset_type, asset_name, version_uuid):
    """获取单个版本的详细信息"""
    tree = load_tree(project_path, asset_type, asset_name)
    
    for v in tree.get("versions", []):
        if v["uuid"] == version_uuid:
            return {"status": "ok", "version": v}
    
    return {"status": "error", "message": f"版本不存在: {version_uuid}"}


def find_version_by_number(project_path, asset_type, asset_name, version_num):
    """按版本号查找（如 'v1', 'v2'）"""
    tree = load_tree(project_path, asset_type, asset_name)
    
    target = f"v{version_num}" if isinstance(version_num, int) else version_num
    
    for v in tree.get("versions", []):
        if v["version"] == target:
            return {"status": "ok", "version": v}
    
    return {"status": "error", "message": f"版本不存在: {target}"}


# ============================================================
#  分支 & 对比
# ============================================================

def create_branch(project_path, asset_type, asset_name, parent_uuid, note=""):
    """
    从指定版本创建分支（记录分支关系，不复制文件）
    
    注意：这只是记录分支意图，实际生成分支版本需要调用 save_version
    并传入 parent_uuid 参数
    """
    result = get_version(project_path, asset_type, asset_name, parent_uuid)
    if result["status"] != "ok":
        return result
    
    parent = result["version"]
    
    return {
        "status": "ok",
        "message": f"从 {parent['version']} ({parent_uuid}) 创建分支",
        "parent_uuid": parent_uuid,
        "parent_version": parent["version"],
        "hint": "调用 save_version 时传入 parent_uuid 即可生成分支版本",
        "note": note
    }


def compare_versions(project_path, asset_type, asset_name, uuid_a, uuid_b):
    """
    对比两个版本的参数差异
    
    Returns:
        dict: 包含相同和不同的参数
    """
    va = get_version(project_path, asset_type, asset_name, uuid_a)
    vb = get_version(project_path, asset_type, asset_name, uuid_b)
    
    if va["status"] != "ok":
        return va
    if vb["status"] != "ok":
        return vb
    
    params_a = va["version"].get("params", {})
    params_b = vb["version"].get("params", {})
    
    all_keys = set(list(params_a.keys()) + list(params_b.keys()))
    
    same = {}
    different = {}
    only_a = {}
    only_b = {}
    
    for key in all_keys:
        val_a = params_a.get(key)
        val_b = params_b.get(key)
        
        if key in params_a and key in params_b:
            if val_a == val_b:
                same[key] = val_a
            else:
                different[key] = {"v1": val_a, "v2": val_b}
        elif key in params_a:
            only_a[key] = val_a
        else:
            only_b[key] = val_b
    
    return {
        "status": "ok",
        "version_a": {"uuid": uuid_a, "version": va["version"]["version"]},
        "version_b": {"uuid": uuid_b, "version": vb["version"]["version"]},
        "same_count": len(same),
        "different_count": len(different),
        "same": same,
        "different": different,
        "only_in_a": only_a,
        "only_in_b": only_b
    }


# ============================================================
#  删除版本（危险操作）
# ============================================================

def delete_version(project_path, asset_type, asset_name, version_uuid, force=False):
    """
    删除一个版本（危险操作！）
    
    默认需要 force=True 才能执行，防止误删。
    注意：K13的核心理念是"锁定即冻结"，删除是不推荐的操作。
    仅在确实不需要了（比如测试数据）时才使用。
    """
    if not force:
        return {
            "status": "error",
            "message": "删除是危险操作，请加 force=True 确认。K13理念是锁定即冻结，不建议删除。"
        }
    
    tree = load_tree(project_path, asset_type, asset_name)
    versions = tree.get("versions", [])
    
    # 查找版本
    target = None
    for i, v in enumerate(versions):
        if v["uuid"] == version_uuid:
            target = v
            break
    
    if not target:
        return {"status": "error", "message": f"版本不存在: {version_uuid}"}
    
    # 检查是否有子版本
    children = [v for v in versions if v.get("parent_uuid") == version_uuid]
    if children:
        child_uuids = [v["uuid"] for v in children]
        return {
            "status": "error",
            "message": f"该版本有 {len(children)} 个子版本，不能删除。子版本: {child_uuids}",
            "children": child_uuids
        }
    
    # 删除文件
    version_dir = get_versions_dir(project_path, asset_type, asset_name) / version_uuid
    if version_dir.exists():
        shutil.rmtree(version_dir)
    
    # 从版本树移除
    versions.remove(target)
    tree["versions"] = versions
    
    if tree.get("latest_uuid") == version_uuid:
        tree["latest_uuid"] = versions[-1]["uuid"] if versions else None
    
    save_tree(project_path, asset_type, asset_name, tree)
    
    return {
        "status": "ok",
        "message": f"版本已删除: {version_uuid}",
        "deleted_version": target
    }


# ============================================================
#  命令行接口
# ============================================================

def print_help():
    """打印帮助信息"""
    help_text = """
K13 版本树 - AI生成版本管理工具

用法: python k13.py <命令> [参数]

命令:
  init <项目路径>                    初始化K13
  save <项目> <类型> <名称> <文件>   保存并锁定新版本
    --params '{"key":"val"}'         参数快照 (JSON字符串)
    --note "备注"                    版本备注
    --parent <UUID>                  父版本UUID
  list <项目> <类型> <名称>          列出所有版本
  get <项目> <类型> <名称> <UUID>    查看单个版本
  compare <项目> <类型> <名称> <UUID1> <UUID2>  对比两个版本
  delete <项目> <类型> <名称> <UUID> 删除版本 (需 --force)
    --force                          确认删除

资产类型: character | scene | storyboard | animation

示例:
  python k13.py init ./my_project
  python k13.py save ./my_project character 林月 out.png --params '{"seed":123}' --note "初版"
  python k13.py list ./my_project character 林月
  python k13.py get ./my_project character 林月 abc12345
  python k13.py compare ./my_project character 林月 abc12345 def67890
"""
    print(help_text)


def main():
    if len(sys.argv) < 2:
        print_help()
        return
    
    cmd = sys.argv[1]
    
    try:
        if cmd == "init":
            if len(sys.argv) < 3:
                print("错误: 缺少项目路径")
                return
            result = init_k13(sys.argv[2])
            print(json.dumps(result, ensure_ascii=False, indent=2))
        
        elif cmd == "save":
            if len(sys.argv) < 6:
                print("错误: 参数不足，需要: save <项目> <类型> <名称> <文件>")
                return
            
            project = sys.argv[2]
            asset_type = sys.argv[3]
            asset_name = sys.argv[4]
            file_path = sys.argv[5]
            
            # 解析可选参数
            params = None
            note = ""
            parent_uuid = None
            
            i = 6
            while i < len(sys.argv):
                if sys.argv[i] == "--params" and i + 1 < len(sys.argv):
                    params = json.loads(sys.argv[i + 1])
                    i += 2
                elif sys.argv[i] == "--note" and i + 1 < len(sys.argv):
                    note = sys.argv[i + 1]
                    i += 2
                elif sys.argv[i] == "--parent" and i + 1 < len(sys.argv):
                    parent_uuid = sys.argv[i + 1]
                    i += 2
                else:
                    i += 1
            
            result = save_version(project, asset_type, asset_name, file_path, 
                                  params=params, note=note, parent_uuid=parent_uuid)
            print(json.dumps(result, ensure_ascii=False, indent=2))
        
        elif cmd == "list":
            if len(sys.argv) < 5:
                print("错误: 参数不足，需要: list <项目> <类型> <名称>")
                return
            result = list_versions(sys.argv[2], sys.argv[3], sys.argv[4])
            print(json.dumps(result, ensure_ascii=False, indent=2))
        
        elif cmd == "get":
            if len(sys.argv) < 6:
                print("错误: 参数不足，需要: get <项目> <类型> <名称> <UUID>")
                return
            result = get_version(sys.argv[2], sys.argv[3], sys.argv[4], sys.argv[5])
            print(json.dumps(result, ensure_ascii=False, indent=2))
        
        elif cmd == "compare":
            if len(sys.argv) < 7:
                print("错误: 参数不足，需要: compare <项目> <类型> <名称> <UUID1> <UUID2>")
                return
            result = compare_versions(sys.argv[2], sys.argv[3], sys.argv[4], 
                                       sys.argv[5], sys.argv[6])
            print(json.dumps(result, ensure_ascii=False, indent=2))
        
        elif cmd == "delete":
            if len(sys.argv) < 6:
                print("错误: 参数不足，需要: delete <项目> <类型> <名称> <UUID>")
                return
            force = "--force" in sys.argv
            result = delete_version(sys.argv[2], sys.argv[3], sys.argv[4], 
                                     sys.argv[5], force=force)
            print(json.dumps(result, ensure_ascii=False, indent=2))
        
        elif cmd == "-h" or cmd == "--help":
            print_help()
        
        else:
            print(f"未知命令: {cmd}")
            print_help()
    
    except Exception as e:
        print(json.dumps({"status": "error", "message": str(e)}, ensure_ascii=False))


if __name__ == "__main__":
    main()
