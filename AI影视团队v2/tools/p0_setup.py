# -*- coding: utf-8 -*-
"""p0_setup.py — P-0 环境准备：Blender 便携版 + Wan 控制模型权重（只写工作区内）

纪律：
- 每个下载任务先做**目录/API 探测**（不靠我猜文件名），拿到真实 URL 与字节数才下；
- 断点续传写 .part，完成后 os.replace；大小不足视为失败并记 status=too_small；
- 全部结果写 logs/p0_setup_state.json，可回读（脚本自身不做删除）；
- --probe 只探测不下载，用来先确认源可用。
"""
import argparse
import hashlib
import json
import os
import re
import sys
import time
import urllib.request
import zipfile
from pathlib import Path

sys.stdout.reconfigure(encoding="utf-8", errors="replace")
ROOT = Path(__file__).resolve().parents[1]
BLENDER = ROOT / "blender"
MODELS = ROOT / "models"
STATE = ROOT / "logs" / "p0_setup_state.json"
NJU = "https://mirrors.nju.edu.cn/blender/release/"
HF = "https://hf-mirror.com"
UA = {"User-Agent": "curl/8.6", "Accept": "*/*"}
REPO = HF + "/Comfy-Org/Wan_2.1_ComfyUI_repackaged/resolve/main/"

# 本轮只下"能验证白模驱动"的最小集（~3.4GB）；其余同仓库文件列为延后项并写进状态文件，不静默丢弃
WANT = {
    "vace_1.3b": ("diffusion_models", "wan2.1_vace_1.3B_preview_fp16.safetensors", 1_000_000_000),
    "vae_wan21": ("vae", "wan_2.1_vae.safetensors", 100_000_000),
    "taehv": ("vae", "taehv_032b.safetensors", 5_000_000),
}
DEFERRED = {
    "fun_control_1.3b": "wan2.1_fun_control_1.3B_bf16.safetensors（与 VACE 重叠，先验证 VACE 再决定）",
    "t2v_1.3b": "wan2.1_t2v_1.3B_fp16.safetensors（纯文生视频，本项目不用）",
    "h3_14b": "MiniMax H3 本地=135GiB 分片 + 需 ~200GB 内存，本机 15GB 不可行（一手：ComfyUI 教程/仓库）",
    "ltx_2.3": "官方前置 32GB+ 显存；本机 12GB 无官方口径 → 待自测后再定",
}


def fetch(url, binary=False, timeout=60):
    req = urllib.request.Request(url, headers=UA)
    with urllib.request.urlopen(req, timeout=timeout) as r:
        data = r.read()
    return data if binary else data.decode("utf-8", "replace")


def size_of(url):
    """跟随重定向拿真实 Content-Length（hf-mirror 会 302 到 xet 域）。"""
    try:
        req = urllib.request.Request(url, headers=UA, method="GET")
        with urllib.request.urlopen(req, timeout=60) as r:
            cl = r.headers.get("Content-Length")
            r.read(1 << 16)
        return int(cl) if cl else None
    except Exception as e:
        return {"err": f"{type(e).__name__}:{str(e)[:110]}"}


def sha(path, limit=1 << 27):
    h = hashlib.sha256()
    with open(path, "rb") as f:
        got = 0
        while True:
            b = f.read(1 << 22)
            if not b:
                break
            h.update(b)
            got += len(b)
            if got > limit:
                break
    return h.hexdigest()[:12]


def probe_blender():
    """解析南大镜像目录，列出 5.x Windows 便携 zip 的真实文件名与大小。"""
    out = []
    for ver in ("5.2", "5.1", "5.0"):
        try:
            html = fetch(NJU + "Blender" + ver + "/")
        except Exception as e:
            out.append({"dir": ver, "err": type(e).__name__})
            continue
        names = re.findall(r'href="([^"]*windows[^"]*\.zip)"', html, re.I)
        for n in sorted(set(names)):
            url = NJU + "Blender" + ver + "/" + n
            out.append({"dir": ver, "file": n, "url": url, "bytes": size_of(url)})
    return out


def probe_weights():
    out = {}
    for key, (sub, fn, minb) in WANT.items():
        url = REPO + "split_files/" + sub + "/" + fn + "?download=true"
        out[key] = {"url": url, "bytes": size_of(url), "min": minb}
    return out


