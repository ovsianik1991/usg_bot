import os
import pandas as pd
import asyncio
import requests
from aiogram import Bot, Dispatcher, types
from aiogram.filters import Command

# Токени з оточення
API_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
GROK_API_KEY = os.getenv("GROK_API_KEY")  # Ключ API Grok з перемінних

bot = Bot(token=API_TOKEN)
dp = Dispatcher()

ADMIN_ID = 123456789  # заміни на свій Telegram ID

FAQ_FILE = "faq.csv"
UNKNOWN_FILE = "unknown_questions.csv"

# Завантажуємо FAQ
faq = pd.read_csv(FAQ_FILE)
faq_dict = dict(zip(faq['question'], faq['answer']))

# Створюємо unknown файл, якщо його немає
if not os.path.exists(UNKNOWN_FILE):
    pd.DataFrame(columns=["question"]).to_csv(UNKNOWN_FILE, index=False)

# Функція для запиту до Grok API
def ask_grok(question):
    messages = [
        {
            "role": "system",
            "content": (
                "Ти FAQ-бот для компанії. Твоя задача — відповідати на питання користувачів, "
                "використовуючи лише базу FAQ. Якщо питання не відповідає жодному з FAQ, "
                "скажи: 'Вибачте, я не знайшов відповіді 🤔\nВаше питання буде збережено для подальшого аналізу.'\n\n"
                "Ось база FAQ:\n" +
                "\n".join([f"Питання: {q}\nВідповідь: {a}" for q, a in faq_dict.items()])
            )
        },
        {"role": "user", "content": question}
    ]

    headers = {
        "Authorization": f"Bearer {GROK_API_KEY}",
        "Content-Type": "application/json"
    }

    data = {
        "model": "grok-beta",   # модель X.ai (може бути інша, залежить від акаунту)
        "messages": messages,
        "temperature": 0.7,
        "max_tokens": 300
    }

    try:
        response = requests.post(
            "https://api.x.ai/v1/chat/completions",
            headers=headers,
            json=data
        )
        response.raise_for_status()
        return response.json()["choices"][0]["message"]["content"].strip()
    except Exception as e:
        return f"Помилка при запиті до AI: {e}"

# /start
@dp.message(Command("start"))
async def start(message: types.Message):
    await message.answer("Привіт! Я FAQ-бот 🚂\nНапишіть своє питання, і я спробую знайти відповідь.")

# Основний хендлер
@dp.message()
async def answer(message: types.Message):
    user_question = message.text.strip()
    
    response = ask_grok(user_question)

    # Якщо Grok не знайшов відповідь — записуємо
    if "не знайшов відповіді" in response.lower():
        unknown_df = pd.read_csv(UNKNOWN_FILE)
        unknown_df = pd.concat([unknown_df, pd.DataFrame({"question": [user_question]})], ignore_index=True)
        unknown_df.to_csv(UNKNOWN_FILE, index=False)
    
    await message.answer(response)

# /add — додавання нового питання/відповіді
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

        # Додаємо до FAQ
        new_row = pd.DataFrame({"question": [question], "answer": [answer]})
        faq_df = pd.read_csv(FAQ_FILE)
        faq_df = pd.concat([faq_df, new_row], ignore_index=True)
        faq_df.to_csv(FAQ_FILE, index=False)

        # Оновлюємо словник FAQ
        global faq_dict
        faq_dict[question] = answer

        await message.answer(f"✅ Питання додано до FAQ:\n{question}")

    except Exception as e:
        await message.answer(f"Помилка: {e}")

# Запуск
async def main():
    print("Бот запущено і чекає повідомлень...")
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
