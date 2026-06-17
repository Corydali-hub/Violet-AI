"""
LLM 调用模块 — 封装 DeepSeek 异步客户端，支持流式输出。
"""

from openai import AsyncOpenAI

from config import LLM_API_KEY, LLM_API_BASE, LLM_MODEL
from prompts import PROMPT, RULES_BASE, RULES_SHORT, SCHOLAR_BONUS
from state_manager import get_state, add_history


# ============================================================
# LLM 异步客户端（兼容 DeepSeek API）
# ============================================================

llm = (
    AsyncOpenAI(
        api_key=LLM_API_KEY,
        base_url=LLM_API_BASE
    )
    if LLM_API_KEY
    else None
)


# ============================================================
# 流式 AI 回复生成器（核心）
# ============================================================

async def stream_reply_llm(
    gid: str,
    prompt: str,
    force_catgirl: bool = False
):
    """
    异步生成器，逐块产出 LLM 回复文本。
    用法：async for chunk in stream_reply_llm(...): ...
    """
    if not llm:
        yield "喵……API 还没配置好，猫猫先失陪了……"
        return

    state = get_state(gid)

    # ── 人格与模式选择 ──
    persona = (
        "catgirl"
        if force_catgirl
        else state["persona"]
    )

    if state["scholar"]:
        system = (
            PROMPT[persona]
            + SCHOLAR_BONUS
            + RULES_BASE
        )
        max_token = 2048
        temperature = 0.3
    else:
        system = (
            PROMPT[persona]
            + RULES_BASE
            + RULES_SHORT
        )
        max_token = 100
        temperature = 0.7

    messages = (
        [{"role": "system", "content": system}]
        + state["history"]
        + [{"role": "user", "content": prompt}]
    )

    try:
        # 异步流式调用 DeepSeek API
        stream = await llm.chat.completions.create(
            model=LLM_MODEL,
            messages=messages,
            temperature=temperature,
            max_tokens=max_token,
            stream=True
        )

        full_text = ""

        # 逐块产出
        async for chunk in stream:
            delta = chunk.choices[0].delta.content
            if delta:
                full_text += delta
                yield delta

        # 流结束后，记录完整的聊天历史
        if full_text:
            add_history(gid, "user", prompt)
            add_history(gid, "assistant", full_text.strip())

    except Exception as e:
        print("LLM流式错误:", e)
        yield "呜……网络好像有点问题，猫猫暂时宕机了……"


# ============================================================
# 非流式调用（保留兼容，内部调用流式生成器）
# ============================================================

async def reply_llm(
    gid: str,
    prompt: str,
    force_catgirl: bool = False
) -> str:
    """旧版非流式调用（兼容性保留）"""
    full = ""
    async for chunk in stream_reply_llm(gid, prompt, force_catgirl):
        full += chunk
    return full or "喵……猫猫没有说话……"