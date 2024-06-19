from telegram.ext import Application, CommandHandler, CallbackQueryHandler, MessageHandler, filters
import config
from config import TOKEN, GIVERS
from handlers.start_handlers import start
from handlers.button_handlers import button
from handlers.message_handlers import handle_message
from handlers.profile_handlers import profile
from services.ton_services import update_giver_balances
import asyncio
from telegram import BotCommand
import nest_asyncio
from database import create_table

nest_asyncio.apply()

async def set_commands(app):
    await app.bot.set_my_commands([
        BotCommand("start", "Запустить бота"),
    ])

async def periodic_update(context):
    update_giver_balances(context.application.bot_data['GIVERS'])

async def run_bot():
    create_table()

    app = Application.builder().token(config.TOKEN).build()

    # Инициализируем данные о гиверах в bot_data
    app.bot_data['GIVERS'] = config.GIVERS

    # Инициализируем баланс гиверов
    update_giver_balances(app.bot_data['GIVERS'])

    job_queue = app.job_queue
    job_queue.run_repeating(periodic_update, interval=60, first=0)

    await set_commands(app)

    app.add_handler(CommandHandler("start", start))
    app.add_handler(CallbackQueryHandler(button))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))

    await app.run_polling()

if __name__ == '__main__':
    asyncio.run(run_bot())
