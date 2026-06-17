"""
QQ 机器人 — OneBot v11 WebSocket
@Kelly_Bundy 双人格（猫娘/毒舌）+ 主人特权

启动入口：python main.py
需要先启动 NapCat（OneBot WebSocket 端口 6700）
"""

import asyncio
import json
import signal

import aiohttp

from config import ONEBOT_WS_URL, BOT_NAME
from llm import llm
from handlers import handle_message
from napcat_config_fixer import ensure_napcat_websocket   # 配置修复器


# ============================================================
# OneBot 通讯
# ============================================================

ws = None
echo = 0


async def send_group(gid: int, text: str):
    """发送群消息。"""
    global echo
    if not ws:
        return
    echo += 1
    await ws.send_json({
        "action": "send_group_msg",
        "params": {
            "group_id": gid,
            "message": text
        },
        "echo": str(echo)
    })


# ============================================================
# 事件分发
# ============================================================

def dispatch(data: dict):
    """将 OneBot 事件分发给对应的处理器。"""
    if (
        data.get("post_type") == "message"
        and data.get("message_type") == "group"
    ):
        asyncio.create_task(handle_message(data, send_group))


# ============================================================
# WebSocket 主循环
# ============================================================

running = True


async def main_loop():
    global ws, running

    print(f"[{BOT_NAME}] 正在连接：{ONEBOT_WS_URL}")

    while running:
        try:
            async with aiohttp.ClientSession() as session:
                async with session.ws_connect(
                    ONEBOT_WS_URL,
                    heartbeat=30,
                    max_msg_size=2**20
                ) as socket:

                    ws = socket

                    print(
                        f"[{BOT_NAME}] 已连接成功 | "
                        f"LLM={'开启' if llm else '关闭'}"
                    )

                    async for message in socket:
                        if message.type == aiohttp.WSMsgType.TEXT:
                            try:
                                data = json.loads(message.data)
                                dispatch(data)
                            except json.JSONDecodeError:
                                pass

                        elif message.type in (
                            aiohttp.WSMsgType.ERROR,
                            aiohttp.WSMsgType.CLOSED
                        ):
                            break

        except asyncio.CancelledError:
            break

        except Exception as e:
            print("连接异常：", e)
            if running:
                await asyncio.sleep(5)


# ============================================================
# 程序入口
# ============================================================

async def main():
    global running

    # === 启动时自动修复 NapCat OneBot 配置 ===
    ensure_napcat_websocket()

    def shutdown():
        global running
        running = False
        print("正在关闭 Kelly_Bundy...")

    for sig in (signal.SIGINT, signal.SIGTERM):
        try:
            asyncio.get_event_loop().add_signal_handler(sig, shutdown)
        except NotImplementedError:
            pass

    await main_loop()


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("Kelly_Bundy 已退出。")