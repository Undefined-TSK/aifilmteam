# -*- coding: utf-8 -*-
"""llm_gateway — AI 影视团队 v2 LLM 统一网关（本地优先 + 云端备选链，纯标准库）

路由决策事实源（K-REV-1，老板 2026-10-03 修订）：
  - docs/02-决策/DECISIONS.md 第十六轮
  - docs/02-决策/16-local-first-key-manifest.md §5.4-5.5
  - runtime/llm_router.json（路由表，本模块只读、绝不改写）

纪律（与路由表 policy 一一对应）：
  1. 本地优先：low_structured / mid_reasoning 档先打 Ollama 本地模型
     （router.local.low_mid_model = qwen3:8b），失败才滑云端链；
     high_deep / vision / embedding 档本地为空，直接走云端链。
  2. 额度滑链（on_quota_error）：HTTP 4xx 且错误码含
     Arrearage / Quota / AllocationQuota / SoldOut / Limit，
     或 message 含"额度" → 判定额度错，自动滑向链内下一个模型；
     其余失败（网络不通 / 5xx / 超时 / 响应解析失败）同样滑链——
     单模型重试 0 次（防卡死），与 policy 链式降级一致。
  3. 切换留痕：每次切换 append 一行 JSON 到
     <v2>/runtime/llm_switch_log.jsonl，字段固定为
     {ts, tier, from_model, to_model, reason, error_code}；
     日志绝不出现密钥（只记模型名/错误码，不记原始 message 全文）。
  4. 密钥只从 runtime/secrets/dashscope.env 进程内读取（INI 风格 KEY=VAL），
     绝不写入任何新文件、日志或返回值。
  5. 推理模型适配（16 号决策 §5.4）：glm-5.3 类模型 content 可能带
     ```json 围栏——parse_json_content() 统一剥围栏后解析；
     max_tokens 默认给足 2048（≥1000），调用方可覆盖。

用法：
  import llm_gateway
  g = llm_gateway.Gateway("low_structured")
  r = g.chat([{"role": "user", "content": "抽取分镜字段..."}], json_mode=True)
  obj = llm_gateway.parse_json_content(r["content"])   # content 可能带围栏
  e = llm_gateway.Gateway("embedding").embed("文本")     # {"embedding": [...], ...}

全部失败抛 GatewayExhausted（对应 policy.after_all_exhausted，由上层报老板）。
"""
import json
import os
import time
import urllib.error
import urllib.request
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
# llm 运行数据（router/secrets/switch_log）落在新根同级的 D:\aifilmteam\runtime
# （2026-10-03 十六轮决策事实源位置）；不用字面量，由 parents[2] 相对推导。
RUNTIME_DIR = Path(__file__).resolve().parents[2] / "runtime"
ROUTER_PATH = RUNTIME_DIR / "llm_router.json"
ENV_PATH = os.path.join(RUNTIME_DIR, "secrets", "dashscope.env")
SWITCH_LOG_PATH = os.path.join(RUNTIME_DIR, "llm_switch_log.jsonl")

VALID_TIERS = ("low_structured", "mid_reasoning", "high_deep", "vision", "embedding")
LOCAL_TIERS = ("low_structured", "mid_reasoning")   # 本地优先档；其余档本地=null
QUOTA_CODE_TOKENS = ("Arrearage", "Quota", "AllocationQuota", "SoldOut", "Limit")
DEFAULT_TIMEOUT = 120.0        # 请求超时默认 120s
DEFAULT_MAX_TOKENS = 2048      # 推理模型（glm-5.3 等）须给足 ≥1000


class GatewayExhausted(Exception):
    """链内所有模型均失败（对应 policy.after_all_exhausted → 上层报老板）。"""


class _HopError(Exception):
    """单跳失败包装：reason（额度错/HTTP错/网络错/解析错）+ 错误码。"""

    def __init__(self, reason, error_code):
        super().__init__(f"{reason}:{error_code}")
        self.reason = reason
        self.error_code = error_code


def _now():
    return time.strftime("%Y-%m-%dT%H:%M:%S", time.localtime())


def _http_post_json(url, headers, payload, timeout):
    """POST JSON 并返回 (status, body_text)。

    HTTPError（4xx/5xx）不抛异常而是返回状态码与响应体，便于滑链判定；
    仅网络级失败（连不上/超时）抛 URLError/OSError/TimeoutError。
    独立为模块级函数，测试可 monkeypatch 注入假响应。
    """
    req = urllib.request.Request(
        url,
        data=json.dumps(payload, ensure_ascii=False).encode("utf-8"),
        headers=headers, method="POST")
    try:
        with urllib.request.urlopen(req, timeout=timeout) as resp:
            return resp.status, resp.read().decode("utf-8", "replace")
    except urllib.error.HTTPError as exc:
        try:
            body = exc.read().decode("utf-8", "replace")
        except Exception:
            body = ""
        return exc.code, body


