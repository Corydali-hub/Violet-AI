"""
Tavily 搜索 API 封装 — 异步调用，返回搜索结果与图片 URL。
"""

import json
import aiohttp

TAVILY_URL = "https://api.tavily.com/search"


async def search(query: str, api_key: str) -> dict:
    """
    调用 Tavily Search API，返回包含 answer / results / images 的字典。
    失败时返回 {"answer": "", "results": [], "images": []}。
    """
    payload = {
        "api_key": api_key,
        "query": query,
        "search_depth": "advanced",
        "include_images": True,
        "include_answer": True,
        "max_results": 5,
    }

    try:
        async with aiohttp.ClientSession() as session:
            async with session.post(TAVILY_URL, json=payload, timeout=15) as resp:
                if resp.status != 200:
                    text = await resp.text()
                    print(f"[Tavily] API 错误 {resp.status}: {text[:200]}")
                    return {"answer": "", "results": [], "images": []}
                data = await resp.json()
                return {
                    "answer": data.get("answer", ""),
                    "results": data.get("results", []),
                    "images": data.get("images", []),
                }
    except Exception as e:
        print(f"[Tavily] 请求异常: {e}")
        return {"answer": "", "results": [], "images": []}
