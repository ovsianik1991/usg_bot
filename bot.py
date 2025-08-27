import os
import pandas as pd
import asyncio
import requests
from aiogram import Bot, Dispatcher, types
from aiogram.filters import Command

# Беремо токени з змінних середовища
API_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
GROK_API_KEY = os.getenv("GROK_API_KEY")

if not API_TOKEN or not GROK_API_KEY:
    raise ValueError("Missing TELEGRAM_BOT_TOKEN or GROK_API_KEY environment variable")

bot = Bot(token=API_TOKEN)
dp = Dispatcher()

ADMIN_ID = 123456789  # Замініть на свій Telegram ID

FAQ_FILE = "faq_new.csv"
UNKNOWN_FILE = "unknown_questions.csv"

# Завантажуємо FAQ
faq = pd.read_csv(FAQ_FILE)
faq_dict = dict(zip(faq['question'], faq['answer']))

# Створюємо unknown файл, якщо його немає
if not os.path.exists(UNKNOWN_FILE):
    pd.DataFrame(columns=["question"]).to_csv(UNKNOWN_FILE, index=False)

# Функція для запиту до Grok API
def ask_grok(question):
    data = {
        "messages": [
            {"role": "user", "content": question}
        ],
        "model": "grok-4",
        "stream": False,
        "temperature": 0.7
    }

    headers = {
        "Authorization": f"Bearer {GROK_API_KEY}",
        "Content-Type": "application/json"
    }

    try:
        response = requests.post("https://api.x.ai/v1/chat/completions", headers=headers, json=data)
        response.raise_for_status()
        return response.json()["choices"][0]["message"]["content"].strip()
    except Exception as e:
        return f"Помилка при запиті до AI: {e}"

@dp.message(Command("start"))
async def start(message: types.Message):
    await message.answer("Привіт! Я FAQ-бот 🚂\nНапишіть своє питання, і я спробую знайти відповідь.")

@dp.message()
async def answer(message: types.Message):
    user_question = message.text.strip()

    # Запит до Grok
    response = ask_grok(user_question)

    # Якщо AI не знайшов відповідь
    if "не знайшов відповіді" in response.lower():
        unknown_df = pd.read_csv(UNKNOWN_FILE)
        unknown_df = pd.concat([unknown_df, pd.DataFrame({"question": [user_question]})], ignore_index=True)
        unknown_df.to_csv(UNKNOWN_FILE, index=False)

    await message.answer(response)

# Додати питання до FAQ
@dp.message(Command("add"))
async def add_to_faq(message: types.Message):
    if message.from_user.id != ADMIN_ID:
        await message.answer("У вас немає прав для цієї команди.")
        return

    try:
        parts = message.text.split("|")
        if len(parts) != 3:
            await message.answer("Використання: /add питання | відповідь | підтвердження")
            return
        
        _, question, answer = parts
        question = question.strip()
        answer = answer.strip()

        new_row = pd.DataFrame({"question": [question], "answer": [answer]})
        faq_df = pd.read_csv(FAQ_FILE)
        faq_df = pd.concat([faq_df, new_row], ignore_index=True)
        faq_df.to_csv(FAQ_FILE, index=False)

        global faq_dict
        faq_dict[question] = answer

        await message.answer(f"✅ Питання додано до FAQ:\n{question}")

    except Exception as e:
        await message.answer(f"Помилка: {e}")

async def main():
    print("Бот запущено і чекає повідомлень...")
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