def download(url, dest, minb, tag, log):
    os.makedirs(os.path.dirname(dest), exist_ok=True)
    rec = {"tag": tag, "dest": os.path.relpath(dest, ROOT).replace("\\", "/"), "url": url}
    if os.path.exists(dest) and os.path.getsize(dest) >= minb:
        rec.update(status="skip_exists", bytes=os.path.getsize(dest), sha12=sha(dest))
        log.append(rec)
        return
    part = dest + ".part"
    start = os.path.getsize(part) if os.path.exists(part) else 0
    t0 = time.time()
    try:
        req = urllib.request.Request(url, headers=dict(UA, Range="bytes=%d-" % start))
        with urllib.request.urlopen(req, timeout=180) as r, open(part, "ab") as f:
            code = getattr(r, "status", 200)
            while True:
                b = r.read(1 << 22)
                if not b:
                    break
                f.write(b)
        n = os.path.getsize(part)
        if n < minb:
            rec.update(status="too_small", bytes=n, http=code)
        else:
            os.replace(part, dest)
            rec.update(status="ok", bytes=n, http=code, sha12=sha(dest),
                       mbps=round(n / 2**20 / max(1, time.time() - t0), 1))
    except Exception as e:
        rec.update(status="err", err=f"{type(e).__name__}:{str(e)[:140]}",
                   partial=os.path.getsize(part) if os.path.exists(part) else 0)
    log.append(rec)
    json.dump({"ts": time.strftime("%F %T"), "records": log}, open(STATE, "w", encoding="utf-8"),
              ensure_ascii=False, indent=1)
    print(json.dumps(rec, ensure_ascii=False), flush=True)


def unzip_blender(zip_path, log):
    name = os.path.basename(zip_path)[:-4]
    tgt = os.path.join(BLENDER, name)
    if os.path.isdir(tgt):
        return {"tag": "extract", "status": "skip_exists", "to": tgt}
    try:
        with zipfile.ZipFile(zip_path) as z:
            n = len(z.namelist())
            z.extractall(BLENDER)
        exe = None
        for root_, _, fs in os.walk(tgt):
            if "blender.exe" in fs:
                exe = os.path.join(root_, "blender.exe")
                break
        return {"tag": "extract", "status": "ok", "entries": n, "to": tgt, "blender_exe": exe}
    except Exception as e:
        return {"tag": "extract", "status": "err", "err": str(e)[:160]}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--probe", action="store_true")
    ap.add_argument("--go", action="store_true")
    a = ap.parse_args()
    if a.probe:
        res = {"blender": probe_blender(), "weights": probe_weights()}
        json.dump(res, open(os.path.join(ROOT, "logs", "p0_probe.json"), "w", encoding="utf-8"),
                  ensure_ascii=False, indent=1)
        print(json.dumps(res, ensure_ascii=False, indent=1)[:2400])
        return 0
    if not a.go:
        print("需要 --probe 或 --go")
        return 2
    log = []
    bz = None
    cands = [b for b in probe_blender()
             if "-windows-x64" in b.get("file", "") and isinstance(b.get("bytes"), int) and b["bytes"] > 5_000_000]
    cands.sort(key=lambda x: x["file"], reverse=True)   # 取最新补丁版，绝不挑 arm64
    bz = cands[0] if cands else None
    if bz:
        download(bz["url"], os.path.join(BLENDER, bz["file"]), 5_000_000, "blender_zip", log)
        got = [r for r in log if r["status"] in ("ok", "skip_exists")]
        if got:
            log.append(unzip_blender(os.path.join(BLENDER, bz["file"]), []))
    else:
        log.append({"tag": "blender_zip", "status": "not_found_in_mirror"})
    log.append({"tag": "deferred", "status": "not_downloaded_by_decision", "detail": DEFERRED})
    for key, (sub, fn, minb) in WANT.items():
        download(REPO + "split_files/" + sub + "/" + fn + "?download=true",
                 os.path.join(MODELS, sub, fn), minb, key, log)
    json.dump({"ts": time.strftime("%F %T"), "records": log}, open(STATE, "w", encoding="utf-8"),
              ensure_ascii=False, indent=1)
    ok = sum(1 for r in log if r.get("status") in ("ok", "skip_exists"))
    print(f"\n完成 {ok}/{len(log)} 项，状态见 logs/p0_setup_state.json")
    return 0


if __name__ == "__main__":
    sys.exit(main())

