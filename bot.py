from telegram.ext import Application, CommandHandler, CallbackQueryHandler, MessageHandler, filters
import config
from config import TOKEN, GIVERS
from handlers.command_handlers import start
from handlers.button_handlers import button
from handlers.message_handlers import handle_message
from services.ton_services import update_giver_balances, update_all_giver_balances, periodic_update_balances
import asyncio
from telegram import BotCommand
import nest_asyncio
from database import create_table
from telegram.ext import CallbackContext
from handlers.language_handlers import choose_language, set_language

nest_asyncio.apply()

async def set_commands(app):
    await app.bot.set_my_commands([
        BotCommand("start", "Запустить бота"),
    ])

async def periodic_update(context: CallbackContext):
    try:
        await update_giver_balances(context.application.bot_data['GIVERS'])
    except Exception as e:
        print(f"Error during periodic update: {e}")

async def run_bot():
    create_table()

    app = Application.builder().token(config.TOKEN).build()
    asyncio.create_task(periodic_update_balances())

    # Инициализируем данные о гиверах в bot_data
    await update_all_giver_balances()
    app.bot_data['GIVERS'] = config.GIVERS

    # Инициализируем баланс гиверов
    await update_giver_balances(app.bot_data['GIVERS'], 'new_address')  # Добавлен аргумент address_key
    app.bot_data['GIVERS'] = GIVERS

    job_queue = app.job_queue
    job_queue.run_repeating(periodic_update, interval=60, first=0)

    await set_commands(app)

    app.add_handler(CommandHandler("start", start))
    app.add_handler(CallbackQueryHandler(button))
    app.add_handler(CallbackQueryHandler(choose_language, pattern='choose_language'))
    app.add_handler(CallbackQueryHandler(set_language, pattern='set_lang_.*'))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))

    await app.run_polling()

if __name__ == '__main__':
    asyncio.run(run_bot())
