import os
import asyncio
import requests
from aiogram import Bot, Dispatcher, types
from aiogram.filters import Command

# Telegram токен (змінна середовища)
API_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
if not API_TOKEN:
    raise ValueError("Не знайдено TELEGRAM_BOT_TOKEN у змінних середовища!")

# Hugging Face API токен (змінна середовища)
HF_API_TOKEN = os.getenv("HF_API_TOKEN")
if not HF_API_TOKEN:
    raise ValueError("Не знайдено HF_API_TOKEN у змінних середовища!")

HEADERS = {"Authorization": f"Bearer {HF_API_TOKEN}"}
HF_MODEL = "gpt2"  # безкоштовна модель для тесту

bot = Bot(token=API_TOKEN)
dp = Dispatcher()

@dp.message(Command("start"))
async def start(message: types.Message):
    await message.answer("Привіт! Я AI FAQ-бот 🚂\nЗадай своє питання українською.")

def get_ai_answer(question):
    url = f"https://api-inference.huggingface.co/models/{HF_MODEL}"
    payload = {
        "inputs": f"Ти помічник зі страхових питань. Відповідай українською.\nПитання: {question}\nВідповідь:"
    }
    try:
        response = requests.post(url, json=payload, headers=HEADERS, timeout=60)
        response.raise_for_status()
        data = response.json()
        if isinstance(data, list) and "generated_text" in data[0]:
            return data[0]["generated_text"].strip()
        elif isinstance(data, dict) and "error" in data:
            return f"Помилка AI: {data['error']}"
        else:
            return "Вибачте, AI не зміг згенерувати відповідь."
    except Exception as e:
        return f"Сталася помилка: {e}"

@dp.message()
async def handle_question(message: types.Message):
    question = message.text.strip()
    answer = get_ai_answer(question)
    await message.answer(answer)

async def main():
    print("Бот запущено і чекає повідомлень...")
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
