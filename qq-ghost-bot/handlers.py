"""
消息处理模块 — 触发器、命令、消息分发（支持流式输出 + 句子级分段发送）。
"""

import asyncio
import re
import time

from state_manager import (
    get_state,
    set_paused,
    set_scholar,
    set_persona,
    set_target,
    clear_history,
    get_last,
    set_last,
    set_all_paused,          # 新增
)
from llm import stream_reply_llm
from config import BOT_NAME, WHITELIST, OWNER_ID, OWNER_TITLE, get_owner_id, get_owner_title

# ============================================================
# 工具：将 @QQ号 转换为真实 CQ:at 码
# ============================================================

# 匹配 @名称 (QQ号) 或 @名称（QQ号）—— 作为 LLM 不写纯数字时的兜底
_AT_NAME_RE = re.compile(r"@([^\d\s)]+)\s*[(（](\d+)[)）]")
# 匹配 @QQ号（纯数字）
_AT_DIGIT_RE = re.compile(r"@(\d+)")


def _apply_at(text: str) -> str:
    """将 LLM 回复中的 @提及 替换为 OneBot 真实的 CQ:at 码。

    优先匹配 @名称 (QQ号) 格式作为兜底，再匹配 @QQ号 格式。
    """
    # 先处理 @名称 (数字) —— 整个替换掉，避免后续被 @数字 二次匹配
    text = _AT_NAME_RE.sub(r"[CQ:at,qq=\2]", text)
    # 再处理 @数字
    text = _AT_DIGIT_RE.sub(r"[CQ:at,qq=\1]", text)
    return text


# ============================================================
# 固定关键词触发器（无需 @）
# ============================================================

TRIGGERS = {
    "谁玩": "我玩我玩",
    "甲烷": "表哥我不是甲烷，拉我拉我，我已经在开机子了",
    "有没有玩的": "我我我，来来来，FTJ7758 2=1",
    "吸血": "吸谁的血，大大方方来吸我的血，绝密航天2=1，FTJ7758，小飞棍3F",
    "八角笼": "谁是好人谁是坏人",
    "啵啵": "TD",
    "哦对了": "是我点的举报",
    "零号大坝": "零号大坝是对的",
    "小团体": "小团体来了，你们聊",
    "标志": "标志",
    "彪子": "彪子",
    "糖拌番茄": "糖拌番茄骨汤面，疙瘩汤面先缓缓",
}

# LLM 调用锁（同群内串行）
_lock = asyncio.Lock()


# ============================================================
# 工具函数
# ============================================================

def allowed(gid: str) -> bool:
    """白名单判断。"""
    return not WHITELIST or gid in WHITELIST


def mentioned(text: str, raw: str, self_id: str) -> bool:
    """是否 @ 机器人。"""
    return (
        BOT_NAME in text
        or f"[CQ:at,qq={self_id}]" in raw
    )


def extract_text(msg: list) -> str:
    """提取文本消息，将 @ 段转为 @QQ 格式，让 LLM 看到 QQ 号。"""
    parts = []
    for seg in msg:
        if seg["type"] == "text":
            parts.append(seg["data"].get("text", ""))
        elif seg["type"] == "at":
            qq = seg["data"].get("qq", "")
            if qq:
                parts.append(f"@{qq}")
    return "".join(parts).strip()


def remove_bot_name(text: str, self_id: str = "") -> str:
    """去掉 @Bot 前缀（支持 @名字 和 @QQ号）。"""
    t = text.strip()
    for prefix in (f"@{BOT_NAME}", BOT_NAME, f"@{self_id}"):
        if t.startswith(prefix):
            return t[len(prefix):].strip()
    return t


# ============================================================
# 主人控制命令（无需 @）
# ============================================================

