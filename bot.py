import os
import asyncio
import requests
from aiogram import Bot, Dispatcher, types
from aiogram.filters import Command

API_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
HF_TOKEN = os.getenv("HUGGINGFACE_API_TOKEN")
HF_MODEL = "tiiuae/falcon-7b-instruct"  # Можна іншу модель

bot = Bot(token=API_TOKEN)
dp = Dispatcher()

ADMIN_ID = 123456789  # <-- Ваш Telegram ID
UNKNOWN_FILE = "unknown_questions.csv"

# Створюємо unknown файл, якщо його немає
import pandas as pd
if not os.path.exists(UNKNOWN_FILE):
    pd.DataFrame(columns=["question"]).to_csv(UNKNOWN_FILE, index=False)

def get_ai_answer(user_question):
    headers = {"Authorization": f"Bearer {HF_TOKEN}"}
    data = {
        "inputs": f"Ти помічник зі страхових питань. Відповідай українською.\nПитання: {user_question}\nВідповідь:"
    }
    response = requests.post(
        f"https://api-inference.huggingface.co/models/{HF_MODEL}",
        headers=headers,
        json=data,
        timeout=30
    )
    try:
        return response.json()[0]['generated_text'].strip()
    except:
        return "Вибачте, сталася помилка при генерації відповіді."

@dp.message(Command("start"))
async def start(message: types.Message):
    await message.answer("Привіт! Я AI FAQ-бот 🚂\nЗадай своє питання українською.")

@dp.message()
async def handle_question(message: types.Message):
    user_question = message.text.strip()
    answer = get_ai_answer(user_question)
    
    if not answer:
        await message.answer("Вибачте, я не зміг знайти відповідь. Питання буде збережено.")
        unknown_df = pd.read_csv(UNKNOWN_FILE)
        unknown_df = pd.concat([unknown_df, pd.DataFrame({"question": [user_question]})], ignore_index=True)
        unknown_df.to_csv(UNKNOWN_FILE, index=False)
    else:
        await message.answer(answer)

async def main():
    print("Бот запущено і чекає повідомлень...")
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
