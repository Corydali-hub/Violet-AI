"""进程管理 — 启动/停止 NapCat 和 Kelly_Bundy Bot。"""
import asyncio
import os
import socket
import subprocess
import sys
from pathlib import Path
from typing import Callable

ROOT = Path(__file__).resolve().parent.parent
BOT_DIR = ROOT / "qq-ghost-bot"

# ── NapCat ─────────────────────────────────────────────────

_napcat_bat: subprocess.Popen | None = None


def start_napcat(napcat_path: str) -> bool:
    global _napcat_bat
    stop_napcat()
    bat = Path(napcat_path) / "launcher-win10.bat"
    if not bat.exists():
        bat = Path(napcat_path) / "launcher.bat"
    if not bat.exists():
        print(f"[NapCat] 未找到启动脚本: {bat}")
        return False
    try:
        # 关键修改：传递 --onebot --port 6700 参数强制开启 OneBot
        _napcat_bat = subprocess.Popen(
            [str(bat), "--onebot", "--port", "6700"],
            cwd=str(Path(napcat_path)),
            creationflags=subprocess.CREATE_NEW_CONSOLE,
        )
        print(f"[NapCat] 启动命令: {bat} --onebot --port 6700")
        return True
    except Exception as e:
        print(f"[NapCat] 启动失败: {e}")
        return False


def stop_napcat():
    global _napcat_bat
    # 杀 NapCat 引导进程
    try:
        import psutil
        for p in psutil.process_iter(['name']):
            if p.info['name'] in ('NapCatWinBootMain.exe', 'NapCatWinBootMain'):
                p.kill()
    except ImportError:
        pass
    if _napcat_bat:
        try:
            _napcat_bat.terminate()
        except Exception:
            pass
        _napcat_bat = None


def napcat_running() -> bool:
    """通过端口 6700 检测 OneBot 是否监听（最可靠）。"""
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.settimeout(0.5)
        result = s.connect_ex(('127.0.0.1', 6700))
        s.close()
        return result == 0
    except Exception:
        return False


def napcat_logged_in() -> bool:
    """端口 6099 (WebUI) 也监听说明已登录。"""
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.settimeout(0.5)
        result = s.connect_ex(('127.0.0.1', 6099))
        s.close()
        return result == 0
    except Exception:
        return False


# ── Kelly Bot ──────────────────────────────────────────────

_bot_proc: subprocess.Popen | None = None
_bot_logs: list[str] = []
_log_callbacks: list[Callable] = []


def start_bot() -> bool:
    """启动 堇言AI Python 机器人。"""
    global _bot_proc, _bot_logs
    stop_bot()
    main_py = BOT_DIR / "main.py"
    if not main_py.exists():
        print(f"[Bot] 找不到 {main_py}")
        return False

    _bot_logs = ["[系统] 堇言AI 启动中..."]

    def _reader(stream, prefix):
        for line in iter(stream.readline, ""):
            if not line:
                break
            text = f"{prefix} {line.rstrip()}"
            _bot_logs.append(text)
            for cb in _log_callbacks:
                try:
                    cb(text)
                except Exception:
                    pass

    try:
        _bot_proc = subprocess.Popen(
            [sys.executable, "-u", str(main_py)],
            cwd=str(BOT_DIR),
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            text=True,
            encoding='gbk',
            errors='replace',
            bufsize=1,
        )
        import threading
        threading.Thread(target=_reader, args=(_bot_proc.stdout, "[Bot]"), daemon=True).start()
        return True
    except Exception as e:
        _bot_logs.append(f"[错误] 启动失败: {e}")
        return False


def stop_bot():
    global _bot_proc
    if _bot_proc:
        try:
            _bot_proc.terminate()
        except Exception:
            pass
        _bot_proc = None


def bot_running() -> bool:
    return _bot_proc is not None and _bot_proc.poll() is None


def get_bot_logs(limit: int = 200) -> list[str]:
    return _bot_logs[-limit:]


def subscribe_logs(cb: Callable):
    _log_callbacks.append(cb)


def unsubscribe_logs(cb: Callable):
    if cb in _log_callbacks:
        _log_callbacks.remove(cb)