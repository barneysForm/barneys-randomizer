# bot.py
import logging
import os
import random
from aiogram import Bot, Dispatcher, types
from aiogram.utils import executor
from db import init_db, add_participant, list_participants

logging.basicConfig(level=logging.INFO)
init_db()

API_TOKEN = os.environ.get("API_TOKEN")  # вставишь токен в Render в переменных окружения
CHANNELS = [os.environ.get("CHANNEL_USERNAME", "@barneysform")]  # юзернейм канала

if not API_TOKEN:
    raise RuntimeError("API_TOKEN is not set in environment variables")

bot = Bot(token=API_TOKEN)
dp = Dispatcher(bot)

@dp.message_handler(commands=["start"])
async def cmd_start(message: types.Message):
    kb = types.ReplyKeyboardMarkup(resize_keyboard=True)
    kb.add(
        types.KeyboardButton(
            "Участвовать",
            web_app=types.WebAppInfo(
                url=os.environ.get("WEBAPP_URL", "https://your-webapp-url.vercel.app")
            )
        )
    )
    await message.answer(
        "Нажми кнопку «Участвовать», чтобы проверить подписку и зарегистрироваться.",
        reply_markup=kb
    )

@dp.message_handler(content_types=types.ContentType.WEB_APP_DATA)
async def web_app_data_handler(message: types.Message):
    user = message.from_user
    user_id = user.id
    not_subscribed = []

    for ch in CHANNELS:
        try:
            member = await bot.get_chat_member(chat_id=ch, user_id=user_id)
            if member.status in ("left", "kicked"):
                not_subscribed.append(ch)
        except Exception as e:
            await message.answer(
                f"⚠️ Ошибка при проверке {ch}. Убедись, что бот — админ канала."
            )
            return

    if not_subscribed:
        await message.answer("❌ Вы не подписаны на: " + ", ".join(not_subscribed))
        return

    add_participant(
        user_id,
        getattr(user, "username", ""),
        getattr(user, "first_name", "")
    )

    await message.answer("✅ Ты успешно зарегистрирован(а) в розыгрыше! 🎉")

@dp.message_handler(commands=["count"])
async def cmd_count(message: types.Message):
    n = len(list_participants())
    await message.answer(f"Участников: {n}")

@dp.message_handler(commands=["draw"])
async def cmd_draw(message: types.Message):
    parts = list_participants()
    if not parts:
        await message.answer("Нет участников.")
        return
    winner = random.choice(parts)
    user_id, username, first_name, joined_at = winner

    mention = (
        f"[{first_name}](tg://user?id={user_id})"
        if first_name else
        f"@{username}" if username else
        str(user_id)
    )

    await message.answer(f"🏆 Победитель: {mention}\nПоздравляем!", parse_mode="Markdown")

if __name__ == "__main__":
    executor.start_polling(dp, skip_updates=True)
