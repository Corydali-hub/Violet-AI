"""
网易云音乐搜索 — 调用公开 API 查找歌曲。
"""

import json

import aiohttp

NETEASE_SEARCH_URL = "https://music.163.com/api/search/get"

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    "Referer": "https://music.163.com/",
    "Accept": "application/json, text/plain, */*",
}


async def search_song(query: str, limit: int = 3) -> list[dict]:
    """
    搜索歌曲，返回 [{id, name, artists, album}, ...]。
    失败或空结果返回空列表。
    """
    params = {
        "s": query,
        "type": 1,      # 1 = 单曲
        "limit": limit,
        "offset": 0,
    }
    try:
        async with aiohttp.ClientSession() as session:
            async with session.get(
                NETEASE_SEARCH_URL,
                params=params,
                headers=HEADERS,
                timeout=aiohttp.ClientTimeout(total=8),
            ) as resp:
                if resp.status != 200:
                    print(f"[Netease] HTTP {resp.status}")
                    return []
                # 网易 API 有时返回 text/plain 而非 application/json
                text = await resp.text()
                data = json.loads(text)
    except Exception as e:
        print(f"[Netease] 搜索异常: {e}")
        return []

    songs = data.get("result", {}).get("songs")
    if not songs:
        return []

    results = []
    for s in songs[:limit]:
        artists = ", ".join(a["name"] for a in s.get("artists", []))
        results.append({
            "id": s["id"],
            "name": s["name"],
            "artists": artists,
            "album": s.get("album", {}).get("name", ""),
        })
    return results
