from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import CallbackContext
from handlers.languages import LANGUAGES

async def choose_language(update: Update, context: CallbackContext) -> None:
    keyboard = [
        [InlineKeyboardButton("English", callback_data='set_lang_en')],
        [InlineKeyboardButton("Русский", callback_data='set_lang_ru')],
        [InlineKeyboardButton("Українська", callback_data='set_lang_uk')]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)

    if update.callback_query:
        await update.callback_query.edit_message_text("Choose a language:", reply_markup=reply_markup)
    else:
        await update.message.reply_text("Choose a language:", reply_markup=reply_markup)

async def set_language(update: Update, context: CallbackContext) -> None:
    query = update.callback_query
    data = query.data

    if data == 'set_lang_en':
        context.user_data['language'] = 'en'
    elif data == 'set_lang_ru':
        context.user_data['language'] = 'ru'
    elif data == 'set_lang_uk':
        context.user_data['language'] = 'uk'

    from handlers.start_handlers import start_from_callback
    await start_from_callback(update, context)