async def handle_owner_no_at(gid: str, msg: str, send_group) -> bool:
    """
    处理主人无需 @ 的命令。
    返回 True 表示已处理（调用方应 return）。
    """

    # 静音
    if "不许吵了" in msg or "闭嘴" in msg:
        set_paused(gid, True)
        await send_group(int(gid), "呜……猫猫安静一点，不闹啦🥺")
        return True

    # 唤醒
    if "猫猫可以说话了哦" in msg or "在哪鬼混呢" in msg:
        set_paused(gid, False)
        await send_group(int(gid), "喵呜~ 猫猫回来啦！")
        return True

    # 全局静音（新增）
    if msg == "全局静音":
        n = set_all_paused(True)
        await send_group(int(gid), f"📢 已静音 {n} 个群，所有群将不再响应对话。")
        return True

    # 全局活跃（新增）
    if msg == "全局活跃":
        n = set_all_paused(False)
        await send_group(int(gid), f"📢 已激活 {n} 个群，所有群恢复正常响应。")
        return True

    # 博学模式开启
    if ("博学猫猫" in msg and "启动" in msg) or "乖乖回答一些问题" in msg:
        set_scholar(gid, True)
        await send_group(int(gid), "喵！知识模块加载完成啦✨猫猫会认真回答复杂问题的！")
        return True

    # 关闭博学模式
    if "傻傻猫娘" in msg or "变笨" in msg:
        set_scholar(gid, False)
        clear_history(gid)
        await send_group(int(gid), "呜喵……脑袋里的知识好像飞走了一点……")
        return True

    return False


# ============================================================
# 主人高级命令（需要 @）
# ============================================================

async def handle_owner_at(gid: str, command: str, send_group) -> bool:
    """
    处理主人 @ 后的命令。
    返回 True 表示已处理。
    """
    state = get_state(gid)

    # 切换乖猫娘
    if command == "乖" and state["persona"] != "catgirl":
        set_persona(gid, "catgirl")
        await send_group(int(gid), "喵呜~ 猫猫变乖啦，以后会软软地陪姐姐聊天呀~")
        return True

    # 切换毒舌人格
    if command == "坏" and state["persona"] != "tsundere":
        set_persona(gid, "tsundere")
        await send_group(int(gid), "哼，终于轮到本小姐出来了吗？希望你们别被我气哭躲到被子里呜呜呜。")
        return True

    # 设置毒舌目标
    if command.startswith("攻击"):
        target = command[2:].strip()
        if target:
            set_target(gid, target)
            await send_group(int(gid), f"呵，知道了，以后猫猫我会重点针对一下 {target}。")
        return True

    # 取消攻击目标
    if command in ("停止攻击", "停", "关闭毒舌"):
        set_target(gid, None)
        await send_group(int(gid), "啧，看在主人的面子上那我就放过你了。")
        return True

    # 清除当前群记忆
    if command == "清记忆":
        clear_history(gid)
        await send_group(int(gid), "喵……猫猫把这个群的记忆全倒出小脑袋瓜啦。")
        return True

    return False


# ============================================================
# 构造 AI 输入
# ============================================================

def build_prompt(
    gid: str,
    uid: str,
    nickname: str,
    command: str,
    is_owner: bool,
) -> tuple[str, bool]:
    """
    构造发给 LLM 的 prompt。
    返回 (prompt, force_catgirl)。
    """
    state = get_state(gid)

    if is_owner:
        owner_title = get_owner_title()
        prompt = (
            f"{owner_title}对你说：{command}\n"
            f"请以亲近、依赖{owner_title}的方式回复。"
        )
        return prompt, True

    elif state["persona"] == "tsundere":
        target = state["target"]
        if target and uid != target:
            # 有毒舌目标，但当前用户不是目标 → 乖巧猫娘
            prompt = (
                f"{nickname}说：{command}\n\n"
                "请直接回答问题，保持温柔可爱。"
            )
            return prompt, True
        else:
            # 无目标（全员毒舌）或当前用户就是目标
            if target:
                prompt = (
                    f"当前重点吐槽目标（QQ={target}）：{nickname}\n\n"
                    f"{nickname}说：{command}\n"
                    f"对 {nickname} 尽情毒舌吐槽，不要心软。"
                )
            else:
                prompt = (
                    f"{nickname}说：{command}\n"
                    f"用毒舌傲娇的风格回复 {nickname}，可以吐槽拆台。"
                )
            return prompt, False

    else:
        prompt = (
            f"用户昵称：{nickname}\n"
            f"用户的问题：{command}\n\n"
            "请直接回答问题，不要重复、复述或重新描述用户的问题。"
        )
        return prompt, False


# ============================================================
# 消息分发入口（流式 + 句子级分段发送）
# ============================================================

