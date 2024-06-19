from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    keyboard = [
        [InlineKeyboardButton("Купить", callback_data='buy')],
        [InlineKeyboardButton("Баланс", callback_data='balance')],
        [InlineKeyboardButton("Профиль", callback_data='profile')]
    ]

    reply_markup = InlineKeyboardMarkup(keyboard)

    welcome_message = "Привет! Я бот для продажи XGramm (XGR) токенов. Используйте кнопки ниже для взаимодействия."
    await update.message.reply_text(welcome_message, reply_markup=reply_markup)
