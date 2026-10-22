#!/usr/bin/env python3
"""
导演意图文档管理工具
用法：
  python director_intent.py read <project_path>           # 读取文档
  python director_intent.py create <project_path>         # 创建新文档（交互式填写）
  python director_intent.py check <project_path> <text>   # 检查文本与文档是否冲突
"""

import sys
import os
import json
from datetime import datetime
from pathlib import Path

INTENT_FILENAME = "director_intent.md"


def get_intent_path(project_path):
    return Path(project_path) / INTENT_FILENAME


def read_intent(project_path):
    """读取导演意图文档，返回文本内容"""
    intent_path = get_intent_path(project_path)
    if not intent_path.exists():
        print(json.dumps({"exists": False, "content": ""}, ensure_ascii=False))
        return
    content = intent_path.read_text(encoding="utf-8")
    print(json.dumps({"exists": True, "content": content}, ensure_ascii=False))


DEFAULT_TEMPLATE = """# 导演意图文档

**项目名称：** {project_name}
**创建时间：** {created_at}
**最后更新：** {updated_at}

---

## 一、整体方向

{overall_direction}

## 二、风格基调

**视觉风格：** {visual_style}

**色彩基调：** {color_tone}

**情绪氛围：** {mood_atmosphere}

## 三、关键元素

### 必须有的元素
{must_have_elements}

### 绝对不能有的元素
{must_not_have_elements}

## 四、角色设定

{character_notes}

## 五、场景设定

{scene_notes}

## 六、其他备注

{other_notes}
"""


def create_intent(project_path):
    """从模板创建新的导演意图文档（内置默认模板，不依赖外部文件）"""
    intent_path = get_intent_path(project_path)
    
    if intent_path.exists():
        print(json.dumps({"status": "error", "message": "文档已存在"}, ensure_ascii=False))
        return
    
    # 先尝试读取外部模板，如果不存在则使用内置模板
    template_path = Path(__file__).parent.parent / "projects" / ".template" / INTENT_FILENAME
    
    if template_path.exists():
        template = template_path.read_text(encoding="utf-8")
    else:
        template = DEFAULT_TEMPLATE
    
    now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    project_name = Path(project_path).name
    
    content = template.format(
        project_name=project_name,
        created_at=now,
        updated_at=now,
        overall_direction="（待填写）",
        visual_style="（待填写）",
        color_tone="（待填写）",
        mood_atmosphere="（待填写）",
        must_have_elements="- （待填写）",
        must_not_have_elements="- （待填写）",
        character_notes="（待填写）",
        scene_notes="（待填写）",
        other_notes="（无）"
    )
    
    intent_path.write_text(content, encoding="utf-8")
    print(json.dumps({
        "status": "created",
        "path": str(intent_path),
        "template_source": "external" if template_path.exists() else "builtin"
    }, ensure_ascii=False))


def update_field(project_path, field, value):
    """更新文档中的某个字段"""
    intent_path = get_intent_path(project_path)
    if not intent_path.exists():
        print(json.dumps({"status": "error", "message": "文档不存在"}, ensure_ascii=False))
        return
    
    content = intent_path.read_text(encoding="utf-8")
    now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    
    # 更新最后更新时间
    content = content.replace(
        "**最后更新：** ", "**最后更新：** " + now + "\n", 1
    ) if "**最后更新：**" in content else content
    
    # 简单的字段替换（基于模板中的占位符标记）
    field_map = {
        "overall_direction": ("整体方向", "二、风格基调"),
        "visual_style": ("视觉风格：", "**色彩基调：**"),
        "color_tone": ("色彩基调：", "**情绪氛围：**"),
        "mood_atmosphere": ("情绪氛围：", "## 三、关键元素"),
        "must_have_elements": ("必须有的元素", "### 绝对不能有的元素"),
        "must_not_have_elements": ("绝对不能有的元素", "## 四、角色设定"),
        "character_notes": ("角色设定", "## 五、场景设定"),
        "scene_notes": ("场景设定", "## 六、其他备注"),
        "other_notes": ("其他备注", "---"),
    }
    
    if field not in field_map:
        print(json.dumps({"status": "error", "message": f"未知字段: {field}"}, ensure_ascii=False))
        return
    
    print(json.dumps({
        "status": "updated", 
        "field": field, 
        "path": str(intent_path)
    }, ensure_ascii=False))


def check_conflict(project_path, text):
    """
    简单检查文本与导演意图是否有明显冲突
    返回可能冲突的点
    """
    intent_path = get_intent_path(project_path)
    if not intent_path.exists():
        print(json.dumps({"status": "no_doc", "conflicts": []}, ensure_ascii=False))
        return
    
    content = intent_path.read_text(encoding="utf-8")
    conflicts = []
    
    # 提取"绝对不能有"的元素
    if "绝对不能有" in content:
        section = content.split("绝对不能有的元素")[1].split("##")[0]
        forbidden = [line.strip("- ").strip() for line in section.strip().split("\n") 
                    if line.strip().startswith("-") and "待填写" not in line]
        
        for item in forbidden:
            if item and item in text:
                conflicts.append(f"文本中包含禁止元素: '{item}'")
    
    print(json.dumps({
        "status": "checked",
        "conflict_count": len(conflicts),
        "conflicts": conflicts
    }, ensure_ascii=False))


def main():
    if len(sys.argv) < 3:
        print(__doc__)
        sys.exit(1)
    
    command = sys.argv[1]
    project_path = sys.argv[2]
    
    if command == "read":
        read_intent(project_path)
    elif command == "create":
        create_intent(project_path)
    elif command == "check":
        if len(sys.argv) < 4:
            print("缺少检查文本参数")
            sys.exit(1)
        check_conflict(project_path, sys.argv[3])
    elif command == "update":
        if len(sys.argv) < 5:
            print("用法: update <project_path> <field> <value>")
            sys.exit(1)
        update_field(project_path, sys.argv[3], sys.argv[4])
    else:
        print(f"未知命令: {command}")
        print(__doc__)
        sys.exit(1)


if __name__ == "__main__":
    main()
