# -*- coding: utf-8 -*-
"""自测客户端：直连 baimo_mcp_addon socket 服务端跑一轮冒烟（断言 1/2 用）。

用法：python selftest_client.py [--ping-only]
"""
import json
import os
import socket
import sys
from pathlib import Path

HOST, PORT = "127.0.0.1", 17800
# 维度25：根路径由文件位置反推（原硬编码 D:/aifilmteam/outputs/...）
ROOT = Path(__file__).resolve().parents[2]
PREVIEW = str(ROOT / "outputs" / "mcp_pilot" / "selftest_preview.png").replace("\\", "/")


def rpc(sock, method, params=None, rid=1, timeout=120):
    sock.settimeout(timeout)
    msg = json.dumps({"jsonrpc": "2.0", "id": rid, "method": method,
                      "params": params or {}}).encode("utf-8")
    sock.sendall(msg + b"\n")
    buf = b""
    while b"\n" not in buf:
        chunk = sock.recv(65536)
        if not chunk:
            raise ConnectionError("连接被关闭")
        buf += chunk
    line, _ = buf.split(b"\n", 1)
    resp = json.loads(line.decode("utf-8"))
    return resp


def main():
    ping_only = "--ping-only" in sys.argv
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.connect((HOST, PORT))
    r = rpc(s, "ping", rid=1)
    print("PING:", json.dumps(r, ensure_ascii=False)[:200])
    if ping_only:
        return 0 if "result" in r else 1
    r = rpc(s, "scene_state", rid=2)
    n = len(r.get("result", {}).get("objects", [])) if "result" in r else -1
    print("SCENE_STATE: objects=%d" % n)
    r = rpc(s, "create_primitive", {"kind": "cube", "size": 2,
                                    "location": [0, 0, 1], "name": "test_cube"},
            rid=3)
    print("CREATE:", json.dumps(r, ensure_ascii=False)[:200])
    r = rpc(s, "add_camera", {"name": "test_cam", "lens": 50,
                              "location": [0, -6, 1.5], "aim": [0, 0, 1]}, rid=4)
    print("CAMERA:", json.dumps(r, ensure_ascii=False)[:200])
    r = rpc(s, "add_light", {"kind": "SUN", "energy": 3, "name": "test_sun"}, rid=5)
    print("LIGHT:", json.dumps(r, ensure_ascii=False)[:200])
    r = rpc(s, "render_preview", {"camera": "test_cam",
                                  "output_path": PREVIEW},
            rid=6, timeout=300)
    print("RENDER_PREVIEW:", json.dumps(r, ensure_ascii=False)[:300])
    ok = all('"error"' not in json.dumps(x) for x in
             [r]) and "result" in r
    print("SELFTEST", "PASS" if ok else "FAIL")
    return 0 if ok else 1


if __name__ == "__main__":
    sys.exit(main())
