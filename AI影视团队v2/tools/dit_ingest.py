# -*- coding: utf-8 -*-
"""dit_ingest.py — 素材血缘账本（DIT 职能脚本化，不新增岗位）

为什么先做它：质检想用像素判据区分"静图"与"真动"已被标定实验否证
（18 镜 4 判据最佳仅 16/18，且 Ken Burns 静图镜的读数高于真动效镜）。
所以静图/真动一律走**溯源**：这一镜有没有视频源、由哪个模型哪个 seed 产出、
被谁引用过。判例已认"流程记录=确权证据"（湖北首例 AI 短剧案，2026-09）。

产物（全部写在 projects/<片>/ditmap/ 下）：
  file_index.jsonl  每个素材一行：sha256/bytes/mtime/kind/是否被引用
  lineage.jsonl     每个镜头一行：kind=video|blockout|flat_move|still_fallback|missing
                    + engine/seed/refs/参数/ QC 引用
  summary.json      体检汇总（真动比例、坏引用、0 字节、孤儿、可交付镜数）
  unverified.jsonl  只有 sha 没 sha 对齐的（--verify 用）

CLI:
  python tools/dit_ingest.py                       # 重建账本（默认《雨夜寻猫》）
  python tools/dit_ingest.py --project 雨夜寻猫 --verify   # 校验 sha 是否被改动
"""
import argparse
import hashlib
import json
import os
import sys
import time
from pathlib import Path

sys.stdout.reconfigure(encoding="utf-8", errors="replace")

ROOT = Path(__file__).resolve().parents[1]
MEDIA_EXT = {".png", ".jpg", ".jpeg", ".mp4", ".mov", ".webm", ".wav", ".mp3", ".flac", ".srt"}
IGNORE_DIRS = {"_qc_tmp", "mix_tmp", "__pycache__", ".git"}


def sha256(path, block=1 << 24):
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for b in iter(lambda: f.read(block), b""):
            h.update(b)
    return h.hexdigest()


def rel(p, proj):
    return os.path.relpath(p, os.path.join(ROOT, "projects", proj)).replace("\\", "/")


def walk_index(proj):
    base = os.path.join(ROOT, "projects", proj)
    idx = {}
    for dirpath, dirnames, filenames in os.walk(base):
        dirnames[:] = [d for d in dirnames if d not in IGNORE_DIRS]
        for fn in filenames:
            ext = os.path.splitext(fn)[1].lower()
            if ext not in MEDIA_EXT:
                continue
            p = os.path.join(dirpath, fn)
            try:
                st = os.stat(p)
            except OSError:
                continue
            r = rel(p, proj)
            idx[r] = {"path": r, "bytes": st.st_size,
                      "mtime": time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(st.st_mtime)),
                      "kind_by_ext": "video" if ext in {".mp4", ".mov", ".webm"} else
                                     ("audio" if ext in {".wav", ".mp3", ".flac"} else
                                      ("subtitle" if ext == ".srt" else "image")),
                      "sha256": sha256(p) if st.st_size else None,
                      "zero_byte": st.st_size == 0}
    return idx


def load_json(path):
    if not os.path.exists(path):
        return None
    try:
        return json.load(open(path, encoding="utf-8"))
    except Exception as e:
        return {"_load_error": str(e)[:120]}


def shots_of(proj):
    """读镜头清单真结构：{shots:[{shot_no,timecode,shot_type,camera_move,spec_duration_sec,
    status,status_label,file,note}]}。返回 (rows, src_ok)。
    v2 布局：清单在 00_brief/shots/（2026-10-05 结构漂移修正）。"""
    d = os.path.join(ROOT, "projects", proj, "00_brief", "shots")
    fp = None
    for fn in sorted(os.listdir(d)) if os.path.isdir(d) else []:
        if fn.endswith(".json") and "shots_map" not in fn and "镜头清单" in fn:
            fp = os.path.join(d, fn)
            break
    if not fp:
        return [], False
    data = load_json(fp)
    rows = data.get("shots") if isinstance(data, dict) else None
    out = []
    for r in rows or []:
        out.append({"shot_id": r.get("shot_no"), "timecode": r.get("timecode"),
                    "declared_clip": (r.get("file") or "").strip() or None,
                    "status": r.get("status"), "status_text": (r.get("status_label") or ""),
                    "shot_size": r.get("shot_type"), "motion": r.get("camera_move"),
                    "dur_table_s": r.get("spec_duration_sec"), "note": r.get("note")})
    return out, True


