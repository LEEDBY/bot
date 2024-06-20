from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes
from telegram.ext import CallbackContext
from database import upsert_user, get_user

async def start(update: Update, context: CallbackContext) -> None:
    user_id = update.effective_user.id
    username = update.effective_user.username
    upsert_user(user_id, username)
    
    keyboard = [
        [InlineKeyboardButton("Купить", callback_data='buy')],
        [InlineKeyboardButton("Баланс", callback_data='balance')],
        [InlineKeyboardButton("Профиль", callback_data='profile')]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)

    if update.message:
        await update.message.reply_text(
            'Привет! Я бот для продажи XGramm (XGR) токенов.\n'
            'Используйте кнопки ниже для взаимодействия.',
            reply_markup=reply_markup
        )
    elif update.callback_query:
        await update.callback_query.message.reply_text(
            'Привет! Я бот для продажи XGramm (XGR) токенов.\n'
            'Используйте кнопки ниже для взаимодействия.',
            reply_markup=reply_markup
        )