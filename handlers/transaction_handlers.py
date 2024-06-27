from telegram import Update, InlineKeyboardMarkup, InlineKeyboardButton
from telegram.ext import CallbackContext
from services.ton_services import check_transaction_status, send_xgr
from handlers.language_handlers import get_user_language
from database import update_bought_tokens
import asyncio
import logging
from handlers.language_handlers import choose_language
from handlers.languages import LANGUAGES
from handlers.language_handlers import set_language

async def check_payment_status(update: Update, context: CallbackContext) -> None:
    query = update.callback_query
    user_id = query.from_user.id
    lang_code = context.user_data.get('language', 'en')
    giver_index = context.user_data.get('selected_giver')
    giver = context.bot_data['GIVERS'][giver_index]
    user_address = context.user_data.get('user_address')
    token_amount = context.user_data.get('token_amount')
    memo = context.user_data.get('memo')

    await context.bot.send_chat_action(chat_id=query.message.chat_id, action="typing")
    await asyncio.sleep(5)

    transaction = await check_transaction_status(giver['address'], memo)

    if transaction:
        ton_amount = transaction['in_msg']['value'] / 1e9  # Преобразование из нанотонов в тон
        xgr_amount = ton_amount / giver['price_per_token']
        result = await send_xgr(giver['address'], user_address, xgr_amount)
        if result.get('ok'):
            update_bought_tokens(user_id, token_amount)
            await query.edit_message_text(
                LANGUAGES[lang_code]['successful_transfer'].format(token_amount=xgr_amount, user_address=user_address)
            )
        else:
            await query.edit_message_text(LANGUAGES[lang_code]['token_send_error'])
    else:
        check_keyboard = [
            [InlineKeyboardButton(LANGUAGES[lang_code]['check_again'], callback_data='check_payment')],
            [InlineKeyboardButton(LANGUAGES[lang_code]['cancel'], callback_data='cancel_purchase')]
        ]
        check_reply_markup = InlineKeyboardMarkup(check_keyboard)
        await query.edit_message_text(
            text=LANGUAGES[lang_code]['funds_not_received'],
            reply_markup=check_reply_markup
        )

async def check_givers_balances(context: CallbackContext):
    for giver in GIVERS:
        main_address = giver['address']
        jetton_master_address = config.XGR_JETTON_MASTER_ADDRESS
        jetton_balance = await get_jetton_balance(main_address, jetton_master_address)
        
        if jetton_balance > giver['initial_balance']:
            amount_received = jetton_balance - giver['initial_balance']
            giver['initial_balance'] = jetton_balance
            await process_received_payment(giver, amount_received)

async def process_received_payment(giver, amount_received):
    user_address = giver.get('last_user_address')
    if user_address:
        xgr_amount = amount_received / giver['price_per_token']
        result = await send_xgr(giver['address'], user_address, xgr_amount)
        if result.get('ok'):
            logging.info(f"Successfully sent {xgr_amount} XGR to {user_address}")
        else:
            logging.error(f"Failed to send XGR to {user_address}")

def start_periodic_balance_check(application):
    application.job_queue.run_repeating(check_givers_balances, interval=60, first=10)