"""配置管理 — 读写 data/config.json。"""
import json
import os
from pathlib import Path
from typing import Any

DATA_DIR = Path(__file__).resolve().parent / "data"
CONFIG_PATH = DATA_DIR / "config.json"

DEFAULT_CONFIG: dict[str, Any] = {
    "llm": {
        "api_key": "",
        "api_base": "https://api.deepseek.com",
        "model": "deepseek-chat",
        "temperature": 0.7,
        "max_tokens": 100,
    },
    "bot": {
        "owner": "2272025586",
        "qq": "",
        "bot_name": "Kelly_Bundy",
        "ws_url": "ws://127.0.0.1:6700",
        "whitelist": [],
    },
    "napcat": {
        "path": "",
    },
    "background": {
        "url": "",
        "blur": 0,
        "offsetX": 0,
        "offsetY": 0,
        "theme": "dark",
    },
}

_config_cache: dict | None = None


def _ensure_dir():
    DATA_DIR.mkdir(parents=True, exist_ok=True)


def load() -> dict:
    global _config_cache
    if _config_cache is not None:
        return _config_cache
    _ensure_dir()
    if CONFIG_PATH.exists():
        with open(CONFIG_PATH, "r", encoding="utf-8") as f:
            _config_cache = json.load(f)
    else:
        _config_cache = DEFAULT_CONFIG.copy()
        save(_config_cache)
    return _config_cache


def save(config: dict) -> None:
    global _config_cache
    _ensure_dir()
    with open(CONFIG_PATH, "w", encoding="utf-8") as f:
        json.dump(config, f, ensure_ascii=False, indent=2)
    _config_cache = config


def get(key: str, default: Any = None) -> Any:
    """用点分隔路径取值，如 'llm.model'。"""
    cfg = load()
    for part in key.split("."):
        if isinstance(cfg, dict):
            cfg = cfg.get(part, default)
        else:
            return default
    return cfg


def set_value(key: str, value: Any) -> None:
    """用点分隔路径设值。"""
    cfg = load()
    parts = key.split(".")
    current = cfg
    for part in parts[:-1]:
        if part not in current:
            current[part] = {}
        current = current[part]
    current[parts[-1]] = value
    save(cfg)