def storyboard_refs(proj):
    """读分镜表 reference_image → {shot_no: 参考图相对路径}。
    降级镜血缘闭环：静帧回退镜必须记录'退回依赖的素材是谁'，不许只标降级不标来源。"""
    base = os.path.join(ROOT, "projects", proj)
    fp = None
    for root, _dirs, files in os.walk(os.path.join(base, "00_brief")):
        for fn in files:
            if fn.endswith(".json") and "分镜表" in fn:
                fp = os.path.join(root, fn)
                break
        if fp:
            break
    if not fp:
        return {}
    data = load_json(fp)
    out = {}
    for sc in (data or {}).get("scenes") or []:
        for s in sc.get("shots") or []:
            ref = (s.get("reference_image") or "").strip()
            out[s.get("shot_no")] = os.path.normpath(ref).replace("\\", "/") if ref else None
    return out


def classify(shot, index, ref_image):
    """kind 由**溯源**决定，不看像素。ref_image = 分镜表 reference_image 相对路径（可 None）。"""
    clip = shot.get("declared_clip")
    hit = None
    if clip:
        base = os.path.basename(clip)
        cands = [p for p in index if os.path.basename(p) == base]
        if cands and not index[cands[0]]["zero_byte"] and index[cands[0]]["kind_by_ext"] == "video":
            hit = cands[0]
    ref = None
    if ref_image:
        r = os.path.normpath(ref_image).replace("\\", "/")
        if r in index:
            ref = {"image": r, "sha256": index[r]["sha256"],
                   "zero_byte": index[r]["zero_byte"]}
        else:
            ref = {"image": r, "sha256": None,
                   "zero_byte": None, "missing_in_project": True}
    if hit:
        eng = "wan2.2" if "wan22" in hit.lower() else ("animatediff" if "_i2v" in hit.lower() else "engine")
        return {"kind": "video", "clip": hit, "engine": eng,
                "clip_sha256": index[hit]["sha256"], "clip_bytes": index[hit]["bytes"],
                "ref_image": ref}
    st = (shot.get("status") or "") + (shot.get("status_text") or "")
    if "degraded" in st or "降级" in st or "Ken Burns" in st:
        return {"kind": "still_fallback", "clip": None, "engine": "ffmpeg_pan_zoom",
                "warning": "静帧+剪辑层推拉：PPT 感受体来源，禁进交付时间线",
                "ref_image": ref}
    if "dynamic" in st or "动态" in st:
        return {"kind": "video", "clip": None, "engine": None,
                "warning": "清单声明动态但无可用视频源，打回补拍", "ref_image": ref}
    if "missing" in st or "缺失" in st:
        return {"kind": "missing", "clip": None, "engine": None, "ref_image": ref}
    return {"kind": "undetermined", "clip": None, "engine": None,
            "warning": "状态无法分类，需人工补标后才可排产", "ref_image": ref}


def refs_from_locks(proj):
    """character_lock/scene_lock + K13 版本树 → 谁引用了哪些素材（含 sha 校验）
    v2 布局：锁文件在 locks/ 下（2026-10-05 结构漂移修正）。"""
    base = os.path.join(ROOT, "projects", proj)
    refs, broken = {}, []
    for sub in ("character_lock", "scene_lock"):
        d = os.path.join(base, "locks", sub)
        for fn in sorted(os.listdir(d)) if os.path.isdir(d) else []:
            if not fn.endswith(".json"):
                continue
            data = load_json(os.path.join(d, fn)) or {}
            blob = json.dumps(data, ensure_ascii=False)
            for k, v in index_cache.items():
                if os.path.basename(k) in blob:
                    refs.setdefault(k, []).append(f"{sub}/{fn}")
    ver = load_json(os.path.join(base, "locks", "k13_locked", "versions.json"))
    if isinstance(ver, dict):
        for it in ver.get("versions") or []:
            fp = it.get("file_path") or ""
            tag = "k13/" + str(it.get("uuid"))
            if not fp:
                continue
            key = os.path.basename(fp)
            hit = [k for k in index_cache if os.path.basename(k) == key]
            if hit:
                refs.setdefault(hit[0], []).append(tag)
            # 版本树 file_path 是旧根绝对路径（v1 遗留）；归一为 v2 相对路径再校验，
            # 旧绝对路径保留在 legacy_path 供审计。
            asset_ref = hit[0] if hit else fp
            probe = os.path.join(base, hit[0]) if hit else fp
            exists = os.path.isfile(probe)
            size = os.path.getsize(probe) if exists else -1
            extra = {"legacy_path": fp} if fp != asset_ref else {}
            if not exists:
                broken.append({"asset": asset_ref, "referenced_by": tag,
                               "why": "版本树引用但文件不存在", **extra})
            elif size < 1000:
                broken.append({"asset": asset_ref, "referenced_by": tag,
                               "why": f"文件仅 {size} 字节（坏产物仍被锁定引用）",
                               "params_seed": (it.get("params") or {}).get("seed"), **extra})
    return refs, broken


