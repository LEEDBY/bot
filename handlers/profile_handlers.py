from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import CallbackContext
from database import get_user

async def profile(update: Update, context: CallbackContext) -> None:
    query = update.callback_query
    user_id = query.from_user.id
    user_data = get_user(user_id)
    if user_data is None:
        await query.message.reply_text("Ошибка: пользователь не найден в базе данных.")
        return

    profile_info = (
        f"ID: {user_data[0]}\n"
        f"Количество купленных токенов: {user_data[2]}"
    )

    keyboard = [[InlineKeyboardButton("Назад", callback_data='back_to_main')]]
    reply_markup = InlineKeyboardMarkup(keyboard)

    await query.message.edit_text(profile_info, reply_markup=reply_markup)
