"""
LLM 调用模块 — 封装 DeepSeek 异步客户端，支持流式输出。
"""

import asyncio
from urllib.parse import urlparse

from openai import AsyncOpenAI

from config import LLM_API_KEY, LLM_API_BASE, LLM_MODEL, get_owner_id, get_owner_title, get_bot_name, get_tavily_api_key
from prompts import PROMPT, RULES_BASE, RULES_SHORT, SCHOLAR_BONUS
from state_manager import get_state, add_history
from tavily_search import search as tavily_search


# ============================================================
# 工具：检测图片 URL 在国内是否可直连
# ============================================================

async def _check_url_reachable(url: str, timeout: float = 3.0) -> bool:
    """TCP 握手探测，成功说明无需代理即可访问"""
    try:
        parsed = urlparse(url)
        host = parsed.hostname
        port = parsed.port or 443
        _, writer = await asyncio.wait_for(
            asyncio.open_connection(host, port),
            timeout=timeout
        )
        writer.close()
        await asyncio.sleep(0)  # 确保 writer 完全关闭
        return True
    except Exception:
        return False


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
    force_catgirl: bool = False,
    search_query: str = "",
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

    owner_id = get_owner_id()
    owner_title = get_owner_title()
    bot_name = get_bot_name()
    fmt = {"owner_id": owner_id, "owner_title": owner_title, "bot_name": bot_name}

    if state["scholar"]:
        system = (
            PROMPT[persona].format(**fmt)
            + SCHOLAR_BONUS
            + RULES_BASE.format(**fmt)
        )
        max_token = 2048
        temperature = 0.3

        # ── 博学模式：如果配置了 Tavily，进行联网搜索 ──
        tavily_key = get_tavily_api_key()
        if tavily_key and search_query:
            print(f"[Tavily] 搜索: {search_query[:60]}")
            result = await tavily_search(search_query, tavily_key)
            if result["images"] or result["answer"] or result["results"]:
                context_parts = ["【联网搜索结果】"]
                if result["answer"]:
                    context_parts.append(f"摘要：{result['answer']}")
                if result["results"]:
                    context_parts.append("参考资料：")
                    for i, r in enumerate(result["results"], 1):
                        snippet = r.get("content", "")[:300]
                        context_parts.append(f"{i}. {r.get('title','')} - {snippet}")
                if result["images"]:
                    # 并发检测国内是否可直连，超时 3 秒/张
                    checks = await asyncio.gather(
                        *[_check_url_reachable(url) for url in result["images"][:10]],
                        return_exceptions=True
                    )
                    reachable = [
                        url for url, ok in zip(result["images"][:10], checks)
                        if ok is True
                    ]
                    if reachable:
                        context_parts.append("相关图片链接（国内可访问）：")
                        for url in reachable[:6]:
                            context_parts.append(f"- {url}")
                        context_parts.append("（你可以引用以上信息，并用 [CQ:image,file=图片URL] 发送图片）")
                        print(f"[Tavily] {len(reachable)}/{len(result['images'])} 张图片国内可达")
                    else:
                        context_parts.append("（搜索结果中有图片但国内均不可达，请用文字描述）")
                        print(f"[Tavily] 0/{len(result['images'])} 张图片国内可达，已跳过")
                context_text = "\n".join(context_parts)
                system += "\n\n" + context_text
                print(f"[Tavily] 搜索结果已加入上下文 ({len(result.get('images',[]))} 张图片)")
    else:
        system = (
            PROMPT[persona].format(**fmt)
            + RULES_BASE.format(**fmt)
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