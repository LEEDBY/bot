from telegram import Update, InlineKeyboardMarkup, InlineKeyboardButton
from telegram.ext import CallbackContext
from services.ton_services import check_transaction_status, send_toncoins

async def check_payment_status(update: Update, context: CallbackContext) -> None:
    query = update.callback_query
    user_id = query.from_user.id
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
            await query.edit_message_text(f'Успешно отправлено {token_amount} XGR на адрес {user_address}')
        else:
            await query.edit_message_text('Ошибка при отправке токенов')
    else:
        check_keyboard = [
            [InlineKeyboardButton("Проверить снова", callback_data='check_payment')],
            [InlineKeyboardButton("Отменить", callback_data='cancel_purchase')]
        ]
        check_reply_markup = InlineKeyboardMarkup(check_keyboard)
        await query.edit_message_text(
            text='Средства не поступили. Пожалуйста, проверьте отправку и попробуйте снова.',
            reply_markup=check_reply_markup
        )
