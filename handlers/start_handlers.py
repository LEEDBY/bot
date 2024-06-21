from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes
from telegram.ext import CallbackContext
from database import upsert_user, get_user
from handlers.languages import LANGUAGES
from handlers.language_handlers import choose_language

async def start_from_callback(update: Update, context: CallbackContext) -> None:
    if 'language' not in context.user_data:
        from handlers.language_handlers import choose_language
        await choose_language(update, context)
        return

    user_id = update.effective_user.id
    username = update.effective_user.username
    lang_code = context.user_data.get('language', 'en')
    upsert_user(user_id, username)
    keyboard = [
        [InlineKeyboardButton(LANGUAGES[lang_code]['buy'], callback_data='buy')],
        [InlineKeyboardButton(LANGUAGES[lang_code]['balance'], callback_data='balance')],
        [InlineKeyboardButton(LANGUAGES[lang_code]['profile'], callback_data='profile')],
        [InlineKeyboardButton(LANGUAGES[lang_code]['language'], callback_data='choose_language')]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)

    if update.message:
        await update.message.reply_text(
            LANGUAGES[lang_code]['welcome'],
            reply_markup=reply_markup
        )
    elif update.callback_query:
        await update.callback_query.message.edit_text(
            LANGUAGES[lang_code]['welcome'],
            reply_markup=reply_markup
        )