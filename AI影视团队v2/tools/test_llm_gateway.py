# -*- coding: utf-8 -*-
"""test_llm_gateway — llm_gateway 四项自测（真实调用，不 mock 本地/云端真链路）

① 本地 chat 一发（真实调用 Ollama qwen3:8b，断言 provider=local 本地优先成立）
② 本地 structured（json_mode）一发（断言可解析且字段命中）
③ embedding 档走云端 text-embedding-v4 一发（消耗免费额度，可接受）
④ 伪造额度错误场景（monkeypatch _http_post_json + 注入假链）验证滑链与日志落盘，
   并断言日志无密钥泄漏。

运行：python test_llm_gateway.py   （退出码 0=全 PASS，1=有 FAIL）
"""
import json
import os
import sys
import tempfile

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import llm_gateway as gw

results = []


def record(name, ok, detail):
    results.append((name, ok))
    print("[%s] %s — %s" % ("PASS" if ok else "FAIL", name, detail))


# ---------- T1 本地 chat（真实 Ollama qwen3:8b） ----------
try:
    g1 = gw.Gateway("mid_reasoning")
    r1 = g1.chat([{"role": "user", "content": "用一句话回答：你是哪个模型？"}],
                 max_tokens=200)
    ok1 = bool((r1["content"] or "").strip()) and r1["provider"] == "local" \
        and r1["model"] == g1.local_model
    record("T1 本地chat(ollama qwen3:8b)", ok1,
           "provider=%s model=%s content=%r" % (
               r1["provider"], r1["model"], (r1["content"] or "")[:60]))
except Exception as exc:
    record("T1 本地chat(ollama qwen3:8b)", False, "异常: %r" % exc)

# ---------- T2 本地 structured（json_mode） ----------
try:
    g2 = gw.Gateway("low_structured")
    r2 = g2.chat([{"role": "user", "content":
                   "从这句话抽取分镜字段并只输出JSON：第3场，全景镜头，时长4秒。"
                   "字段: scene(int), shot(str), duration_s(int)"}],
                 json_mode=True, max_tokens=500)
except Exception as exc:
    record("T2 本地structured(json_mode+剥围栏解析)", False, "调用异常: %r" % exc)
else:
    try:
        obj = gw.parse_json_content(r2["content"])
        ok2 = r2["provider"] == "local" and obj.get("scene") == 3 \
            and obj.get("duration_s") == 4
        record("T2 本地structured(json_mode+剥围栏解析)", ok2,
               "provider=%s 解析=%s" % (
                   r2["provider"], json.dumps(obj, ensure_ascii=False)[:120]))
    except Exception as exc:
        record("T2 本地structured(json_mode+剥围栏解析)", False,
               "解析异常: %r content=%r" % (exc, (r2.get("content") or "")[:300]))

# ---------- T3 embedding 档走云端 text-embedding-v4 ----------
try:
    g3 = gw.Gateway("embedding")
    r3 = g3.embed("AI影视团队v2 llm_gateway 自测向量")
    dim = len(r3["embedding"])
    ok3 = dim > 0 and r3["model"] == "text-embedding-v4"
    record("T3 embedding云端text-embedding-v4", ok3,
           "model=%s dim=%d switches=%d" % (r3["model"], dim, len(r3["switches"])))
except Exception as exc:
    record("T3 embedding云端text-embedding-v4", False, "异常: %r" % exc)

# ---------- T4 伪造额度错 → 滑链 + 日志落盘 + 无密钥泄漏 ----------
try:
    tmpdir = tempfile.mkdtemp(prefix="llm_gw_test_")
    tmplog = os.path.join(tmpdir, "switch_log.jsonl")
    g4 = gw.Gateway("low_structured",
                    chain=[{"provider": "cloud", "model": "fake-model-a"},
                           {"provider": "cloud", "model": "fake-model-b"}],
                    log_path=tmplog)
    called = []

    def fake_post(url, headers, payload, timeout):
        called.append(payload.get("model"))
        if payload.get("model") == "fake-model-a":
            return 429, json.dumps(
                {"error": {"code": "Arrearage",
                           "message": "Model quota exhausted, 额度已用尽"}})
        return 200, json.dumps({"choices": [{"message": {"content": "{\"ok\": true}"}}],
                                "usage": {"total_tokens": 1}})

    orig_post = gw._http_post_json
    gw._http_post_json = fake_post
    try:
        r4 = g4.chat([{"role": "user", "content": "hi"}])
    finally:
        gw._http_post_json = orig_post
    with open(tmplog, encoding="utf-8") as f:
        log_lines = [json.loads(l) for l in f if l.strip()]
    ok4 = (r4["model"] == "fake-model-b" and len(r4["switches"]) == 1
           and len(log_lines) == 1)
    rec = log_lines[0] if log_lines else {}
    ok4 = ok4 and rec.get("from_model") == "fake-model-a" \
        and rec.get("to_model") == "fake-model-b" \
        and rec.get("reason") == "quota_error" \
        and rec.get("error_code") == "Arrearage" \
        and rec.get("tier") == "low_structured" and bool(rec.get("ts"))
    # 密钥绝不落日志：取 env 中真实 Key 值反查日志全文
    with open(gw.ENV_PATH, encoding="utf-8") as f:
        env_lines = [l.strip() for l in f if l.startswith("DASHSCOPE_API_KEY=")]
    key_val = env_lines[0].split("=", 1)[1].strip() if env_lines else ""
    with open(tmplog, encoding="utf-8") as f:
        log_text = f.read()
    no_leak = bool(key_val) and key_val not in log_text
    ok4 = ok4 and no_leak
    record("T4 伪造额度错滑链+日志落盘+无密钥泄漏", ok4,
           "调用序=%s 切换记录=%s 无泄漏=%s" % (
               called, json.dumps(rec, ensure_ascii=False), no_leak))
except Exception as exc:
    record("T4 伪造额度错滑链+日志落盘+无密钥泄漏", False, "异常: %r" % exc)

fails = [n for n, ok in results if not ok]
print("\n=== 自测汇总: %d/%d PASS ===" % (len(results) - len(fails), len(results)))
if fails:
    print("FAIL 项: %s" % ", ".join(fails))
sys.exit(1 if fails else 0)
