"""Kelly_Bundy Launcher — FastAPI 后端。"""
import asyncio
import os
import sys
import time
from pathlib import Path

import aiohttp
from fastapi import FastAPI, WebSocket, WebSocketDisconnect, UploadFile, File as FastAPIFile
from fastapi.responses import FileResponse, JSONResponse
from fastapi.staticfiles import StaticFiles

# 让 launcher 作为包可导入，同时能 import qq-ghost-bot 下的模块
_PROJECT_ROOT = Path(__file__).resolve().parent.parent
_BOT_DIR = _PROJECT_ROOT / "qq-ghost-bot"
sys.path.insert(0, str(_PROJECT_ROOT))
sys.path.insert(0, str(_BOT_DIR))

from launcher import config_manager as cfg
from launcher import manager as mgr
from state_manager import load_all_states, save_state_for_launcher, set_all_paused   # 新增

app = FastAPI(title="Kelly_Bundy Launcher", version="2.0")

# ── 静态文件（前端 build 后产物）───────────────────────────
STATIC = Path(__file__).resolve().parent / "static"
STATIC.mkdir(exist_ok=True)

if (STATIC / "assets").exists():
    app.mount("/assets", StaticFiles(directory=STATIC / "assets"), name="assets")

BG_DIR = STATIC / "bg"
BG_DIR.mkdir(exist_ok=True)
if BG_DIR.exists():
    app.mount("/static/bg", StaticFiles(directory=BG_DIR), name="bg")


@app.get("/favicon.png")
def favicon():
    f = STATIC / "favicon.png"
    if f.exists():
        return FileResponse(f, media_type="image/png")


@app.get("/logo.png")
def logo():
    f = STATIC / "logo.png"
    if f.exists():
        return FileResponse(f, media_type="image/png")


# ── WebSocket 连接池（实时日志）─────────────────────────────
_ws_clients: list[WebSocket] = []


def _broadcast_log(text: str):
    loop = asyncio.get_event_loop()
    dead = []
    for ws in _ws_clients:
        try:
            asyncio.run_coroutine_threadsafe(ws.send_text(text), loop)
        except Exception:
            dead.append(ws)
    for ws in dead:
        _ws_clients.remove(ws)


mgr.subscribe_logs(_broadcast_log)


# ============================================================
#  API：配置
# ============================================================

@app.get("/api/config")
def get_config():
    return cfg.load()


@app.put("/api/config")
def update_config(data: dict):
    cfg.save(data)
    return {"ok": True}


@app.post("/api/config/key")
def set_config_key(payload: dict):
    key = payload.get("key")
    value = payload.get("value")
    if key:
        cfg.set_value(key, value)
    return {"ok": True}


# ============================================================
#  API：进程控制
# ============================================================

@app.post("/api/bot/start")
def api_bot_start():
    napcat_path = cfg.get("napcat.path", "")
    if napcat_path:
        mgr.start_napcat(napcat_path)
    ok = mgr.start_bot()
    return {"running": ok}


@app.post("/api/bot/stop")
def api_bot_stop():
    mgr.stop_bot()
    return {"running": False}


@app.post("/api/bot/restart")
def api_bot_restart():
    mgr.stop_bot()
    time.sleep(1)
    napcat_path = cfg.get("napcat.path", "")
    if napcat_path:
        mgr.start_napcat(napcat_path)
    ok = mgr.start_bot()
    return {"running": ok}


@app.post("/api/napcat/start")
def api_napcat_start():
    path = cfg.get("napcat.path", "")
    if not path:
        return {"ok": False, "error": "NapCat 路径未配置"}
    ok = mgr.start_napcat(path)
    return {"ok": ok}


@app.post("/api/napcat/stop")
def api_napcat_stop():
    mgr.stop_napcat()
    return {"ok": True}


# ============================================================
#  API：状态
# ============================================================

@app.get("/api/status")
def api_status():
    napcat_path = cfg.get("napcat.path", "")
    nc_running = mgr.napcat_running()
    nc_logged = mgr.napcat_logged_in()

    qr_available = False
    qr_age = 999
    if napcat_path:
        qr_file = Path(napcat_path) / "cache" / "qrcode.png"
        if qr_file.exists():
            qr_age = time.time() - qr_file.stat().st_mtime
            if qr_age < 120:
                qr_available = True

    return {
        "bot_running": mgr.bot_running(),
        "napcat_running": nc_running,
        "napcat_logged": nc_logged,
        "ws_connected": nc_running,
        "llm_configured": bool(cfg.get("llm.api_key", "")),
        "qr_available": qr_available,
        "qr_age": int(qr_age),
        "uptime": 0,
    }


@app.get("/api/logs")
def api_logs(limit: int = 200):
    return mgr.get_bot_logs(limit)


# ============================================================
#  API：QQ登录二维码
# ============================================================

@app.get("/api/qrcode")
def qrcode():
    # 优先用配置中的 NapCat 路径
    np = cfg.get("napcat.path", "")
    if np:
        qr = Path(np) / "cache" / "qrcode.png"
        if qr.exists():
            return FileResponse(qr, media_type="image/png")

    # 回退到默认相对路径
    default_qr = _BOT_DIR.parent / "NapCat.Shell" / "cache" / "qrcode.png"
    if default_qr.exists():
        return FileResponse(default_qr, media_type="image/png")

    return JSONResponse({"error": "no qrcode"}, status_code=404)


# ============================================================
#  API：群列表（通过 OneBot）
# ============================================================

