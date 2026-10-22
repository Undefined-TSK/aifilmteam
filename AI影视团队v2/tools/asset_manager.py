#!/usr/bin/env python3
"""
资产清单与依赖管理工具
管理项目中的所有资产，以及它们之间的依赖关系

资产类型：
- character: 角色图
- scene: 场景图
- storyboard: 分镜
- video: 动画/视频

用法：
  python asset_manager.py list <project_path>                  # 列出所有资产
  python asset_manager.py add <project_path> <asset_type> <asset_name> <deps_json>  # 添加资产
  python asset_manager.py update <project_path> <asset_name> <field> <value>  # 更新资产字段
  python asset_manager.py remove <project_path> <asset_name>   # 移除资产
  python asset_manager.py status <project_path>                # 查看整体进度状态
  python asset_manager.py next <project_path>                  # 下一个可以开始的资产（依赖都满足的）
  python asset_manager.py plan <project_path> <prompt>         # 根据指令拆解生成资产计划
"""

import sys
import json
from datetime import datetime
from pathlib import Path

ASSETS_FILE = "assets.json"

# 默认依赖顺序：角色 → 场景 → 分镜 → 动画
DEFAULT_DEPENDENCIES = {
    "character": [],
    "scene": [],
    "storyboard": ["character", "scene"],
    "video": ["storyboard"]
}


def get_assets_path(project_path):
    return Path(project_path) / ASSETS_FILE


def load_assets(project_path):
    """加载资产清单"""
    assets_path = get_assets_path(project_path)
    if not assets_path.exists():
        return {"assets": [], "created_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S")}
    with open(assets_path, "r", encoding="utf-8") as f:
        return json.load(f)


def save_assets(project_path, data):
    """保存资产清单"""
    assets_path = get_assets_path(project_path)
    assets_path.parent.mkdir(parents=True, exist_ok=True)
    with open(assets_path, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)


def list_assets(project_path):
    """列出所有资产"""
    data = load_assets(project_path)
    assets = data.get("assets", [])
    
    result = {
        "total": len(assets),
        "by_type": {},
        "assets": assets
    }
    
    for asset in assets:
        atype = asset["type"]
        if atype not in result["by_type"]:
            result["by_type"][atype] = 0
        result["by_type"][atype] += 1
    
    print(json.dumps(result, ensure_ascii=False, indent=2))


def add_asset(project_path, asset_type, asset_name, deps_json):
    """添加一个资产"""
    data = load_assets(project_path)
    
    # 检查是否已存在
    for a in data["assets"]:
        if a["name"] == asset_name:
            print(json.dumps({"status": "exists", "message": f"资产 {asset_name} 已存在"}, ensure_ascii=False))
            return
    
    # 解析依赖
    try:
        dependencies = json.loads(deps_json) if deps_json else []
    except json.JSONDecodeError:
        dependencies = []
    
    # 如果没指定依赖，用默认的
    if not dependencies and asset_type in DEFAULT_DEPENDENCIES:
        # 默认依赖是类型，需要找对应类型的资产
        dep_types = DEFAULT_DEPENDENCIES[asset_type]
        for a in data["assets"]:
            if a["type"] in dep_types:
                dependencies.append(a["name"])
    
    asset = {
        "name": asset_name,
        "type": asset_type,
        "status": "pending",  # pending, generating, review, locked, failed
        "dependencies": dependencies,
        "description": "",
        "prompt": "",
        "params": {},
        "output_file": None,
        "version_uuid": None,
        "retry_count": 0,
        "created_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "updated_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    }
    
    data["assets"].append(asset)
    save_assets(project_path, data)
    
    print(json.dumps({
        "status": "added",
        "name": asset_name,
        "type": asset_type,
        "dependencies": dependencies
    }, ensure_ascii=False, indent=2))


def update_asset(project_path, asset_name, field, value):
    """更新资产字段"""
    data = load_assets(project_path)
    
    for asset in data["assets"]:
        if asset["name"] == asset_name:
            if field == "status":
                asset["status"] = value
            elif field == "output_file":
                asset["output_file"] = value
            elif field == "version_uuid":
                asset["version_uuid"] = value
            elif field == "prompt":
                asset["prompt"] = value
            elif field == "description":
                asset["description"] = value
            elif field == "retry_count":
                asset["retry_count"] = int(value)
            elif field == "params":
                try:
                    asset["params"] = json.loads(value)
                except json.JSONDecodeError:
                    pass
            else:
                asset[field] = value
            
            asset["updated_at"] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            save_assets(project_path, data)
            
            print(json.dumps({
                "status": "updated",
                "asset": asset_name,
                "field": field,
                "value": value
            }, ensure_ascii=False, indent=2))
            return
    
    print(json.dumps({"status": "not_found", "message": f"资产 {asset_name} 不存在"}, ensure_ascii=False))


