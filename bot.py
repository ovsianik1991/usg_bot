import os
import requests
import csv
import asyncio
from aiogram import Bot, Dispatcher, types
from aiogram.client.bot import DefaultBotProperties
from aiogram.filters import Command

# ==== Токени з змінних середовища ====
API_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
HF_API_TOKEN = os.getenv("HF_API_TOKEN")

if not API_TOKEN:
    raise ValueError("Не знайдено TELEGRAM_BOT_TOKEN у змінних середовища!")

if not HF_API_TOKEN:
    raise ValueError("Не знайдено HF_API_TOKEN у змінних середовища!")

# ==== Завантажуємо FAQ з CSV ====
faq = []
with open("faq.csv", "r", encoding="utf-8") as f:
    reader = csv.DictReader(f)
    for row in reader:
        faq.append({"question": row["question"], "answer": row["answer"]})

# ==== Створюємо бота та диспетчер ====
bot = Bot(token=API_TOKEN, default=DefaultBotProperties(parse_mode="HTML"))
dp = Dispatcher()

# ==== Функція для пошуку відповіді в FAQ ====
def find_faq_answer(user_question: str):
    for item in faq:
        if user_question.lower() in item["question"].lower():
            return item["answer"]
    return None

# ==== Функція для Hugging Face API ====
def ask_hf_model(prompt: str):
    url = "https://api-inference.huggingface.co/models/deepseek-ai/DeepSeek-V3.1"
    headers = {"Authorization": f"Bearer {HF_API_TOKEN}"}
    payload = {"inputs": prompt}

    response = requests.post(url, headers=headers, json=payload, timeout=30)
    response.raise_for_status()

    data = response.json()
    if isinstance(data, list) and "generated_text" in data[0]:
        return data[0]["generated_text"]
    elif isinstance(data, dict) and "error" in data:
        return f"Помилка AI: {data['error']}"
    else:
        return "Помилка AI: неочікуваний формат відповіді"

# ==== Обробка команд ====
@dp.message(Command(commands=["start"]))
async def cmd_start(message: types.Message):
    await message.answer("Привіт! Я ваш AI-асистент. Задавайте питання.")

# ==== Обробка всіх повідомлень ====
@dp.message()
async def handle_message(message: types.Message):
    user_question = message.text.strip()
    answer = find_faq_answer(user_question)

    if answer:
        await message.answer(answer)
    else:
        try:
            ai_answer = ask_hf_model(user_question)
            await message.answer(ai_answer)
        except requests.HTTPError as e:
            await message.answer(f"Сталася помилка: {e}")
        except Exception as e:
            await message.answer(f"Сталася помилка: {e}")

# ==== Запуск бота ====
if __name__ == "__main__":
    asyncio.run(dp.start_polling(bot))
