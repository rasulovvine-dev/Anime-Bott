import aiohttp

BASE_URL = "https://api.jikan.moe/v4"


async def _get(path: str, params: dict | None = None) -> dict | None:
    timeout = aiohttp.ClientTimeout(total=15)
    async with aiohttp.ClientSession(timeout=timeout) as session:
        async with session.get(f"{BASE_URL}{path}", params=params) as resp:
            if resp.status != 200:
                return None
            return await resp.json()


async def search_anime(query: str) -> dict | None:
    """Nom bo'yicha eng mos animeni qaytaradi."""
    data = await _get("/anime", {"q": query, "limit": 1, "sfw": "true"})
    if not data or not data.get("data"):
        return None
    return data["data"][0]


async def random_anime() -> dict | None:
    """Tasodifiy anime qaytaradi."""
    data = await _get("/random/anime")
    if not data or not data.get("data"):
        return None
    return data["data"]


def format_anime(anime: dict) -> tuple[str | None, str]:
    """(poster_url, caption) qaytaradi."""
    title = anime.get("title_english") or anime.get("title") or "Noma'lum"
    score = anime.get("score") or "—"
    episodes = anime.get("episodes") or "?"
    year = anime.get("year") or "—"
    genres = ", ".join(g["name"] for g in anime.get("genres", [])) or "—"

    synopsis = anime.get("synopsis") or "Tavsif mavjud emas."
    if len(synopsis) > 400:
        synopsis = synopsis[:400].rsplit(" ", 1)[0] + "..."

    poster = (
        anime.get("images", {}).get("jpg", {}).get("large_image_url")
        or anime.get("images", {}).get("jpg", {}).get("image_url")
    )

    caption = (
        f"🎬 <b>{title}</b>\n"
        f"⭐ Reyting: {score}\n"
        f"📺 Epizodlar: {episodes}\n"
        f"📅 Yil: {year}\n"
        f"🎭 Janrlar: {genres}\n\n"
        f"{synopsis}"
    )
    # Telegram caption limiti 1024 belgi
    return poster, caption[:1024]
