#!/usr/bin/env python3
"""
Character Lock Writer — 角色锁定写入工具
角色设计师定稿后写入character_lock JSON，供分镜师和动画师自动注入prompt
"""

import sys
import json
from pathlib import Path
from datetime import datetime


def get_lock_dir(project_path):
    return Path(project_path) / "character_lock"


def write_character(project_path, character_name, params_json):
    lock_dir = get_lock_dir(project_path)
    lock_dir.mkdir(parents=True, exist_ok=True)

    try:
        data = json.loads(params_json)
    except json.JSONDecodeError:
        return {"status": "error", "message": "Invalid JSON parameters"}

    data["character_name"] = character_name
    data["locked_at"] = datetime.now().isoformat()

    file_path = lock_dir / f"{character_name}.json"
    file_path.write_text(
        json.dumps(data, ensure_ascii=False, indent=2),
        encoding="utf-8"
    )

    return {
        "status": "locked",
        "character_name": character_name,
        "path": str(file_path),
        "content": data,
    }


def read_character(project_path, character_name):
    file_path = get_lock_dir(project_path) / f"{character_name}.json"
    if not file_path.exists():
        return {"status": "not_found", "character_name": character_name}
    data = json.loads(file_path.read_text(encoding="utf-8"))
    return {"status": "ok", "character_name": character_name, "content": data}


def list_characters(project_path):
    lock_dir = get_lock_dir(project_path)
    if not lock_dir.exists():
        return {"characters": [], "total": 0}
    characters = []
    for f in sorted(lock_dir.glob("*.json")):
        try:
            data = json.loads(f.read_text(encoding="utf-8"))
            data["file_name"] = f.stem
            characters.append(data)
        except Exception:
            pass
    return {"characters": characters, "total": len(characters)}


def remove_character(project_path, character_name):
    file_path = get_lock_dir(project_path) / f"{character_name}.json"
    if not file_path.exists():
        return {"status": "not_found", "character_name": character_name}
    file_path.unlink()
    return {"status": "removed", "character_name": character_name}


def main():
    if len(sys.argv) < 3:
        print(json.dumps({"error": "Usage: character_lock_writer.py <project_path> <command> [args...]"}))
        sys.exit(1)

    project_path = sys.argv[1]
    command = sys.argv[2]

    if command == "write":
        if len(sys.argv) < 5:
            print(json.dumps({"error": "Usage: write <character_name> <params_json>"}))
            sys.exit(1)
        result = write_character(project_path, sys.argv[3], sys.argv[4])
    elif command == "read":
        if len(sys.argv) < 4:
            print(json.dumps({"error": "Usage: read <character_name>"}))
            sys.exit(1)
        result = read_character(project_path, sys.argv[3])
    elif command == "list":
        result = list_characters(project_path)
    elif command == "remove":
        if len(sys.argv) < 4:
            print(json.dumps({"error": "Usage: remove <character_name>"}))
            sys.exit(1)
        result = remove_character(project_path, sys.argv[3])
    else:
        result = {"error": f"Unknown command: {command}"}

    print(json.dumps(result, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
