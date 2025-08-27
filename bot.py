import os
import asyncio
import requests
from aiogram import Bot, Dispatcher, types
from aiogram.filters import Command

API_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
HF_TOKEN = os.getenv("HUGGINGFACE_API_TOKEN")
HF_MODEL = "TheBloke/wizardLM-7B-uncensored-HF"  # безкоштовна і робоча модель

bot = Bot(token=API_TOKEN)
dp = Dispatcher()

@dp.message(Command("start"))
async def start(message: types.Message):
    await message.answer("Привіт! Я AI FAQ-бот 🚂\nЗадай своє питання українською.")

def get_ai_answer(user_question):
    headers = {"Authorization": f"Bearer {HF_TOKEN}"}
    data = {"inputs": f"Ти помічник зі страхових питань. Відповідай українською.\nПитання: {user_question}\nВідповідь:"}

    try:
        response = requests.post(
            f"https://api-inference.huggingface.co/models/{HF_MODEL}",
            headers=headers,
            json=data,
            timeout=60
        )
        result = response.json()
        if isinstance(result, list) and "generated_text" in result[0]:
            return result[0]["generated_text"].strip()
        elif isinstance(result, dict) and "error" in result:
            return f"Помилка AI: {result['error']}"
        else:
            return "Вибачте, AI не зміг згенерувати відповідь."
    except Exception as e:
        return f"Вибачте, сталася помилка при генерації відповіді: {e}"

@dp.message()
async def handle_question(message: types.Message):
    user_question = message.text.strip()
    answer = get_ai_answer(user_question)
    await message.answer(answer)

async def main():
    print("Бот запущено і чекає повідомлень...")
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
