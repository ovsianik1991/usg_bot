import os
import csv
import hashlib
from aiogram import Bot, Dispatcher, F
from aiogram.types import Message, CallbackQuery
from aiogram.filters import Command
from aiogram.utils.keyboard import InlineKeyboardBuilder
import asyncio

API_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
if not API_TOKEN:
    raise ValueError("Не знайдено TELEGRAM_BOT_TOKEN у змінних середовища!")

bot = Bot(token=API_TOKEN)
dp = Dispatcher()

# Завантажуємо FAQ з CSV
FAQ = {}
QUESTION_MAP = {}  # question_id -> question_text

with open("faq_new.csv", newline="", encoding="utf-8") as csvfile:
    reader = csv.reader(csvfile)
    for row in reader:
        if len(row) >= 2:
            question, answer = row[0], row[1]
            # створюємо короткий ключ (до 32 символів)
            qid = hashlib.md5(question.encode()).hexdigest()[:32]
            FAQ[qid] = answer
            QUESTION_MAP[qid] = question

def build_keyboard():
    kb = InlineKeyboardBuilder()
    for qid, question in QUESTION_MAP.items():
        kb.button(text=question, callback_data=qid)
    kb.adjust(1)
    return kb.as_markup()

@dp.message(Command("start"))
async def cmd_start(message: Message):
    await message.answer(
        "Привіт! Ось список запитань. Натисни на потрібне питання, щоб отримати відповідь:",
        reply_markup=build_keyboard()
    )

@dp.callback_query(F.data.in_(FAQ.keys()))
async def handle_faq(callback: CallbackQuery):
    qid = callback.data
    question = QUESTION_MAP[qid]
    answer = FAQ[qid]
    await callback.message.edit_text(
        f"❓ {question}\n\n💡 {answer}",
        reply_markup=build_keyboard()
    )

if __name__ == "__main__":
    asyncio.run(dp.start_polling(bot))
