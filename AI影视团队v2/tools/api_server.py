#!/usr/bin/env python3
"""
CINEAST API Server — FastAPI版
前后端联调桥接层：FastAPI + uvicorn
包装现有CLI工具为HTTP API，同时托管前端页面
"""

import json
import subprocess
import sys
import os
from datetime import datetime
from pathlib import Path
from fastapi import Body, FastAPI, Query
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse, JSONResponse
from fastapi.middleware.cors import CORSMiddleware

# ============================================================
# 配置
# ============================================================

HOST = "127.0.0.1"
PORT = 8190
PROJECT_ROOT = Path(__file__).parent.parent
PROJECT_PATH = PROJECT_ROOT / "projects" / "雨夜寻猫"
TOOLS_DIR = Path(__file__).parent
WEB_DIR = PROJECT_ROOT / "web"
PYTHON = sys.executable

TOOLS = {
    "k13": TOOLS_DIR / "k13_version_tree.py",
    "budget": TOOLS_DIR / "budget_manager.py",
    "asset": TOOLS_DIR / "asset_manager.py",
    "handoff": TOOLS_DIR / "handoff_manager.py",
    "intent": TOOLS_DIR / "director_intent.py",
    "scene_lock": TOOLS_DIR / "scene_lock_writer.py",
    "charlock": TOOLS_DIR / "character_lock_writer.py",
    "comfyui": TOOLS_DIR / "comfyui_generator.py",
}


def run_tool(tool_key, args, timeout=30):
    """调用CLI工具并返回dict结果"""
    script = str(TOOLS[tool_key])
    cmd = [PYTHON, script] + args
    try:
        result = subprocess.run(
            cmd, capture_output=True, text=True, timeout=timeout
        )
        if result.returncode != 0:
            return {"error": result.stderr.strip() or "Tool execution failed"}
        out = result.stdout or ""
        if not out.strip():
            return {"error": "Tool produced no output"}
        try:
            return json.loads(out)
        except (json.JSONDecodeError, TypeError):
            return {"raw_output": out[:2000]}
    except subprocess.TimeoutExpired:
        return {"error": "Tool execution timed out (30s)"}
    except Exception as e:
        return {"error": str(e)}


def read_scene_locks():
    scene_lock_dir = PROJECT_PATH / "scene_lock"
    if not scene_lock_dir.exists():
        return {"scenes": [], "total": 0}
    scenes = []
    for f in sorted(scene_lock_dir.glob("*.json")):
        try:
            data = json.loads(f.read_text(encoding="utf-8"))
            data["file_name"] = f.stem
            scenes.append(data)
        except Exception:
            pass
    return {"scenes": scenes, "total": len(scenes)}


def get_project_info():
    intent_path = PROJECT_PATH / "director_intent.md"
    return {
        "project_name": PROJECT_PATH.name,
        "project_path": str(PROJECT_PATH),
        "has_intent": intent_path.exists(),
        "has_budget": (PROJECT_PATH / "budget.json").exists(),
        "has_assets": (PROJECT_PATH / "assets.json").exists(),
        "has_k13": (PROJECT_PATH / "k13_locked" / "versions.json").exists(),
        "has_handoffs": (PROJECT_PATH / "handoffs.json").exists(),
        "has_scene_locks": (PROJECT_PATH / "scene_lock").exists()
        and any((PROJECT_PATH / "scene_lock").glob("*.json")),
    }


def get_graph_path():
    return PROJECT_PATH / "graph.json"


def read_graph():
    graph_path = get_graph_path()
    if not graph_path.exists():
        return {"exists": False, "nodes": [], "edges": []}
    try:
        data = json.loads(graph_path.read_text(encoding="utf-8"))
        return {
            "exists": True,
            "nodes": data.get("nodes", []),
            "edges": data.get("edges", []),
            "saved_at": data.get("saved_at"),
        }
    except json.JSONDecodeError:
        # 损坏与"不存在"必须区分，否则前端会静默换回默认图，
        # 用户以为是自己改坏了画布。
        return {"exists": False, "corrupt": True,
                "message": "graph.json 解析失败，已保留原文件待人工确认",
                "nodes": [], "edges": []}
    except OSError as e:
        return {"exists": False, "error": str(e), "nodes": [], "edges": []}


