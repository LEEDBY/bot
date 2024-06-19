from telegram import Update
from telegram.ext import CallbackContext
from database import get_user

async def profile(update: Update, context: CallbackContext) -> None:
    user_id = update.effective_user.id
    user_data = get_user(user_id)
    if user_data:
        profile_info = (
            f"Ваш профиль:\n\n"
            f"ID: {user_data[0]}\n"
            f"Купленные токены: {user_data[2]} XGR\n"
        )
        await update.message.reply_text(profile_info)
    else:
        await update.message.reply_text("Ошибка: пользователь не найден в базе данных.")
