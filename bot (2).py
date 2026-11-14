import asyncio
import logging
import os

from aiogram import Bot, Dispatcher, F
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode
from aiogram.filters import Command, CommandStart
from aiogram.types import Message
from dotenv import load_dotenv

from jikan import format_anime, random_anime, search_anime

load_dotenv()

BOT_TOKEN = os.getenv("BOT_TOKEN")
if not BOT_TOKEN:
    raise RuntimeError("BOT_TOKEN topilmadi. .env faylga yoki Railway Variables ga qo'shing.")

logging.basicConfig(level=logging.INFO)

bot = Bot(token=BOT_TOKEN, default=DefaultBotProperties(parse_mode=ParseMode.HTML))
dp = Dispatcher()


async def send_anime(message: Message, anime: dict) -> None:
    poster, caption = format_anime(anime)
    if poster:
        await message.answer_photo(photo=poster, caption=caption)
    else:
        await message.answer(caption)


@dp.message(CommandStart())
async def cmd_start(message: Message) -> None:
    await message.answer(
        "👋 Salom! Men anime ma'lumot botiman.\n\n"
        "Anime nomini yozing — poster, reyting va qisqa tavsifini ko'rsataman.\n"
        "🎲 /random — tasodifiy anime"
    )


@dp.message(Command("random"))
async def cmd_random(message: Message) -> None:
    await message.answer("🎲 Qidiryapman...")
    try:
        anime = await random_anime()
    except Exception:
        logging.exception("Jikan random xatosi")
        anime = None

    if not anime:
        await message.answer("❌ Hozir topib bo'lmadi, birozdan keyin urinib ko'ring.")
        return
    await send_anime(message, anime)


@dp.message(F.text & ~F.text.startswith("/"))
async def on_text(message: Message) -> None:
    query = message.text.strip()
    await message.answer("🔎 Qidiryapman...")
    try:
        anime = await search_anime(query)
    except Exception:
        logging.exception("Jikan qidiruv xatosi")
        await message.answer("⚠️ Xatolik yuz berdi, keyinroq urinib ko'ring.")
        return

    if not anime:
        await message.answer("❌ Bunday anime topilmadi. Nomni boshqacha yozib ko'ring.")
        return
    await send_anime(message, anime)


async def main() -> None:
    await bot.delete_webhook(drop_pending_updates=True)
    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())
