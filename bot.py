import os
import requests
from aiogram import Bot, Dispatcher, types
from aiogram.types import ParseMode

API_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
HF_API_TOKEN = os.getenv("HF_API_TOKEN")

bot = Bot(token=API_TOKEN)
dp = Dispatcher(bot)

HEADERS = {"Authorization": f"Bearer {HF_API_TOKEN}"}
MODEL_URL = "https://api-inference.huggingface.co/models/deepseek-ai/DeepSeek-V3.1"

def query_huggingface(payload):
    response = requests.post(MODEL_URL, headers=HEADERS, json=payload)
    if response.status_code == 200:
        return response.json()
    else:
        return {"error": f"Помилка {response.status_code}: {response.text}"}

@dp.message_handler(commands=["start"])
async def cmd_start(message: types.Message):
    await message.reply("Привіт! Надішліть повідомлення, і я відповім.")

@dp.message_handler()
async def handle_message(message: types.Message):
    user_input = message.text.strip()
    if user_input:
        payload = {"inputs": user_input}
        hf_response = query_huggingface(payload)
        if "error" in hf_response:
            await message.reply(f"Сталася помилка: {hf_response['error']}")
        else:
            await message.reply(hf_response.get("generated_text", "Вибачте, я не зміг згенерувати відповідь."), parse_mode=ParseMode.MARKDOWN)
    else:
        await message.reply("Будь ласка, надішліть текст для обробки.")

if __name__ == "__main__":
    from aiogram import executor
    executor.start_polling(dp, skip_updates=True)
