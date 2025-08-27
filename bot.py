import csv
import os
import asyncio
from aiogram import Bot, Dispatcher, types
from aiogram.client.bot import DefaultBotProperties
from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup
from aiogram.filters import Command, CallbackQuery

# ==== Токен з змінних середовища ====
API_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
if not API_TOKEN:
    raise ValueError("Не знайдено TELEGRAM_BOT_TOKEN у змінних середовища!")

# ==== Завантаження FAQ ====
faq = []
with open("faq.csv", "r", encoding="utf-8") as f:
    reader = csv.DictReader(f)
    for row in reader:
        faq.append({"question": row["question"], "answer": row["answer"]})

# ==== Налаштування пагінації ====
PAGE_SIZE = 5  # скільки питань на сторінку

def generate_buttons(page=0):
    keyboard = InlineKeyboardMarkup(row_width=1)
    start_idx = page * PAGE_SIZE
    end_idx = start_idx + PAGE_SIZE
    for idx, item in enumerate(faq[start_idx:end_idx], start=start_idx):
        keyboard.add(InlineKeyboardButton(text=item["question"], callback_data=f"faq_{idx}"))
    # Кнопки навігації
    nav_buttons = []
    if page > 0:
        nav_buttons.append(InlineKeyboardButton("⬅️ Назад", callback_data=f"page_{page-1}"))
    if end_idx < len(faq):
        nav_buttons.append(InlineKeyboardButton("Вперед ➡️", callback_data=f"page_{page+1}"))
    if nav_buttons:
        keyboard.row(*nav_buttons)
    return keyboard

# ==== Створення бота та диспетчера ====
bot = Bot(token=API_TOKEN, default=DefaultBotProperties(parse_mode="HTML"))
dp = Dispatcher()

# ==== Стартова команда ====
@dp.message(Command(commands=["start"]))
async def cmd_start(message: types.Message):
    await message.answer(
        "Привіт! Виберіть питання, щоб отримати відповідь:",
        reply_markup=generate_buttons(page=0)
    )

# ==== Обробка натискання на кнопку ====
@dp.callback_query(CallbackQuery.filter())
async def handle_callback(query: types.CallbackQuery):
    data = query.data
    if data.startswith("faq_"):
        idx = int(data.split("_")[1])
        answer = faq[idx]["answer"]
        await query.message.answer(answer)
        await query.answer()  # закриваємо "loading" на кнопці
    elif data.startswith("page_"):
        page = int(data.split("_")[1])
        await query.message.edit_reply_markup(reply_markup=generate_buttons(page))
        await query.answer()

# ==== Запуск бота ====
if __name__ == "__main__":
    asyncio.run(dp.start_polling(bot))
