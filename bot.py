import asyncio
import requests
from aiogram import Bot, Dispatcher, types
from aiogram.filters import Command

API_TOKEN = "ВАШ_TELEGRAM_BOT_TOKEN"
HF_MODEL = "gpt2"  # безкоштовна модель, працює без токена

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
        response = requests.post(url, json=payload, timeout=60)
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
