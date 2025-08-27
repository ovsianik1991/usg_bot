import os
import pandas as pd
import asyncio
import requests
from aiogram import Bot, Dispatcher, types
from aiogram.filters import Command

API_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
GROK_API_KEY = os.getenv("GROK_API_KEY")

if not API_TOKEN or not GROK_API_KEY:
    raise ValueError("Missing TELEGRAM_BOT_TOKEN or GROK_API_KEY environment variable")

bot = Bot(token=API_TOKEN)
dp = Dispatcher()

FAQ_FILE = "faq.csv"
UNKNOWN_FILE = "unknown_questions.csv"

faq = pd.read_csv(FAQ_FILE)
faq_dict = dict(zip(faq['question'], faq['answer']))

if not os.path.exists(UNKNOWN_FILE):
    pd.DataFrame(columns=["question"]).to_csv(UNKNOWN_FILE, index=False)

def ask_grok(question: str) -> str:
    messages = [
        {"role": "system", "content": "Ти FAQ-бот. Відповідай, використовуючи лише дані з бази FAQ. Якщо не знаєш — скажи язково та збережи питання."},
        {"role": "user", "content": question}
    ]
    headers = {
        "Authorization": f"Bearer {GROK_API_KEY}",
        "Content-Type": "application/json"
    }
    data = {
        "model": "grok-beta",  # спробуй також "grok-3-beta" якщо доступна
        "messages": messages,
        "temperature": 0.7,
        "max_tokens": 300
    }
    response = requests.post("https://api.x.ai/v1/chat/completions", headers=headers, json=data, timeout=30)
    response.raise_for_status()
    resp = response.json()
    return resp["choices"][0]["message"]["content"].strip()

@dp.message(Command("start"))
async def start(message: types.Message):
    await message.answer("Привіт! Я FAQ-бот. Спробуй задати питання.")

@dp.message()
async def handle_message(message: types.Message):
    text = message.text.strip()
    try:
        answer = ask_grok(text)
        if "не знайшов" in answer.lower():
            df = pd.read_csv(UNKNOWN_FILE)
            df = pd.concat([df, pd.DataFrame({"question":[text]})], ignore_index=True)
            df.to_csv(UNKNOWN_FILE, index=False)
        await message.answer(answer)
    except requests.HTTPError as e:
        await message.answer(f"AI помилка: {e}")
    except Exception as e:
        await message.answer(f"Неочікувана помилка: {e}")

if __name__ == "__main__":
    asyncio.run(dp.start_polling(bot))
