from telegram import Update, InlineKeyboardMarkup, InlineKeyboardButton
from telegram.ext import CallbackContext
from database import upsert_user, get_user
from handlers.profile_handlers import profile

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
    await update.message.reply_text(
        'Привет! Я бот для продажи XGramm (XGR) токенов.\n'
        'Используйте кнопки ниже для взаимодействия.',
        reply_markup=reply_markup
    )

async def start_from_callback(update: Update, context: CallbackContext) -> None:
    query = update.callback_query
    user_id = query.from_user.id
    username = query.from_user.username
    upsert_user(user_id, username)
    keyboard = [
        [InlineKeyboardButton("Купить", callback_data='buy')],
        [InlineKeyboardButton("Баланс", callback_data='balance')],
        [InlineKeyboardButton("Профиль", callback_data='profile')]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await query.edit_message_text(
        'Привет! Я бот для продажи XGramm (XGR) токенов.\n'
        'Используйте кнопки ниже для взаимодействия.',
        reply_markup=reply_markup
    )

