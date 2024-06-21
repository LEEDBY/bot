from telegram import Update, InlineKeyboardMarkup, InlineKeyboardButton
from telegram.ext import CallbackContext
from services.ton_services import check_transaction_status, send_toncoins
from handlers.language_handlers import get_user_language
from database import update_bought_tokens
import asyncio
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

    transaction = check_transaction_status(giver['address'], memo)

    if transaction:
        result = send_toncoins(giver['address'], giver['secret'], user_address, token_amount, memo)
        if result.get('ok'):
            update_bought_tokens(user_id, token_amount)
            await query.edit_message_text(
                LANGUAGES[lang_code]['successful_transfer'].format(token_amount=token_amount, user_address=user_address)
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