async def handle_message(data: dict, send_group):
    """
    处理一条群消息。
    send_group: async callable(gid: int, text: str)
    """

    gid = str(data.get("group_id", ""))
    uid = str(data.get("user_id", ""))
    sid = str(data.get("self_id", ""))

    if not gid or not allowed(gid):
        return

    state = get_state(gid)

    raw = data.get("raw_message", "")

    nickname = (
        data.get("sender", {}).get("card", "")
        or data.get("sender", {}).get("nickname", "群友")
    )

    text = extract_text(data.get("message", []))
    if not text:
        return

    msg = text.strip()
    is_owner = (uid == get_owner_id())

    # ── 主人控制（无需 @） ──
    if is_owner and await handle_owner_no_at(gid, msg, send_group):
        return

    # ── 静音检查 ──
    if state["paused"]:
        return

    # ── 复读检测 ──
    now = time.time()
    previous = get_last(gid, uid)
    if (
        previous
        and previous[0] == msg
        and now - previous[1] < 30
    ):
        set_last(gid, uid, msg, now)
        await send_group(int(gid), msg)
        return
    else:
        set_last(gid, uid, msg, now)

    # ── 固定关键词触发（无需 @） ──
    for key, value in TRIGGERS.items():
        if msg.startswith(key):
            await send_group(int(gid), value)
            return

    # ── 非 @ 不进入 AI 对话 ──
    if not mentioned(text, raw, sid):
        return

    # 去掉 @ 名字
    command = remove_bot_name(text, sid)

    # ── 主人高级命令（需要 @） ──
    if is_owner and await handle_owner_at(gid, command, send_group):
        return

    # ── 构造 Prompt 并调用 LLM（流式 + 句子级分段） ──
    prompt, force_catgirl = build_prompt(gid, uid, nickname, command, is_owner)

    # 中文句子结束标点（句号、问号、感叹号、分号、省略号、换行）
    SENTENCE_ENDINGS = {"。", "？", "！", "；", "…", "\n"}
    MIN_LEN = 200   # 每段最少字数
    MAX_LEN = 400   # 每段最大字数

    async with _lock:
        buffer = ""
        first_sent = False

        async for delta in stream_reply_llm(gid, prompt, force_catgirl, search_query=command):
            buffer += delta

            # 当 buffer 长度达到最小阈值时，尝试分段
            while len(buffer) >= MIN_LEN:
                # 在 [MIN_LEN, MAX_LEN] 范围内从后往前找最后一个句子结束标点
                start = MIN_LEN - 1
                end = min(len(buffer), MAX_LEN)
                cut_pos = -1

                # 从 end 往 start 方向找标点
                for i in range(end, start - 1, -1):
                    if buffer[i - 1] in SENTENCE_ENDINGS:
                        cut_pos = i
                        break

                if cut_pos != -1:
                    # 找到合适的截断点（完整句子结束）
                    await send_group(int(gid), _apply_at(buffer[:cut_pos]))
                    buffer = buffer[cut_pos:]
                    first_sent = True
                    continue

                # 没找到标点，但 buffer 已超过 MAX_LEN，强制截断
                if len(buffer) >= MAX_LEN:
                    # 为了减少割裂，尝试在 MAX_LEN 附近（±10）找标点，找不到就硬切
                    force_cut = MAX_LEN
                    # 在 [MAX_LEN-10, MAX_LEN+10] 范围内找最后一个标点
                    search_start = max(0, MAX_LEN - 10)
                    search_end = min(len(buffer), MAX_LEN + 10)
                    found = -1
                    for i in range(search_end, search_start - 1, -1):
                        if buffer[i - 1] in SENTENCE_ENDINGS:
                            found = i
                            break
                    if found != -1:
                        cut_pos = found
                    else:
                        cut_pos = MAX_LEN   # 实在找不到就硬切
                    await send_group(int(gid), _apply_at(buffer[:cut_pos]))
                    buffer = buffer[cut_pos:]
                    first_sent = True
                    continue

                # 既不满足标点截断，也未达到强制截断长度，退出 while，继续接收
                break

        # 收尾：发送最后剩余的文本（无论多少，一次性发完，避免刷屏）
        if buffer:
            await send_group(int(gid), _apply_at(buffer))
        elif not first_sent:
            # 极端情况：AI 什么都没生成
            await send_group(int(gid), "喵……猫猫好像说不出话了……")