def _classify_error(status, body_text):
    """分类 HTTP 错误 → (error_code, is_quota)。

    额度错判定（16 号决策 §5.2 老板指令口径）：4xx 且
    错误码含 Arrearage/Quota/AllocationQuota/SoldOut/Limit（大小写不敏感，
    兼容 "arrearage"/"quota_exceeded" 等变体）或 message 含"额度"。
    """
    code, msg = "", body_text[:300]
    try:
        data = json.loads(body_text)
        if isinstance(data, dict):
            err = data.get("error") if isinstance(data.get("error"), dict) else data
            code = str(err.get("code") or "")
            msg = str(err.get("message") or "")
    except ValueError:
        pass
    code_lower = code.lower()
    is_quota = (400 <= status < 500) and (
        any(tok.lower() in code_lower for tok in QUOTA_CODE_TOKENS)
        or ("额度" in msg))
    return code or ("http_%d" % status), is_quota


def parse_json_content(content):
    """剥 ```json 围栏并解析模型输出为 JSON（glm-5.3 类推理模型适配）。

    解析顺序：直接 json.loads → 剥围栏后 loads → 提取首 { 到末 } / [ 到 ] 片段
    → 容错回退（去尾逗号 / ast.literal_eval）→ 全部失败抛 ValueError。
    """
    if content is None:
        raise ValueError("模型 content 为空，无法解析 JSON")
    s = content.strip()
    try:
        return json.loads(s)
    except ValueError:
        pass
    if s.startswith("```"):
        lines = s.splitlines()[1:]            # 去掉 ```json / ``` 行
        while lines and lines[-1].strip().startswith("```"):
            lines.pop()
        s = "\n".join(lines).strip()
        try:
            return json.loads(s)
        except ValueError:
            pass
    candidates = [s]
    for open_ch, close_ch in (("{", "}"), ("[", "]")):
        i, j = s.find(open_ch), s.rfind(close_ch)
        if i != -1 and j > i:
            candidates.append(s[i:j + 1])
    import ast
    import re
    for cand in candidates:
        for repaired in (cand, re.sub(r",\s*([}\]])", r"\1", cand)):
            try:
                return json.loads(repaired)
            except ValueError:
                pass
            try:
                return ast.literal_eval(repaired)
            except (ValueError, SyntaxError):
                pass
    raise ValueError("无法从模型输出解析 JSON（已尝试剥围栏/提取片段/容错回退）")


