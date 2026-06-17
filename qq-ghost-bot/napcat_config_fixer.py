"""
NapCat OneBot 配置文件自动修复器
确保当前登录账号的 WebSocket 服务已开启（端口 6700）
"""

import json
import os
from pathlib import Path
import glob

# 标准 WebSocket 配置（与 onebot11_2392951403.json 一致）
DEFAULT_WEBSOCKET_SERVER = {
    "name": "websocket-server",
    "enable": True,
    "host": "127.0.0.1",
    "port": 6700,
    "messagePostFormat": "array",
    "reportSelfMessage": False,
    "token": "",
    "enableForcePushEvent": True,
    "debug": False,
    "heartInterval": 30000
}

# 基础配置骨架（缺失字段自动补充）
BASE_CONFIG_TEMPLATE = {
    "network": {
        "httpServers": [],
        "httpSseServers": [],
        "httpClients": [],
        "websocketServers": [],
        "websocketClients": [],
        "plugins": []
    },
    "musicSignUrl": "",
    "enableLocalFile2Url": False,
    "parseMultMsg": False,
    "imageDownloadProxy": "",
    "timeout": {
        "baseTimeout": 10000,
        "uploadSpeedKBps": 256,
        "downloadSpeedKBps": 256,
        "maxTimeout": 1800000
    }
}


def find_napcat_config_dir() -> Path | None:
    """查找 NapCat 配置目录（支持多种项目结构）"""
    base = Path(__file__).resolve().parent.parent
    candidates = [
        base / "NapCat.Shell" / "config",
        base / "NapCat" / "config",
        Path.cwd() / "NapCat.Shell" / "config",
        Path.cwd() / "config"
    ]
    for c in candidates:
        if c.exists() and c.is_dir():
            return c
    return None


def get_current_login_qq() -> str | None:
    """尝试从 NapCat 缓存中推断当前登录的 QQ 号（目前仅遍历所有配置）"""
    config_dir = find_napcat_config_dir()
    if not config_dir:
        return None
    files = glob.glob(str(config_dir / "onebot11_*.json"))
    if not files:
        return None
    # 返回最近修改的文件对应的 QQ（可优化）
    latest = max(files, key=os.path.getmtime)
    qq = Path(latest).stem.replace("onebot11_", "")
    return qq


def fix_all_onebot_configs():
    """修复所有 onebot11_*.json 配置文件，确保 websocket 已开启"""
    config_dir = find_napcat_config_dir()
    if not config_dir:
        print("[fixer] WARN: 未找到 NapCat 配置目录，跳过修复")
        return False

    files = glob.glob(str(config_dir / "onebot11_*.json"))
    if not files:
        print("[fixer] WARN: 未找到任何 onebot11_*.json 配置文件")
        return False

    fixed_count = 0
    for file_path in files:
        try:
            with open(file_path, "r", encoding="utf-8") as f:
                config = json.load(f)
        except Exception as e:
            print(f"[fixer] ERR: 读取 {file_path} 失败: {e}")
            continue

        # 确保 network 字段存在
        if "network" not in config:
            config["network"] = {}

        # 确保 websocketServers 存在
        if "websocketServers" not in config["network"]:
            config["network"]["websocketServers"] = []

        # 检查是否已有有效的 WebSocket 配置
        ws_servers = config["network"]["websocketServers"]
        has_valid = False
        for server in ws_servers:
            if server.get("enable") is True and server.get("port") == 6700:
                has_valid = True
                break

        if not has_valid:
            # 如果为空，添加标准配置
            config["network"]["websocketServers"].append(DEFAULT_WEBSOCKET_SERVER)
            # 同时补全缺失的骨架字段（确保结构完整）
            for key, value in BASE_CONFIG_TEMPLATE.items():
                if key not in config:
                    config[key] = value
                elif isinstance(value, dict) and key == "timeout":
                    for sub_key, sub_val in value.items():
                        if sub_key not in config["timeout"]:
                            config["timeout"][sub_key] = sub_val

            try:
                with open(file_path, "w", encoding="utf-8") as f:
                    json.dump(config, f, ensure_ascii=False, indent=2)
                print(f"[fixer] OK: 已修复 {Path(file_path).name}")
                fixed_count += 1
            except Exception as e:
                print(f"[fixer] ERR: 写入 {file_path} 失败: {e}")
        else:
            print(f"[fixer] OK: 已就绪 {Path(file_path).name} (WebSocket 已配置)")

    if fixed_count > 0:
        print(f"[fixer] 共修复 {fixed_count} 个配置文件，请重启 NapCat 使配置生效")
    else:
        print("[fixer] 所有配置文件均已配置，无需修复")

    return True


def ensure_napcat_websocket():
    """一键确保 NapCat WebSocket 已开启（供 main.py 调用）"""
    print("[fixer] 正在检查 NapCat OneBot 配置...")
    fix_all_onebot_configs()
    print("[fixer] 完成")