from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import CallbackContext
from database import get_user
from handlers.language_handlers import choose_language
from handlers.languages import LANGUAGES
from handlers.language_handlers import set_language

async def profile(update: Update, context: CallbackContext) -> None:
    query = update.callback_query
    user_id = query.from_user.id
    lang_code = context.user_data.get('language', 'en')
    user_data = get_user(user_id)
    if user_data is None:
        await query.message.reply_text(LANGUAGES[lang_code]['user_not_found'])
        return

    profile_info = (
        f"ID: {user_data[0]}\n"
        f"{LANGUAGES[lang_code]['tokens_purchased']}: {user_data[2]}"
    )

    keyboard = [[InlineKeyboardButton(LANGUAGES[lang_code]['back'], callback_data='back_to_main')]]
    reply_markup = InlineKeyboardMarkup(keyboard)

    await query.message.edit_text(profile_info, reply_markup=reply_markup)
