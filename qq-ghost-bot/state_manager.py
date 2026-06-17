"""
共享群状态管理器 — Bot 和 Launcher 共用。

设计原则：
- state_overrides.json 是唯一数据源
- Bot 修改状态时采用 read-merge-write 模式，避免覆盖 Launcher 对其它群的修改
- Bot 处理每条消息前检查文件 mtime，仅在外部 (Launcher) 改动时才重新加载
- 聊天历史 (history) 和复读 (last) 只在内存中，不写盘
"""

import json
import time
from pathlib import Path
from typing import Optional

# 文件路径
STATE_FILE = Path(__file__).resolve().parent / "data" / "state_overrides.json"

# 内存状态：{ group_id -> { persona, target, scholar, paused, history, last } }
_groups: dict[str, dict] = {}
_file_mtime: float = 0.0

HIST_MAX = 20


# ============================================================
# 文件读写
# ============================================================

def _read_file() -> dict:
    """读取 JSON 文件，返回 {gid: {persona, target, scholar, paused}}。"""
    try:
        if STATE_FILE.exists():
            return json.loads(STATE_FILE.read_text(encoding="utf-8"))
    except Exception:
        pass
    return {}


def _write_file(data: dict):
    """
    将当前所有群的状态键写入 JSON 文件。
    采用 read-merge-write：先读盘上最新内容，只更新当前内存中存在的群，
    避免覆盖 Launcher 对其它群的修改。
    """
    STATE_FILE.parent.mkdir(parents=True, exist_ok=True)

    # 读取盘上最新
    disk_data = _read_file()

    # 合入内存中存在的群
    for gid, state in data.items():
        disk_data[gid] = {
            "persona": state.get("persona", "catgirl"),
            "target": state.get("target"),
            "scholar": state.get("scholar", False),
            "paused": state.get("paused", False),
        }

    with open(STATE_FILE, "w", encoding="utf-8") as f:
        json.dump(disk_data, f, ensure_ascii=False, indent=2)
    global _file_mtime
    _file_mtime = STATE_FILE.stat().st_mtime


def _check_external_change() -> bool:
    """检查文件是否被外部 (Launcher) 修改过（不更新 mtime，由调用方决定何时更新）。"""
    try:
        if STATE_FILE.exists():
            mtime = STATE_FILE.stat().st_mtime
            if mtime > _file_mtime + 0.01:
                return True
    except Exception:
        pass
    return False


# ============================================================
# 公开 API
# ============================================================

def get_state(gid: str) -> dict:
    """
    获取群状态。
    首次访问时从文件初始化；之后每次调用检查文件 mtime，
    只有在 Launcher 侧有改动时才重新加载所有群的状态。
    """
    global _file_mtime

    # 首次初始化
    if gid not in _groups:
        _groups[gid] = {
            "persona": "catgirl",
            "target": None,
            "scholar": False,
            "paused": False,
            "history": [],
            "last": {},
        }
        # 首次加载时记录 mtime
        if STATE_FILE.exists():
            _file_mtime = STATE_FILE.stat().st_mtime

    # 检查外部改动（Launcher 侧修改）
    if _check_external_change():
        file_data = _read_file()
        # 更新所有已加载的群（不是只更新当前 gid）
        for g in list(_groups.keys()):
            if g in file_data:
                ov = file_data[g]
                for key in ("persona", "target", "scholar", "paused"):
                    if key in ov:
                        _groups[g][key] = ov[key]
        # 所有群都更新完毕后再记录 mtime
        if STATE_FILE.exists():
            _file_mtime = STATE_FILE.stat().st_mtime

    return _groups[gid]


def set_paused(gid: str, paused: bool):
    """设置静音状态，立即写盘。"""
    state = get_state(gid)
    state["paused"] = paused
    _write_file(_groups)


def set_scholar(gid: str, scholar: bool):
    """设置博学模式，立即写盘。"""
    state = get_state(gid)
    state["scholar"] = scholar
    if scholar:
        state["history"].clear()
    _write_file(_groups)


def set_persona(gid: str, persona: str):
    """切换人格 (catgirl / tsundere)，立即写盘并清空历史。"""
    state = get_state(gid)
    state["persona"] = persona
    state["history"].clear()
    _write_file(_groups)


def set_target(gid: str, target: Optional[str]):
    """设置毒舌目标，立即写盘。"""
    state = get_state(gid)
    state["target"] = target
    _write_file(_groups)


def clear_history(gid: str):
    """清空聊天记录（只在内存）。"""
    state = get_state(gid)
    state["history"].clear()


def trim_history(state: dict):
    """裁剪聊天记录。"""
    history = state["history"]
    if len(history) > HIST_MAX:
        state["history"] = history[-HIST_MAX:]


def add_history(gid: str, role: str, content: str):
    """追加聊天记录。"""
    state = get_state(gid)
    state["history"].append({"role": role, "content": content})
    trim_history(state)


def get_last(gid: str, uid: str):
    """获取某用户上次的消息和時間。"""
    state = get_state(gid)
    return state["last"].get(uid)


def set_last(gid: str, uid: str, msg: str, ts: float):
    """记录某用户上次的消息。"""
    state = get_state(gid)
    state["last"][uid] = (msg, ts)


# ============================================================
# 批量操作
# ============================================================

def set_all_paused(paused: bool) -> int:
    """
    将当前所有已记录状态的群统一设置为静音/活跃。
    返回被修改的群数量。
    """
    # 先确保所有已加载的群状态是最新的
    # 读取所有群的状态文件
    file_data = _read_file()
    count = 0
    for gid, s in file_data.items():
        if s.get("paused", False) != paused:
            s["paused"] = paused
            count += 1
    if count > 0:
        # 写回文件，并更新内存
        with open(STATE_FILE, "w", encoding="utf-8") as f:
            json.dump(file_data, f, ensure_ascii=False, indent=2)
        global _file_mtime
        _file_mtime = STATE_FILE.stat().st_mtime
        # 同步更新内存中已加载的群
        for gid, s in file_data.items():
            if gid in _groups:
                _groups[gid]["paused"] = s["paused"]
    return count


# ============================================================
# Launcher 兼容 API（供 launcher/app.py 使用）
# ============================================================

def load_all_states() -> dict[str, dict]:
    """Launcher 启动时加载所有群状态。"""
    file_data = _read_file()
    result = {}
    for gid, s in file_data.items():
        result[gid] = {
            "persona": s.get("persona", "catgirl"),
            "target": s.get("target"),
            "scholar": s.get("scholar", False),
            "paused": s.get("paused", False),
            "memory_count": 0,
        }
    return result


def save_state_for_launcher(gid: str, data: dict):
    """Launcher 修改群状态时调用，写盘（read-merge-write）。"""
    file_data = _read_file()
    file_data[gid] = {
        "persona": data.get("persona", "catgirl"),
        "target": data.get("target"),
        "scholar": data.get("scholar", False),
        "paused": data.get("paused", False),
    }
    STATE_FILE.parent.mkdir(parents=True, exist_ok=True)
    with open(STATE_FILE, "w", encoding="utf-8") as f:
        json.dump(file_data, f, ensure_ascii=False, indent=2)
    global _file_mtime
    _file_mtime = STATE_FILE.stat().st_mtime