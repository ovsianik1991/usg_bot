
import csv
import difflib
from aiogram import Bot, Dispatcher, types
from aiogram.utils import executor

# ==== ВАШ TELEGRAM TOKEN ====
API_TOKEN = "8480419956:AAHHOx-nZdZFxjYKtyYJbxvZ1GXF-rZ7NkU"

# ==== Загружаем FAQ из CSV ====
faq = []
with open("faq.csv", "r", encoding="utf-8") as f:
    reader = csv.DictReader(f)
    for row in reader:
        faq.append({"question": row["question"], "answer": row["answer"]})

# ==== Создаем бота ====
bot = Bot(token=API_TOKEN)
dp = Dispatcher(bot)

def find_answer(user_q: str):
    questions = [item["question"] for item in faq]
    # ищем похожие вопросы
    match = difflib.get_close_matches(user_q, questions, n=1, cutoff=0.4)
    if match:
        q = match[0]
        for item in faq:
            if item["question"] == q:
                return item["answer"]
    return None

@dp.message_handler()
async def handle_message(message: types.Message):
    user_q = message.text.strip()
    answer = find_answer(user_q)
    if answer:
        await message.answer(answer)
    else:
        await message.answer("❓ Вибачте, я не знайшов відповіді. Спробуйте інакше сформулювати питання.")

if __name__ == "__main__":
    executor.start_polling(dp, skip_updates=True)
