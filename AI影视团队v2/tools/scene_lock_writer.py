#!/usr/bin/env python3
"""
Scene Lock Writer — 场景锁定写入工具
场景设计师定稿后写入scene_lock JSON，供分镜师和动画师自动注入prompt
"""

import sys
import json
from pathlib import Path
from datetime import datetime


def get_lock_dir(project_path):
    return Path(project_path) / "scene_lock"


def write_scene(project_path, scene_name, params_json):
    lock_dir = get_lock_dir(project_path)
    lock_dir.mkdir(parents=True, exist_ok=True)

    try:
        data = json.loads(params_json)
    except json.JSONDecodeError:
        return {"status": "error", "message": "Invalid JSON parameters"}

    data["scene_name"] = scene_name
    data["locked_at"] = datetime.now().isoformat()

    file_path = lock_dir / f"{scene_name}.json"
    file_path.write_text(
        json.dumps(data, ensure_ascii=False, indent=2),
        encoding="utf-8"
    )

    return {
        "status": "locked",
        "scene_name": scene_name,
        "path": str(file_path),
        "content": data,
    }


def read_scene(project_path, scene_name):
    file_path = get_lock_dir(project_path) / f"{scene_name}.json"
    if not file_path.exists():
        return {"status": "not_found", "scene_name": scene_name}
    data = json.loads(file_path.read_text(encoding="utf-8"))
    return {"status": "ok", "scene_name": scene_name, "content": data}


def list_scenes(project_path):
    lock_dir = get_lock_dir(project_path)
    if not lock_dir.exists():
        return {"scenes": [], "total": 0}
    scenes = []
    for f in sorted(lock_dir.glob("*.json")):
        try:
            data = json.loads(f.read_text(encoding="utf-8"))
            data["file_name"] = f.stem
            scenes.append(data)
        except Exception:
            pass
    return {"scenes": scenes, "total": len(scenes)}


def remove_scene(project_path, scene_name):
    file_path = get_lock_dir(project_path) / f"{scene_name}.json"
    if not file_path.exists():
        return {"status": "not_found", "scene_name": scene_name}
    file_path.unlink()
    return {"status": "removed", "scene_name": scene_name}


def main():
    if len(sys.argv) < 3:
        print(json.dumps({"error": "Usage: scene_lock_writer.py <project_path> <command> [args...]"}))
        sys.exit(1)

    project_path = sys.argv[1]
    command = sys.argv[2]

    if command == "write":
        if len(sys.argv) < 5:
            print(json.dumps({"error": "Usage: write <scene_name> <params_json>"}))
            sys.exit(1)
        result = write_scene(project_path, sys.argv[3], sys.argv[4])
    elif command == "read":
        if len(sys.argv) < 4:
            print(json.dumps({"error": "Usage: read <scene_name>"}))
            sys.exit(1)
        result = read_scene(project_path, sys.argv[3])
    elif command == "list":
        result = list_scenes(project_path)
    elif command == "remove":
        if len(sys.argv) < 4:
            print(json.dumps({"error": "Usage: remove <scene_name>"}))
            sys.exit(1)
        result = remove_scene(project_path, sys.argv[3])
    else:
        result = {"error": f"Unknown command: {command}"}

    print(json.dumps(result, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
