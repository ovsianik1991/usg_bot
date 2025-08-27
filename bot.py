import os
import pandas as pd
import asyncio
from aiogram import Bot, Dispatcher, types
from aiogram.filters import Command
from difflib import get_close_matches

API_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")

bot = Bot(token=API_TOKEN)
dp = Dispatcher()

# Адмін для оновлення FAQ
ADMIN_ID = 123456789  # <-- замініть на свій Telegram ID

# Файли
FAQ_FILE = "faq.csv"
UNKNOWN_FILE = "unknown_questions.csv"

# Завантажуємо FAQ
faq = pd.read_csv(FAQ_FILE)
questions_list = [q.lower() for q in faq['question']]

# Створимо unknown файл, якщо його немає
if not os.path.exists(UNKNOWN_FILE):
    pd.DataFrame(columns=["question"]).to_csv(UNKNOWN_FILE, index=False)

@dp.message(Command("start"))
async def start(message: types.Message):
    await message.answer(
        "Привіт! Я FAQ-бот 🚂\nНапишіть своє питання, і я спробую знайти відповідь."
    )

@dp.message()
async def answer(message: types.Message):
    user_question = message.text.strip().lower()
    
    match = get_close_matches(user_question, questions_list, n=1, cutoff=0.4)
    if match:
        response = faq.loc[faq['question'].str.lower() == match[0], 'answer'].values[0]
        await message.answer(response)
    else:
        # Пропонуємо схожі питання
        suggestions = get_close_matches(user_question, questions_list, n=3, cutoff=0.3)
        if suggestions:
            suggestion_text = "\n".join(f"- {s}" for s in suggestions)
            await message.answer(
                "Вибачте, я не знайшов точної відповіді 🤔\nМожливо, ви мали на увазі одне з цих питань:\n" + suggestion_text
            )
        else:
            await message.answer("Вибачте, я не знайшов відповіді 🤔\nВаше питання буде збережено для подальшого аналізу.")
            
            # Логування нового питання
            unknown_df = pd.read_csv(UNKNOWN_FILE)
            unknown_df = pd.concat([unknown_df, pd.DataFrame({"question": [message.text.strip()]})], ignore_index=True)
            unknown_df.to_csv(UNKNOWN_FILE, index=False)

# Команда для додавання питання до FAQ (тільки адміністратор)
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

        # Оновлюємо список питань
        questions_list.append(question.lower())

        await message.answer(f"✅ Питання додано до FAQ:\n{question}")

    except Exception as e:
        await message.answer(f"Помилка: {e}")

async def main():
    print("Бот запущено і чекає повідомлень...")
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
