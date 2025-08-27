import os
import pandas as pd
import asyncio
from aiogram import Bot, Dispatcher, types
from aiogram.filters import Command
from sentence_transformers import SentenceTransformer
from sklearn.metrics.pairwise import cosine_similarity
import numpy as np

API_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")

bot = Bot(token=API_TOKEN)
dp = Dispatcher()

ADMIN_ID = 123456789  # <-- замініть на свій Telegram ID

FAQ_FILE = "faq.csv"
UNKNOWN_FILE = "unknown_questions.csv"

# Завантажуємо FAQ
faq = pd.read_csv(FAQ_FILE)
questions_list = faq['question'].tolist()

# Створюємо unknown файл, якщо його немає
if not os.path.exists(UNKNOWN_FILE):
    pd.DataFrame(columns=["question"]).to_csv(UNKNOWN_FILE, index=False)

# NLP модель для ембеддінгів
model = SentenceTransformer('paraphrase-multilingual-MiniLM-L12-v2')
faq_embeddings = model.encode(questions_list)

@dp.message(Command("start"))
async def start(message: types.Message):
    await message.answer(
        "Привіт! Я FAQ-бот 🚂\nНапишіть своє питання, і я спробую знайти відповідь."
    )

@dp.message()
async def answer(message: types.Message):
    user_question = message.text.strip()

    # Ембеддінг питання користувача
    user_emb = model.encode([user_question])
    
    # Косинусна схожість
    similarities = cosine_similarity(user_emb, faq_embeddings)[0]
    best_idx = np.argmax(similarities)
    
    # Поріг схожості
    if similarities[best_idx] >= 0.6:
        response = faq.iloc[best_idx]['answer']
        await message.answer(response)
    else:
        # Показуємо топ-3 схожих питання
        top_indices = similarities.argsort()[-3:][::-1]
        top_scores = similarities[top_indices]
        
        suggestions = []
        for idx, score in zip(top_indices, top_scores):
            if score >= 0.3:  # мінімальна схожість для підказки
                suggestions.append(f"- {faq.iloc[idx]['question']}")
        
        if suggestions:
            suggestion_text = "\n".join(suggestions)
            await message.answer(
                "Вибачте, я не знайшов точної відповіді 🤔\nМожливо, ви мали на увазі одне з цих питань:\n" + suggestion_text
            )
        else:
            await message.answer("Вибачте, я не знайшов відповіді 🤔\nВаше питання буде збережено для подальшого аналізу.")
            
            # Логування нового питання
            unknown_df = pd.read_csv(UNKNOWN_FILE)
            unknown_df = pd.concat([unknown_df, pd.DataFrame({"question": [user_question]})], ignore_index=True)
            unknown_df.to_csv(UNKNOWN_FILE, index=False)

# Команда для додавання питання до FAQ
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

        # Оновлюємо вектори
        global faq_embeddings, questions_list
        questions_list.append(question)
        faq_embeddings = model.encode(questions_list)

        await message.answer(f"✅ Питання додано до FAQ:\n{question}")

    except Exception as e:
        await message.answer(f"Помилка: {e}")

async def main():
    print("Бот запущено і чекає повідомлень...")
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