index_cache = {}


def main():
    global index_cache
    ap = argparse.ArgumentParser()
    ap.add_argument("--project", default="雨夜寻猫")
    ap.add_argument("--verify", action="store_true")
    a = ap.parse_args()
    proj = a.project
    base = os.path.join(ROOT, "projects", proj)
    out = os.path.join(base, "ditmap")
    os.makedirs(out, exist_ok=True)
    index_cache = index = walk_index(proj)
    shots, has_json = shots_of(proj)
    refs_map = storyboard_refs(proj)

    refs, broken = refs_from_locks(proj)

    lines, kin = [], {}
    for s in shots:
        c = classify(s, index, refs_map.get(s.get("shot_id")))
        k = c["kind"]
        kin[k] = kin.get(k, 0) + 1
        rec = dict(s)
        rec.update(c)
        lines.append(rec)
    vid = kin.get("video", 0)
    tot = max(1, len(lines))

    with open(os.path.join(out, "file_index.jsonl"), "w", encoding="utf-8") as f:
        for p, v in sorted(index.items()):
            o = dict(v)
            o["referenced_by"] = refs.get(p, [])
            f.write(json.dumps(o, ensure_ascii=False) + "\n")
    with open(os.path.join(out, "lineage.jsonl"), "w", encoding="utf-8") as f:
        for r in lines:
            f.write(json.dumps(r, ensure_ascii=False) + "\n")

    zero = [p for p, v in index.items() if v["zero_byte"]]
    orphans = [p for p, v in index.items() if not refs.get(p) and v["kind_by_ext"] != "subtitle"
               and "/output/" not in p and "/_check" not in p]
    sf = [r for r in lines if r.get("kind") == "still_fallback"]
    ref_missing = [r["shot_id"] for r in sf
                   if (r.get("ref_image") or {}).get("missing_in_project")]
    summ = {"project": proj, "generated_at": time.strftime("%Y-%m-%d %H:%M:%S"),
           "src_json": has_json, "media_files": len(index),
            "media_by_type": {t: sum(1 for v in index.values() if v["kind_by_ext"] == t)
                              for t in ("image", "video", "audio")},
            "shots": len(lines), "shot_kind": kin,
            "dynamic_ratio_by_provenance": round(vid / tot, 3),
            "deliverable_shots": vid,
            "still_fallback_ref_image": {
                "with_ref": sum(1 for r in sf if r.get("ref_image")),
                "without_ref": sum(1 for r in sf if not r.get("ref_image")),
                "ref_missing_in_project": ref_missing},
            "zero_byte_assets": zero, "broken_references": broken,
            "unreferenced_assets": len(orphans),
            "audio_stems_present": bool([p for p in index if p.startswith("audio/dialogue")]),
            "integrity_flags": ({"zero_byte": len(zero), "broken_refs": len(broken),
                                 "non_video_shots": kin.get("still_fallback", 0) + kin.get("missing", 0)},
                                "注：本文件只记事实与完整性标志；PASS/FAIL 交付判定属 tools/qc_media.py（技术门）")
}
    json.dump(summ, open(os.path.join(out, "summary.json"), "w", encoding="utf-8"), ensure_ascii=False, indent=1)

    if a.verify:
        bad = []
        for p, v in index.items():
            if v["zero_byte"]:
                continue
            try:
                cur = sha256(os.path.join(base, p))
            except OSError:
                cur = None
            if cur != v["sha256"]:
                bad.append({"path": p, "was": v["sha256"], "now": cur})
        json.dump(bad, open(os.path.join(out, "unverified.jsonl"), "w", encoding="utf-8"),
                  ensure_ascii=False, indent=1)
        summ["verify_mismatch"] = len(bad)

    print(f"血缘账本 → projects/{proj}/ditmap/  （素材 {len(index)} 个 / 镜头 {len(lines)} 条 / 清单JSON={has_json}）")
    print("镜头溯源分类：", kin, "→ 真动比例(按溯源) = %.1f%%" % (vid / tot * 100))
    print("降级镜参考图血缘：有源 %d / 无源 %d / 源缺失 %s" % (
        summ["still_fallback_ref_image"]["with_ref"],
        summ["still_fallback_ref_image"]["without_ref"],
        summ["still_fallback_ref_image"]["ref_missing_in_project"] or "无"))
    print("0 字节素材：", len(zero), zero[:6])
    print("坏引用：", len(broken), [b["asset"] for b in broken[:6]])
    print("无引用孤儿：", len(orphans))
    print("完整性标志：", summ["integrity_flags"], "（交付判定由 qc_media 出）")
    return 0


if __name__ == "__main__":
    sys.exit(main())