@app.get("/api/groups")
async def api_groups():
    if not mgr.napcat_running():
        return JSONResponse({"error": "NapCat 未运行"}, status_code=503)
    ws_url = cfg.get("bot.ws_url", "ws://127.0.0.1:6700")
    try:
        async with aiohttp.ClientSession() as s:
            async with s.ws_connect(ws_url, timeout=10) as ws:
                await ws.send_json({"action": "get_group_list", "echo": "get_groups_1"})
                for _ in range(20):
                    resp = await ws.receive_json(timeout=5)
                    if isinstance(resp, dict) and "status" in resp:
                        if resp.get("status") == "ok":
                            groups = resp.get("data", [])
                            # ===== 自动注册所有群 =====
                            from state_manager import _read_file, _write_file
                            file_data = _read_file()
                            for g in groups:
                                gid = str(g["group_id"])
                                if gid not in file_data:
                                    file_data[gid] = {
                                        "persona": "catgirl",
                                        "target": None,
                                        "scholar": False,
                                        "paused": False,
                                    }
                            if file_data:
                                _write_file(file_data)
                            # ===== 自动注册结束 =====
                            wl = cfg.get("bot.whitelist", [])
                            wl_str = [str(g) for g in wl]
                            if wl_str:
                                groups = [g for g in groups if str(g.get("group_id")) in wl_str]
                            return groups
                        return JSONResponse({"error": f"OneBot: {resp.get('status')}"}, status_code=502)
                return JSONResponse({"error": "未收到有效响应（20次尝试）"}, status_code=502)
    except Exception as e:
        return JSONResponse({"error": f"连接失败: {str(e)}"}, status_code=503)


# ============================================================
#  API：群独立状态（使用共享 state_manager）
# ============================================================

# 内存中的群状态缓存（启动时从共享文件恢复）
_group_states: dict[str, dict] = {}


def _restore_states():
    """启动时从共享文件恢复上次的状态。"""
    global _group_states
    try:
        _group_states = load_all_states()
    except Exception:
        pass


def _ensure_group(gid: str) -> dict:
    if gid not in _group_states:
        _group_states[gid] = {
            "persona": "catgirl",
            "target": None,
            "scholar": False,
            "paused": False,
            "memory_count": 0,
        }
    return _group_states[gid]


# 启动时加载
_restore_states()


@app.get("/api/groups/{gid}/state")
def get_group_state(gid: str):
    """获取群状态 — 每次从共享文件重新加载，确保和 Bot 实时同步。"""
    _restore_states()  # 重新从文件加载所有群状态
    return _ensure_group(gid)


@app.put("/api/groups/{gid}/state")
def update_group_state(gid: str, data: dict):
    state = _ensure_group(gid)
    for k in ("persona", "target", "scholar", "paused"):
        if k in data:
            val = data[k]
            # 空字符串视为 None（清除目标等）
            if k == "target" and val == "":
                val = None
            state[k] = val
    # 写入共享文件，bot 主进程会通过 mtime 检测到变更
    save_state_for_launcher(gid, state)
    return state


# ============================================================
#  API：批量群操作（新增）
# ============================================================

@app.post("/api/groups/all/pause")
def api_all_pause():
    """静音所有群"""
    count = set_all_paused(True)
    return {"ok": True, "count": count}


@app.post("/api/groups/all/active")
def api_all_active():
    """激活所有群"""
    count = set_all_paused(False)
    return {"ok": True, "count": count}


# ============================================================
#  API：背景图管理
# ============================================================

@app.post("/api/background/upload")
async def upload_background(file: UploadFile = FastAPIFile(...)):
    try:
        ext = Path(file.filename).suffix or ".png"
        filename = f"bg_{int(time.time())}{ext}"
        save_path = BG_DIR / filename
        content = await file.read()
        with open(save_path, "wb") as f:
            f.write(content)
        return {"url": f"/static/bg/{filename}", "ok": True}
    except Exception as e:
        return JSONResponse({"error": str(e)}, status_code=500)


@app.get("/api/background/config")
def get_background_config():
    cfg_data = cfg.load()
    bg = cfg_data.get("background", {})
    return {
        "url": bg.get("url", ""),
        "blur": bg.get("blur", 0),
        "offsetX": bg.get("offsetX", 0),
        "offsetY": bg.get("offsetY", 0),
        "theme": bg.get("theme", "dark"),
    }


@app.put("/api/background/config")
def update_background_config(data: dict):
    cfg_data = cfg.load()
    cfg_data["background"] = {
        "url": data.get("url", ""),
        "blur": data.get("blur", 0),
        "offsetX": data.get("offsetX", 0),
        "offsetY": data.get("offsetY", 0),
        "theme": data.get("theme", "dark"),
    }
    cfg.save(cfg_data)
    return {"ok": True}


# ============================================================
#  WebSocket：实时日志
# ============================================================

@app.websocket("/ws/logs")
async def ws_logs(ws: WebSocket):
    await ws.accept()
    for line in mgr.get_bot_logs(100):
        try:
            await ws.send_text(line)
        except Exception:
            break
    _ws_clients.append(ws)
    try:
        while True:
            await ws.receive_text()
    except WebSocketDisconnect:
        pass
    finally:
        if ws in _ws_clients:
            _ws_clients.remove(ws)


# ============================================================
#  前端页面（SPA fallback）
# ============================================================

@app.get("/")
async def index():
    index_html = STATIC / "index.html"
    if index_html.exists():
        return FileResponse(index_html)
    return {"message": "Kelly_Bundy Launcher API", "version": "2.0"}