def remove_asset(project_path, asset_name):
    """移除资产"""
    data = load_assets(project_path)
    
    original_count = len(data["assets"])
    data["assets"] = [a for a in data["assets"] if a["name"] != asset_name]
    
    if len(data["assets"]) == original_count:
        print(json.dumps({"status": "not_found", "message": f"资产 {asset_name} 不存在"}, ensure_ascii=False))
        return
    
    save_assets(project_path, data)
    print(json.dumps({"status": "removed", "name": asset_name}, ensure_ascii=False, indent=2))


def get_status(project_path):
    """查看整体进度状态"""
    data = load_assets(project_path)
    assets = data.get("assets", [])
    
    status_counts = {
        "pending": 0,
        "generating": 0,
        "review": 0,
        "locked": 0,
        "failed": 0
    }
    
    for asset in assets:
        s = asset.get("status", "pending")
        if s in status_counts:
            status_counts[s] += 1
        else:
            status_counts[s] = 1
    
    total = len(assets)
    locked = status_counts.get("locked", 0)
    progress = (locked / total * 100) if total > 0 else 0
    
    print(json.dumps({
        "total": total,
        "progress_percent": round(progress, 1),
        "by_status": status_counts,
        "locked_count": locked
    }, ensure_ascii=False, indent=2))


def get_next_ready(project_path):
    """获取下一个可以开始生成的资产（依赖都已满足）"""
    data = load_assets(project_path)
    assets = data.get("assets", [])
    
    # 构建已锁定资产集合
    locked_names = {a["name"] for a in assets if a.get("status") == "locked"}
    
    # 找pending且依赖都满足的
    ready = []
    for asset in assets:
        if asset.get("status") != "pending":
            continue
        
        deps = asset.get("dependencies", [])
        all_deps_met = all(dep in locked_names for dep in deps)
        
        if all_deps_met:
            ready.append({
                "name": asset["name"],
                "type": asset["type"],
                "dependencies": deps
            })
    
    # 按类型排序：角色 → 场景 → 分镜 → 动画
    type_order = {"character": 0, "scene": 1, "storyboard": 2, "video": 3}
    ready.sort(key=lambda x: type_order.get(x["type"], 99))
    
    print(json.dumps({
        "ready_count": len(ready),
        "next": ready[0] if ready else None,
        "all_ready": ready
    }, ensure_ascii=False, indent=2))


