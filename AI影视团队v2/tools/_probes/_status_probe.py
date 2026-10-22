"""只读状态探针：列出工程件是否存在、行数、素材数量。不改任何文件。"""
import json, os, subprocess, sys
sys.stdout.reconfigure(encoding="utf-8", errors="replace")
R = r"D:\ai_film_projects"

FILES = {
    "qc_media": r"tools\qc_media.py",
    "jobs": r"tools\jobs.py",
    "dit_ingest": r"tools\dit_ingest.py",
    "track_contract": r"pipeline\contracts\track_contract.v1.json",
    "validator": r"pipeline\contracts\validate_tracks.py",
    "clock": r"pipeline\clock.py",
    "blender_engine": r"pipeline\blender_engine.py",
    "holographic": r"docs\AI交接全息文档.md",
    "audit_v6": r"docs\阶段0体检审计报告与规划修订v6.0.md",
    "shotlist_v1": r"projects\雨夜寻猫\storyboard\雨夜寻猫_镜头清单_v1.md",
    "pending_mem": r"logs\_mem_mirror\PENDING_MEMORY_APPENDS.md",
    "director_intent": r"projects\雨夜寻猫\director_intent.md",
}
DIRS = {
    "pipeline_dir": "pipeline",
    "blender_dir": "blender",
    "shots_json": r"pipeline\shots",
    "dialogue": r"projects\雨夜寻猫\audio\dialogue",
    "ambient": r"projects\雨夜寻猫\audio\ambient",
    "bgm": r"projects\雨夜寻猫\audio\bgm",
    "sfx": r"projects\雨夜寻猫\audio\sfx",
    "output": r"projects\雨夜寻猫\output",
    "assets_png": r"projects\雨夜寻猫\assets",
}
out = {"files": {}, "dirs": {}}
for k, rel in FILES.items():
    p = os.path.join(R, rel)
    ok = os.path.isfile(p)
    lines = 0
    if ok:
        try:
            lines = sum(1 for _ in open(p, "rb"))
        except Exception:
            lines = -1
    out["files"][k] = {"exists": ok, "lines": lines, "path": rel}
exts = (".wav", ".mp3", ".flac", ".mp4", ".png", ".jpg", ".json")
for k, rel in DIRS.items():
    p = os.path.join(R, rel)
    if os.path.isdir(p):
        fs = [f for f in os.listdir(p) if os.path.splitext(f)[1].lower() in exts]
        out["dirs"][k] = {"exists": True, "count": len(fs), "sample": sorted(fs)[:8]}
    else:
        out["dirs"][k] = {"exists": False}
g = subprocess.run("git status --porcelain", shell=True, cwd=R,
                   capture_output=True, text=True, encoding="utf-8", errors="replace")
out["git_dirty"] = len([x for x in (g.stdout or "").splitlines() if x.strip()])
m = subprocess.run("wmic ComputerSystem get TotalPhysicalMemory", shell=True,
                   capture_output=True, text=True, encoding="utf-8", errors="replace")
vals = [x for x in (m.stdout or "").splitlines() if x.strip().isdigit()]
out["ram_gb"] = round(int(vals[0]) / 2**30) if vals else None
print(json.dumps(out, ensure_ascii=False, indent=1))