def write_graph(payload):
    graph_path = get_graph_path()
    nodes = payload.get("nodes", [])
    edges = payload.get("edges", [])
    for n in nodes:
        n.pop("selected", None)
        n.pop("dragging", None)
        n.pop("measured", None)
    for e in edges:
        e.pop("selected", None)
    data = {
        "nodes": nodes,
        "edges": edges,
        "saved_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
    }
    # 原子写：先写同目录 tmp，再 os.replace 换名。中途失败只会留下一个
    # 多余的 .tmp，绝不会把正式文件写成半截 JSON。
    tmp = graph_path.with_name(graph_path.name + ".tmp")
    tmp.write_text(
        json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8"
    )
    os.replace(tmp, graph_path)
    return {"status": "saved", "nodes": len(nodes), "edges": len(edges), "saved_at": data["saved_at"]}


# ============================================================
# FastAPI App
# ============================================================

app = FastAPI(title="CINEAST API", version="2.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# 静态资源
# /assets → showcase页面图片资源
app.mount("/assets", StaticFiles(directory=str(WEB_DIR / "showcase" / "assets")), name="showcase-assets")
# /project-assets → 项目生成资产（角色/场景/分镜等，供workspace使用）
_project_assets = PROJECT_PATH / "assets"
if _project_assets.exists():
    app.mount("/project-assets", StaticFiles(directory=str(_project_assets)), name="project-assets")
# /k13-assets → K13锁定版本资产（供版本树缩略图使用）
_k13_locked = PROJECT_PATH / "k13_locked"
if _k13_locked.exists():
    app.mount("/k13-assets", StaticFiles(directory=str(_k13_locked)), name="k13-assets")
# /react → React Flow 工作台（构建产物）
_react_dist = WEB_DIR / "react-workspace" / "dist"
if _react_dist.exists():
    app.mount("/react", StaticFiles(directory=str(_react_dist), html=True), name="react-workspace")


# --- 页面路由 ---

@app.get("/", response_class=FileResponse)
async def page_index():
    """产品官网 showcase"""
    return FileResponse(str(WEB_DIR / "showcase" / "index.html"))


@app.get("/workspace", response_class=FileResponse)
async def page_workspace():
    """工作台（HTML版）"""
    return FileResponse(str(WEB_DIR / "workspace" / "workspace.html"))


@app.get("/workspace-react", response_class=FileResponse)
async def page_workspace_react():
    """工作台（React Flow版）"""
    dist_index = WEB_DIR / "react-workspace" / "dist" / "index.html"
    if dist_index.exists():
        return FileResponse(str(dist_index))
    return JSONResponse({"error": "React workspace not built. Run: cd web/react-workspace && npm run build"}, status_code=404)


# --- API 路由 ---

@app.get("/api")
async def api_root():
    return {
        "service": "CINEAST API",
        "version": "2.0",
        "endpoints": [
            "/api/health", "/api/project",
            "/api/budget/status", "/api/budget/history",
            "/api/versions", "/api/versions/history?name=xxx",
            "/api/assets", "/api/assets/status",
            "/api/handoffs", "/api/handoffs/stats",
            "/api/intent", "/api/scenes",
            "/api/graph (GET/POST/DELETE)",
        ],
    }


@app.get("/api/health")
async def health():
    return {"status": "ok", "project": PROJECT_PATH.name}


@app.get("/api/project")
async def project_info():
    return get_project_info()


@app.get("/api/budget/status")
async def budget_status():
    return JSONResponse(run_tool("budget", ["status", str(PROJECT_PATH)]))


@app.get("/api/budget/history")
async def budget_history():
    return JSONResponse(run_tool("budget", ["history", str(PROJECT_PATH)]))


@app.get("/api/versions")
async def versions_list():
    return JSONResponse(run_tool("k13", ["list", str(PROJECT_PATH)]))


@app.get("/api/versions/history")
async def versions_history(name: str = Query(..., description="资产名称")):
    return JSONResponse(run_tool("k13", ["history", str(PROJECT_PATH), name]))


@app.get("/api/assets")
async def assets_list():
    return JSONResponse(run_tool("asset", ["list", str(PROJECT_PATH)]))


@app.get("/api/assets/status")
async def assets_status():
    return JSONResponse(run_tool("asset", ["status", str(PROJECT_PATH)]))


@app.get("/api/handoffs")
async def handoffs_list(status: str = Query(None)):
    args = [str(PROJECT_PATH), "list"]
    if status:
        args.append(status)
    return JSONResponse(run_tool("handoff", args))


@app.get("/api/handoffs/stats")
async def handoffs_stats():
    return JSONResponse(run_tool("handoff", [str(PROJECT_PATH), "stats"]))


@app.get("/api/intent")
async def intent_read():
    return JSONResponse(run_tool("intent", ["read", str(PROJECT_PATH)]))


@app.get("/api/scenes")
async def scenes_list():
    return read_scene_locks()


@app.get("/api/characters")
async def characters_list():
    return run_tool(
        "charlock", [str(PROJECT_PATH), "list"]
    )

# --- 节点图画布持久化 ---

@app.get("/api/graph")
async def graph_get():
    return read_graph()


@app.post("/api/graph")
async def graph_save(payload: dict = Body(...)):
    try:
        return write_graph(payload)
    except Exception as e:
        return JSONResponse({"error": str(e)}, status_code=500)


@app.delete("/api/graph")
async def graph_reset():
    """重置画布存档：rename 成带时间戳的 .deleted 备份，可回滚，
    并把 exists/restored 如实告诉前端（不再把失败说成成功）。"""
    graph_path = get_graph_path()
    if not graph_path.exists():
        return {"status": "reset", "exists": False, "restored": True}
    stamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    backup = graph_path.with_name(f"graph_{stamp}.deleted")
    try:
        graph_path.rename(backup)
    except OSError as e:
        # 绝不退化成 unlink：文件被占用时宁可报错，也不能丢存档。
        return JSONResponse(
            {"status": "reset_failed", "exists": True, "restored": False,
             "message": f"存档被占用，无法移出：{e}"},
            status_code=500,
        )
    return {"status": "reset", "exists": False, "restored": True,
            "backup": backup.name}


# --- 生成与锁定（MVP 生成闭环）---

@app.post("/api/generate")
async def generate(payload: dict = Body(...)):
    """调用 ComfyUI 生成一张图，联动预算，保存到项目资产目录"""
    project = payload.get("project") or str(PROJECT_PATH)
    asset_type = payload.get("asset_type")
    asset_name = payload.get("asset_name")
    prompt = payload.get("prompt")
    if not all([asset_type, asset_name, prompt]):
        return JSONResponse(
            {"error": "asset_type, asset_name, prompt 均为必填"}, status_code=400
        )
    args = ["generate", project, asset_type, asset_name, prompt]
    opt = {
        "negative": "--negative",
        "seed": "--seed",
        "steps": "--steps",
        "cfg": "--cfg",
        "width": "--width",
        "height": "--height",
        "cost": "--cost",
        "model": "--model",
    }
    for key, flag in opt.items():
        if payload.get(key) is not None:
            args += [flag, str(payload[key])]
    return JSONResponse(run_tool("comfyui", args, timeout=180))


@app.post("/api/lock")
async def lock_version(payload: dict = Body(...)):
    """将已生成的资产锁定到 K13 版本树（冻结不可修改）"""
    project = payload.get("project") or str(PROJECT_PATH)
    asset_type = payload.get("asset_type")
    asset_name = payload.get("asset_name")
    file_path = payload.get("file_path")
    params_json = payload.get("params_json") or "{}"
    if not all([asset_type, asset_name, file_path]):
        return JSONResponse(
            {"error": "asset_type, asset_name, file_path 均为必填"}, status_code=400
        )
    return JSONResponse(
        run_tool("k13", ["lock", project, asset_type, asset_name, file_path, params_json])
    )


# ============================================================
# 启动
# ============================================================

def main():
    print(f"CINEAST API Server (FastAPI)")
    print(f"  Project:  {PROJECT_PATH.name}")
    print(f"  Path:     {PROJECT_PATH}")
    print(f"  Web:      {WEB_DIR}")
    print(f"  Python:   {PYTHON}")
    print(f"  Listen:   http://{HOST}:{PORT}")
    print(f"  Pages:    / (showcase)  /workspace (工作台)")
    print(f"  API docs: http://{HOST}:{PORT}/docs")
    print()
    import uvicorn
    uvicorn.run(app, host=HOST, port=PORT, log_level="info")


if __name__ == "__main__":
    main()