def plan_from_prompt(project_path, prompt):
    """
    根据指令拆解生成资产计划
    智能识别角色、场景、分镜、视频等资产类型及数量
    """
    data = load_assets(project_path)
    
    # 分类关键词库
    character_keywords = [
        "女孩", "男孩", "女主角", "男主角", "女主", "男主", "角色", "人物",
        "剑客", "武士", "公主", "王子", "医生", "警察", "侦探", "老师",
        "穿", "叫", "名字叫", "名叫", "小雪", "林月", "白衣", "黑衣",
        "主角", "配角", "反派", "老人", "小孩", "女性", "男性"
    ]
    
    scene_keywords = [
        "雨夜", "街道", "场景", "房间", "室内", "室外", "城市", "森林", "海",
        "竹林", "沙漠", "雪山", "城堡", "宫殿", "学校", "医院", "办公室",
        "背景", "环境", "地点", "外景", "内景", "全景", "远景", "中景"
    ]
    
    storyboard_keywords = [
        "分镜", "镜头", "画面", "构图", "景别", "特写", "全景", "运镜",
        "第一镜", "开场镜头", "结尾镜头", "镜头语言"
    ]
    
    video_keywords = [
        "短片", "视频", "动画", "秒", "镜头运动", "动态", "影片", "电影",
        "动画短片", "宣传视频", "片头", "片尾"
    ]
    
    # 统计各类关键词命中次数
    def count_keywords(text, keywords):
        count = 0
        matched = []
        for kw in keywords:
            if kw in text:
                count += 1
                matched.append(kw)
        return count, matched
    
    char_count, char_matched = count_keywords(prompt, character_keywords)
    scene_count, scene_matched = count_keywords(prompt, scene_keywords)
    storyboard_count, storyboard_matched = count_keywords(prompt, storyboard_keywords)
    video_count, video_matched = count_keywords(prompt, video_keywords)
    
    # 构建资产列表
    assets_to_create = []
    
    # 角色资产（尝试识别角色数量和名字）
    if char_count > 0:
        # 简单识别角色名字：找"叫XX"、"名叫XX"、"名字叫XX"
        import re
        name_patterns = [
            r"叫([\u4e00-\u9fa5]{2,4})",
            r"名叫([\u4e00-\u9fa5]{2,4})",
            r"名字叫([\u4e00-\u9fa5]{2,4})",
            r"女主角([\u4e00-\u9fa5]{2,4})",
            r"男主角([\u4e00-\u9fa5]{2,4})",
        ]
        char_names = []
        for pattern in name_patterns:
            matches = re.findall(pattern, prompt)
            char_names.extend(matches)
        
        # 去重
        char_names = list(set(char_names))
        
        if char_names:
            for name in char_names[:3]:  # 最多识别3个角色
                assets_to_create.append({
                    "type": "character",
                    "name": f"{name}角色",
                    "detected_name": name
                })
        else:
            # 没识别出具体名字，给通用名称
            # 判断是主角还是多个角色
            if "两个" in prompt or "两位" in prompt or "两个角色" in prompt:
                assets_to_create.append({"type": "character", "name": "主角A"})
                assets_to_create.append({"type": "character", "name": "主角B"})
            else:
                assets_to_create.append({"type": "character", "name": "主角形象"})
    
    # 场景资产
    if scene_count > 0:
        # 识别场景类型
        scene_names = []
        if "竹林" in prompt:
            scene_names.append("竹林场景")
        elif "城市" in prompt:
            scene_names.append("城市场景")
        elif "森林" in prompt:
            scene_names.append("森林场景")
        elif "海" in prompt:
            scene_names.append("海边场景")
        elif "沙漠" in prompt:
            scene_names.append("沙漠场景")
        elif "雪山" in prompt:
            scene_names.append("雪山场景")
        elif "城堡" in prompt or "宫殿" in prompt:
            scene_names.append("城堡场景")
        elif "房间" in prompt or "室内" in prompt:
            scene_names.append("室内场景")
        else:
            scene_names.append("主场景")
        
        for sname in scene_names[:2]:  # 最多2个场景
            assets_to_create.append({"type": "scene", "name": sname})
    
    # 分镜资产
    if storyboard_count > 0:
        assets_to_create.append({"type": "storyboard", "name": "第一组分镜"})
    
    # 视频资产
    if video_count > 0:
        assets_to_create.append({"type": "video", "name": "成片"})
    
    # 如果什么都没识别出来，默认给角色+场景
    if not assets_to_create:
        assets_to_create = [
            {"type": "character", "name": "主角形象"},
            {"type": "scene", "name": "主场景"}
        ]
    
    # 计算依赖关系说明
    dep_order = []
    types_in_plan = [a["type"] for a in assets_to_create]
    if "character" in types_in_plan:
        dep_order.append("角色")
    if "scene" in types_in_plan:
        dep_order.append("场景")
    if "storyboard" in types_in_plan:
        dep_order.append("分镜")
    if "video" in types_in_plan:
        dep_order.append("动画")
    
    print(json.dumps({
        "prompt": prompt,
        "analysis": {
            "character_keywords_hit": char_count,
            "scene_keywords_hit": scene_count,
            "storyboard_keywords_hit": storyboard_count,
            "video_keywords_hit": video_count,
            "character_matched": char_matched,
            "scene_matched": scene_matched
        },
        "detected_assets": assets_to_create,
        "dependency_order": " → ".join(dep_order) if dep_order else "角色 → 场景 → 分镜 → 动画",
        "note": "AI拆解仅供参考，请人工确认后再执行"
    }, ensure_ascii=False, indent=2))


def main():
    if len(sys.argv) < 3:
        print(__doc__)
        sys.exit(1)
    
    command = sys.argv[1]
    project_path = sys.argv[2]
    
    if command == "list":
        list_assets(project_path)
    elif command == "add":
        if len(sys.argv) < 6:
            print("用法: add <project_path> <asset_type> <asset_name> <deps_json>")
            sys.exit(1)
        add_asset(project_path, sys.argv[3], sys.argv[4], sys.argv[5])
    elif command == "update":
        if len(sys.argv) < 6:
            print("用法: update <project_path> <asset_name> <field> <value>")
            sys.exit(1)
        update_asset(project_path, sys.argv[3], sys.argv[4], sys.argv[5])
    elif command == "remove":
        if len(sys.argv) < 4:
            print("用法: remove <project_path> <asset_name>")
            sys.exit(1)
        remove_asset(project_path, sys.argv[3])
    elif command == "status":
        get_status(project_path)
    elif command == "next":
        get_next_ready(project_path)
    elif command == "plan":
        if len(sys.argv) < 4:
            print("用法: plan <project_path> <prompt>")
            sys.exit(1)
        plan_from_prompt(project_path, sys.argv[3])
    else:
        print(f"未知命令: {command}")
        print(__doc__)
        sys.exit(1)


if __name__ == "__main__":
    main()
