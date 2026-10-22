# -*- coding: utf-8 -*-
"""config/config_loader.py — 统一配置加载与校验（维度33 配置管理）

职责：
1. 加载 config/settings.yaml（唯一配置源）；
2. 支持环境变量覆盖（前缀 AI_FILM_，双下划线分层，如 AI_FILM_PORTS__OLLAMA=11435）；
3. 启动时校验必填项与合法范围，缺失/越界即抛 ConfigError（fail-fast，不静默回落）。

设计纪律（对齐老板铁律「报已测必须给回显」「反补丁式修补」）：
- 只读配置，不写配置；不改变任何现有脚本行为（纯新增，现役脚本按需逐步接入）；
- 阈值类配置以 spec/ 为唯一事实来源，本模块只做镜像校验，冲突时以 spec 为准。
"""
from __future__ import annotations

import os
from pathlib import Path
from typing import Any

import yaml

ROOT = Path(__file__).resolve().parents[1]
SETTINGS_PATH = Path(__file__).resolve().parent / "settings.yaml"
ENV_PREFIX = "AI_FILM_"


class ConfigError(Exception):
    """配置缺失或非法。"""


# 校验规则：点分路径 -> (类型, 合法范围/枚举)
_RULES: dict[str, tuple[type, Any]] = {
    "app.env": (str, ("development", "staging", "production")),
    "ports.blender_addon": (int, (1, 65535)),
    "ports.ollama": (int, (1, 65535)),
    "ports.api_server": (int, (1, 65535)),
    "ports.comfyui": (int, (1, 65535)),
    "vram_lock.ttl_seconds": (int, (1, 86400)),
    "vram_lock.heartbeat_seconds": (int, (1, 3600)),
    "vram_lock.poll_seconds": (int, (1, 300)),
    "qc.motion_px_per_frame_min": (float, (0.0, 100.0)),
    "qc.arcface_similarity_min": (float, (0.0, 1.0)),
    "qc.sync_c_min": (float, (0.0, 100.0)),
    "budget.r5_total_cny": (float, (0.0, 100000.0)),
    "budget.warn_ratio": (float, (0.0, 1.0)),
    "budget.halt_ratio": (float, (0.0, 2.0)),
    "models.ollama_llm": (str, None),
    "models.vace_dir": (str, None),
}


def _dig(data: dict, dotted: str) -> Any:
    cur: Any = data
    for part in dotted.split("."):
        if not isinstance(cur, dict) or part not in cur:
            raise ConfigError(f"缺少必填配置项：{dotted}")
        cur = cur[part]
    return cur


def _coerce(value: str, typ: type) -> Any:
    if typ is float:
        return float(value)
    if typ is int:
        return int(value)
    return value


def _apply_env_override(data: dict) -> dict:
    """AI_FILM_PORTS__OLLAMA=11435 → data['ports']['ollama']=11435（保留 YAML 原类型）。"""
    for key, raw in os.environ.items():
        if not key.startswith(ENV_PREFIX):
            continue
        path = key[len(ENV_PREFIX):].lower().split("__")
        cur = data
        for part in path[:-1]:
            cur = cur.setdefault(part, {})
        cur[path[-1]] = raw
    return data


def load() -> dict:
    if not SETTINGS_PATH.exists():
        raise ConfigError(f"配置文件不存在：{SETTINGS_PATH}")
    with SETTINGS_PATH.open("r", encoding="utf-8") as fh:
        data = yaml.safe_load(fh) or {}
    return _apply_env_override(data)


def validate() -> dict:
    """加载 + 校验，返回配置字典；失败抛 ConfigError。"""
    data = load()
    errors: list[str] = []
    for dotted, (typ, rng) in _RULES.items():
        try:
            value = _dig(data, dotted)
        except ConfigError as exc:
            errors.append(str(exc))
            continue
        if not isinstance(value, typ) or isinstance(value, bool):
            try:
                value = _coerce(str(value), typ)
            except (TypeError, ValueError):
                errors.append(f"{dotted} 类型应为 {typ.__name__}，实际 {type(value).__name__}")
                continue
        if rng is not None:
            if isinstance(rng, tuple) and len(rng) == 2 and all(isinstance(x, (int, float)) for x in rng):
                if not (rng[0] <= value <= rng[1]):
                    errors.append(f"{dotted}={value} 越界，合法范围 [{rng[0]}, {rng[1]}]")
            elif isinstance(rng, tuple):
                if value not in rng:
                    errors.append(f"{dotted}={value} 非法，合法取值 {rng}")
    if errors:
        raise ConfigError("配置校验失败：\n  - " + "\n  - ".join(errors))
    return data


def get(dotted: str, default: Any = None) -> Any:
    data = load()
    try:
        return _dig(data, dotted)
    except ConfigError:
        return default


if __name__ == "__main__":
    cfg = validate()
    print(f"[OK] 配置校验通过：{SETTINGS_PATH}")
    print(f"  env={cfg['app']['env']}  project={cfg['app']['project']}")
    print(f"  blender_addon={cfg['ports']['blender_addon']}  ollama={cfg['ports']['ollama']}")
    print(f"  qc: motion>={cfg['qc']['motion_px_per_frame_min']}px  arcface>={cfg['qc']['arcface_similarity_min']}  sync_c>={cfg['qc']['sync_c_min']}")
    print(f"  budget={cfg['budget']['r5_total_cny']} CNY（预警 {cfg['budget']['warn_ratio']:.0%} / 熔断 {cfg['budget']['halt_ratio']:.0%}）")
