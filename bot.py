import os
import requests
from aiogram import Bot, Dispatcher, types
from aiogram.types import ParseMode
from aiogram.utils import executor

# Токен Telegram бота
API_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
if not API_TOKEN:
    raise ValueError("Не знайдено TELEGRAM_BOT_TOKEN у змінних середовища!")

# Токен Hugging Face
HF_API_TOKEN = os.getenv("HF_API_TOKEN")
if not HF_API_TOKEN:
    raise ValueError("Не знайдено HF_API_TOKEN у змінних середовища!")

# Ініціалізація бота та диспетчера
bot = Bot(token=API_TOKEN, parse_mode=ParseMode.HTML)
dp = Dispatcher(bot)

# URL моделі DeepSeek-V3.1 на Hugging Face
HF_API_URL = "https://api-inference.huggingface.co/models/deepseek-ai/DeepSeek-V3.1"
headers = {"Authorization": f"Bearer {HF_API_TOKEN}"}

# Обробник команд /start
@dp.message_handler(commands=["start"])
async def cmd_start(message: types.Message):
    await message.answer("Привіт! Напишіть своє питання, і я спробую на нього відповісти.")

# Обробник текстових повідомлень
@dp.message_handler()
async def handle_message(message: types.Message):
    user_input = message.text.strip()
    if not user_input:
        await message.answer("Будь ласка, введіть текст.")
        return

    payload = {"inputs": user_input}
    try:
        response = requests.post(HF_API_URL, headers=headers, json=payload, timeout=30)
        response.raise_for_status()

        result = response.json()
        if isinstance(result, list) and "generated_text" in result[0]:
            answer = result[0]["generated_text"]
        else:
            answer = "Вибачте, я не зміг зрозуміти ваше питання."

        await message.answer(answer)

    except requests.exceptions.RequestException as e:
        await message.answer(f"Сталася помилка: {str(e)}")

if __name__ == "__main__":
    executor.start_polling(dp, skip_updates=True)
