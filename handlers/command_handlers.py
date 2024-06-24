from telegram import Update, InlineKeyboardMarkup, InlineKeyboardButton
from telegram.ext import CallbackContext
from database import upsert_user, get_user
from handlers.profile_handlers import profile
from handlers.language_handlers import choose_language
from handlers.start_handlers import start_from_callback


async def start(update: Update, context: CallbackContext) -> None:
    await start_from_callback(update, context)