class Gateway:
    """单档位网关：按 tier 从 router 读链（本地优先 + 云端备选链），滑链调用。"""

    def __init__(self, tier, router_path=ROUTER_PATH, log_path=SWITCH_LOG_PATH,
                 timeout=DEFAULT_TIMEOUT, chain=None):
        """chain 非 None 时整体注入替代链（仅测试用，跳过 router 组链）。"""
        if tier not in VALID_TIERS:
            raise ValueError("tier 必须为 %s 之一，收到: %r" % (VALID_TIERS, tier))
        with open(router_path, encoding="utf-8") as f:
            router = json.load(f)
        self.tier = tier
        self.timeout = timeout
        self.log_path = log_path
        local_cfg = router.get("local", {})
        self.local_endpoint = local_cfg.get("endpoint")
        self.local_model = local_cfg.get("low_mid_model")
        if chain is not None:
            self.chain = [dict(h) for h in chain]
        else:
            self.chain = []
            if tier in LOCAL_TIERS and self.local_model:
                self.chain.append({"provider": "local", "model": self.local_model})
            cloud_chain = (router.get("cloud", {}).get("tiers", {})
                           .get(tier, {}).get("cloud_chain") or [])
            self.chain += [{"provider": "cloud", "model": m} for m in cloud_chain]
        if not self.chain:
            raise ValueError("档位 %s 组链为空（router 配置缺失）" % tier)
        # 密钥只驻进程内存（惰性读取，幂等）
        self._env_loaded = False
        self._api_key = None
        self._cloud_base = None

    # ---------- 密钥与端点（进程内读取，绝不落盘） ----------

    def _load_cloud_env(self):
        """从 runtime/secrets/dashscope.env 读 Key/BaseURL（INI 风格，幂等）。"""
        if self._env_loaded:
            return
        key = base = None
        with open(ENV_PATH, encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                if not line or line.startswith("#") or "=" not in line:
                    continue
                k, _, v = line.partition("=")
                k, v = k.strip(), v.strip()
                if k == "DASHSCOPE_API_KEY":
                    key = v
                elif k == "DASHSCOPE_BASE_URL":
                    base = v
        if not key or not base:
            raise RuntimeError(
                "dashscope.env 缺少 DASHSCOPE_API_KEY / DASHSCOPE_BASE_URL")
        self._api_key, self._cloud_base = key, base
        self._env_loaded = True

    def _hop_url(self, hop, suffix):
        if hop["provider"] == "local":
            return self.local_endpoint.rstrip("/") + "/v1" + suffix
        self._load_cloud_env()
        return self._cloud_base.rstrip("/") + suffix

    def _hop_headers(self, hop):
        headers = {"Content-Type": "application/json"}
        if hop["provider"] == "cloud":
            self._load_cloud_env()
            headers["Authorization"] = "Bearer " + self._api_key
        return headers

    # ---------- 滑链与留痕 ----------

    def _slide(self, fail_idx, reason, error_code, switches):
        """链内滑向下一个模型并 append 一行切换日志（无下一个则抛耗尽）。"""
        if fail_idx + 1 >= len(self.chain):
            raise GatewayExhausted(
                "档位 %s 链内全部模型失败（末跳=%s, reason=%s, code=%s）"
                % (self.tier, self.chain[fail_idx]["model"], reason, error_code))
        rec = {"ts": _now(), "tier": self.tier,
               "from_model": self.chain[fail_idx]["model"],
               "to_model": self.chain[fail_idx + 1]["model"],
               "reason": reason, "error_code": error_code}
        d = os.path.dirname(self.log_path)
        if d:
            os.makedirs(d, exist_ok=True)
        with open(self.log_path, "a", encoding="utf-8") as f:
            f.write(json.dumps(rec, ensure_ascii=False) + "\n")
        switches.append(rec)

    def _run_chain(self, build_payload, suffix, parse_result):
        """沿链逐跳尝试：build_payload(hop)->payload；parse_result(hop, data)->结果。

        单模型失败重试 0 次，直接滑链（防卡死）；额度错/其余失败均滑。
        """
        switches = []
        for i, hop in enumerate(self.chain):
            try:
                if hop["provider"] == "local" and suffix != "/chat/completions":
                    raise _HopError("unsupported", "local_no_%s" % suffix.strip("/"))
                status, body = _http_post_json(
                    self._hop_url(hop, suffix), self._hop_headers(hop),
                    build_payload(hop), self.timeout)
                if status >= 400:
                    code, is_quota = _classify_error(status, body)
                    raise _HopError("quota_error" if is_quota else "http_error", code)
                try:
                    data = json.loads(body)
                except ValueError:
                    raise _HopError("bad_response", "parse_error")
                try:
                    return parse_result(hop, data, switches)
                except _HopError:
                    raise
                except Exception:
                    raise _HopError("bad_response", "parse_error")
            except _HopError as exc:
                # 末跳失败时 _slide() 直接抛 GatewayExhausted（无下一个可滑），
                # 故循环之后天然不可达，无需循环外兜底 raise。
                self._slide(i, exc.reason, exc.error_code, switches)
            except (urllib.error.URLError, OSError, TimeoutError):
                self._slide(i, "request_failed", "network_error", switches)

    # ---------- 对外能力 ----------

    def chat(self, messages, tools=None, max_tokens=DEFAULT_MAX_TOKENS,
             json_mode=False):
        """对话补全：本地优先（low/mid 档）→ 云端链滑降。

        返回 {"content", "model", "provider", "raw", "switches"}；
        json_mode=True 时请求 response_format=json_object（本地 Ollama 与
        云端兼容端点均支持）；content 可能带围栏，用 parse_json_content 解析。
        """
        def build_payload(hop):
            payload = {"model": hop["model"], "messages": messages,
                       "max_tokens": max_tokens}
            if tools:
                payload["tools"] = tools
            if json_mode:
                payload["response_format"] = {"type": "json_object"}
            return payload

        def parse_result(hop, data, switches):
            msg = data["choices"][0]["message"]
            return {"content": msg.get("content"), "model": hop["model"],
                    "provider": hop["provider"], "raw": data,
                    "switches": switches}

        return self._run_chain(build_payload, "/chat/completions", parse_result)

    def embed(self, text):
        """向量化：走 embedding 档云端链（本地优先纪律下云端仅测试用途）。

        返回 {"embedding", "model", "provider", "switches"}。
        """
        def build_payload(hop):
            return {"model": hop["model"], "input": text}

        def parse_result(hop, data, switches):
            return {"embedding": data["data"][0]["embedding"],
                    "model": hop["model"], "provider": hop["provider"],
                    "switches": switches}

        return self._run_chain(build_payload, "/embeddings", parse_result)


if __name__ == "__main__":
    # 轻量观测入口：python llm_gateway.py → 打印各档位组链（不发起调用）
    with open(ROUTER_PATH, encoding="utf-8") as f:
        router = json.load(f)
    print("router=%s policy=%s" % (ROUTER_PATH, router.get("policy", {}).get("default")))
    for tier in VALID_TIERS:
        g = Gateway(tier)
        print("%-16s -> %s" % (tier, " | ".join(
            "%s:%s" % (h["provider"], h["model"]) for h in g.chain)))
