import os
import requests
from aiogram import Bot, Dispatcher, types
from aiogram.filters import Command
from aiogram.enums import ParseMode
from aiogram.utils.keyboard import ReplyKeyboardBuilder
from aiogram.types import Message

# ==== TELEGRAM TOKEN ====
API_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
if not API_TOKEN:
    raise ValueError("Не знайдено TELEGRAM_BOT_TOKEN у змінних середовища!")

# ==== HUGGING FACE TOKEN ====
HF_API_TOKEN = os.getenv("HF_API_TOKEN")
if not HF_API_TOKEN:
    raise ValueError("Не знайдено HF_API_TOKEN у змінних середовища!")

HF_MODEL = "deepseek-ai/DeepSeek-V3.1"  # Модель HF

bot = Bot(token=API_TOKEN, parse_mode=ParseMode.HTML)
dp = Dispatcher()

# ==== Запит до Hugging Face API ====
def generate_answer(question: str) -> str:
    url = f"https://api-inference.huggingface.co/models/{HF_MODEL}"
    headers = {"Authorization": f"Bearer {HF_API_TOKEN}"}
    payload = {"inputs": question}
    try:
        response = requests.post(url, headers=headers, json=payload, timeout=60)
        response.raise_for_status()
        data = response.json()
        # Hugging Face може повертати список результатів
        if isinstance(data, list) and len(data) > 0 and "generated_text" in data[0]:
            return data[0]["generated_text"]
        elif isinstance(data, dict) and "error" in data:
            return f"Помилка AI: {data['error']}"
        return str(data)
    except requests.exceptions.RequestException as e:
        return f"Сталася помилка: {e}"

# ==== Команди бота ====
@dp.message(Command(commands=["start", "help"]))
async def cmd_start(message: Message):
    await message.answer("Привіт! Я AI-FAQ бот. Задайте своє питання, і я спробую відповісти.")

# ==== Обробка текстових повідомлень ====
@dp.message()
async def handle_message(message: Message):
    question = message.text.strip()
    if not question:
        await message.answer("❗ Будь ласка, введіть запитання.")
        return

    await message.answer("⌛ Працюю над відповіддю...")
    answer = generate_answer(question)
    await message.answer(answer)

if __name__ == "__main__":
    import asyncio
    asyncio.run(dp.start_polling(bot))
