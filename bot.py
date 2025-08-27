import os
from aiogram import Bot, Dispatcher, F
from aiogram.types import Message, CallbackQuery, InlineKeyboardButton, InlineKeyboardMarkup
from aiogram.utils.keyboard import InlineKeyboardBuilder
from aiogram import flags
import asyncio

# Беремо токен з змінної середовища
API_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
if not API_TOKEN:
    raise ValueError("Не знайдено TELEGRAM_BOT_TOKEN у змінних середовища!")

bot = Bot(token=API_TOKEN)
dp = Dispatcher()

# Приклад бази запитань та відповідей
FAQ = {
    "Як створити акаунт?": "Щоб створити акаунт, натисніть кнопку 'Реєстрація' та заповніть форму.",
    "Як відновити пароль?": "Щоб відновити пароль, натисніть 'Забули пароль?' на сторінці входу.",
    "Як змінити мову інтерфейсу?": "Мову можна змінити в налаштуваннях профілю, розділ 'Мова'."
}

# Створюємо клавіатуру з усіма питаннями
def build_keyboard():
    kb = InlineKeyboardBuilder()
    for question in FAQ.keys():
        kb.button(text=question, callback_data=question)
    kb.adjust(1)  # по 1 кнопці в рядку
    return kb.as_markup()

# Стартова команда
@dp.message(Command("start"))
async def cmd_start(message: Message):
    await message.answer(
        "Привіт! Ось список запитань. Натисни на потрібне питання, щоб отримати відповідь:",
        reply_markup=build_keyboard()
    )

# Обробка натискань кнопок
@dp.callback_query(F.data.in_(FAQ.keys()))
async def handle_faq(callback: CallbackQuery):
    question = callback.data
    answer = FAQ[question]
    await callback.message.edit_text(f"❓ {question}\n\n💡 {answer}")

# Запуск бота
if __name__ == "__main__":
    import asyncio
    from aiogram import executor
    asyncio.run(dp.start_polling(bot))
