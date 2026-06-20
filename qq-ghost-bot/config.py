"""
配置文件 — 统一从 WebUI (config.json) 和 .env 读取。
优先级：WebUI > .env > 默认值
"""

import os
import json
from pathlib import Path
from dotenv import load_dotenv

# 始终从脚本所在目录加载 .env（不受 cwd 影响）
load_dotenv(Path(__file__).parent / ".env")

# ============================================================
# 工具：读取 WebUI 的配置文件（支持热重载）
# ============================================================

_CONFIG_PATH = Path(__file__).resolve().parent.parent / "launcher" / "data" / "config.json"
_CONFIG_MTIME: float = 0.0
_WEBUI_CONFIG: dict = {}


def _load_webui_config():
    """尝试读取 launcher/data/config.json，失败则返回空字典"""
    global _CONFIG_MTIME, _WEBUI_CONFIG

    if not _CONFIG_PATH.exists():
        _CONFIG_MTIME = 0.0
        _WEBUI_CONFIG = {}
        return {}

    try:
        new_mtime = _CONFIG_PATH.stat().st_mtime
        # 文件未变化 → 直接返回缓存
        if new_mtime == _CONFIG_MTIME and _WEBUI_CONFIG:
            return _WEBUI_CONFIG
    except OSError:
        pass

    try:
        with open(_CONFIG_PATH, "r", encoding="utf-8") as f:
            data = json.load(f)
            _WEBUI_CONFIG = data if isinstance(data, dict) else {}
            _CONFIG_MTIME = _CONFIG_PATH.stat().st_mtime
            return _WEBUI_CONFIG
    except Exception as e:
        print(f"[config] 读取 WebUI 配置失败: {e}，将使用 .env 或默认值")
        return {}


# 首次加载
_load_webui_config()


# ============================================================
# 配置项读取（按优先级）
# ============================================================

def _get_webui(*keys: str, default: str = "") -> str:
    """
    从 WebUI 配置中按路径取值（每次调用自动检测文件变化）。
    例如: _get_webui("bot", "bot_name") 读取 config.json 中的 bot.bot_name
    """
    cfg = _load_webui_config()
    if not cfg:
        return default
    current = cfg
    for key in keys:
        if isinstance(current, dict):
            current = current.get(key)
            if current is None:
                return default
        else:
            return default
    return current if current is not None else default


# ===== LLM 配置 =====
def _get_llm_config():
    webui_key = _get_webui("llm", "api_key", default="")
    env_key = os.getenv("LLM_API_KEY", "")
    LLM_API_KEY = webui_key if webui_key else env_key
    
    webui_base = _get_webui("llm", "api_base", default="")
    env_base = os.getenv("LLM_API_BASE", "https://api.deepseek.com/v1")
    LLM_API_BASE = webui_base if webui_base else env_base
    
    webui_model = _get_webui("llm", "model", default="")
    env_model = os.getenv("LLM_MODEL", "deepseek-chat")
    LLM_MODEL = webui_model if webui_model else env_model
    
    # 可选：温度和 max_tokens（WebUI 也有，但未在 Setup.vue 暴露，可备用）
    webui_temp = _get_webui("llm", "temperature", default="")
    TEMPERATURE = float(webui_temp) if webui_temp else float(os.getenv("TEMPERATURE", "0.7"))
    
    webui_max = _get_webui("llm", "max_tokens", default="")
    MAX_TOKEN = int(webui_max) if webui_max else int(os.getenv("MAX_TOKEN", "2048"))
    
    return LLM_API_KEY, LLM_API_BASE, LLM_MODEL, TEMPERATURE, MAX_TOKEN


LLM_API_KEY, LLM_API_BASE, LLM_MODEL, TEMPERATURE, MAX_TOKEN = _get_llm_config()


# ===== 机器人基础配置（优先 WebUI） =====
# 机器人名字
BOT_NAME = (
    _get_webui("bot", "bot_name", default="")
    or os.getenv("BOT_NAME", "")
    or "MyBot"
)

# 机器人名字（热重载：每次调用重新读取）
def get_bot_name() -> str:
    return (
        _get_webui("bot", "bot_name", default="")
        or os.getenv("BOT_NAME", "")
        or "猫娘"
    )


# 主人 QQ（热重载：每次调用重新读取）
def get_owner_id() -> str:
    return (
        _get_webui("bot", "owner", default="")
        or os.getenv("OWNER_ID", "")
        or ""
    )


# 主人称呼（热重载：每次调用重新读取）
def get_owner_title() -> str:
    return (
        _get_webui("bot", "owner_title", default="")
        or os.getenv("OWNER_TITLE", "")
        or "主人"
    )


# 向后兼容的模块级常量（首次导入时固定，可能过时；推荐用 getter 函数）
OWNER_ID = get_owner_id()
OWNER_TITLE = get_owner_title()

# ===== Tavily 搜索 API（可选） =====
def get_tavily_api_key() -> str:
    return _get_webui("tavily", "api_key", default="") or os.getenv("TAVILY_API_KEY", "")


# ===== OneBot WebSocket 地址 =====
ONEBOT_WS_URL = (
    _get_webui("bot", "ws_url", default="")
    or os.getenv("ONEBOT_WS_URL", "")
    or "ws://127.0.0.1:6700"
)


# ===== 群白名单 =====
def _get_whitelist():
    webui_wl = _get_webui("bot", "whitelist", default=[])
    if isinstance(webui_wl, list) and webui_wl:
        return [str(x) for x in webui_wl]
    
    env_wl = os.getenv("WHITELIST", "")
    if env_wl:
        return [x.strip() for x in env_wl.split(",") if x.strip()]
    
    return []


WHITELIST = set(_get_whitelist())


# ============================================================
# 调试输出
# ============================================================

if __name__ != "__main__":
    sources = []
    if _get_webui("bot", "owner", default=""):
        sources.append("WebUI")
    elif os.getenv("OWNER_ID", ""):
        sources.append(".env")
    else:
        sources.append("未配置")
    
    print(f"[config] 主人 QQ: {get_owner_id() or '(未设置)'} (来源: {sources[0]})")
    print(f"[config] 机器人名字: {BOT_NAME}")
    print(f"[config] 主人称呼: {get_owner_title()}")
    print(f"[config] OneBot WS 地址: {ONEBOT_WS_URL}")