from telegram import Update, InlineKeyboardMarkup, InlineKeyboardButton
from telegram.ext import CallbackContext
from .command_handlers import start, profile, start_from_callback
from services.ton_services import check_transaction_status, send_toncoins, generate_memo
from handlers.profile_handlers import profile

async def button(update: Update, context: CallbackContext) -> None:
    query = update.callback_query
    await query.answer()

    if query.data == 'buy':
        balances = [giver['balance'] for giver in context.bot_data['GIVERS']]
        balance_info = '\n'.join([f'Гивер {i+1}: {balance} XGR' for i, balance in enumerate(balances)])
        keyboard = [[InlineKeyboardButton(f"Гивер {i+1}", callback_data=f'buy_giver_{i}') for i in range(len(context.bot_data['GIVERS']))]]
        keyboard.append([InlineKeyboardButton("Назад", callback_data='back_to_main')])
        reply_markup = InlineKeyboardMarkup(keyboard)
        context.user_data['previous_state'] = 'main_menu'
        await query.edit_message_text(text=f"Выберите гивера:\n{balance_info}", reply_markup=reply_markup)
    elif query.data == 'balance':
        balances = [giver['balance'] for giver in context.bot_data['GIVERS']]
        balance_info = '\n'.join([f'Гивер {i+1}: {balance} XGR' for i, balance in enumerate(balances)])
        keyboard = [[InlineKeyboardButton("Назад", callback_data='back_to_main')]]
        reply_markup = InlineKeyboardMarkup(keyboard)
        context.user_data['previous_state'] = 'main_menu'
        await query.edit_message_text(text=f'Баланс кошельков гиверов:\n{balance_info}', reply_markup=reply_markup)
    elif query.data.startswith('buy_giver_'):
        giver_index = int(query.data.split('_')[-1])
        context.user_data['selected_giver'] = giver_index
        context.user_data['awaiting_address'] = True
        keyboard = [[InlineKeyboardButton("Назад", callback_data='back_to_buy')]]
        reply_markup = InlineKeyboardMarkup(keyboard)
        context.user_data['previous_state'] = 'buy'
        await query.edit_message_text(
            text=f'Вы выбрали гивера {giver_index+1}. Пожалуйста, введите ваш адрес TON.\n\n'
                 'Убедитесь, что адрес указан без лишних знаков и пробелов, и принадлежит сети TON.',
            reply_markup=reply_markup
        )
    elif query.data == 'profile':
        await profile(update, context)
        context.user_data['previous_state'] = 'main_menu'
    elif query.data == 'back_to_main':
        await start_from_callback(update, context)
    elif query.data == 'back_to_buy':
        balances = [giver['balance'] for giver in context.bot_data['GIVERS']]
        balance_info = '\n'.join([f'Гивер {i+1}: {balance} XGR' for i, balance in enumerate(balances)])
        keyboard = [[InlineKeyboardButton(f"Гивер {i+1}", callback_data=f'buy_giver_{i}') for i in range(len(context.bot_data['GIVERS']))]]
        keyboard.append([InlineKeyboardButton("Назад", callback_data='back_to_main')])
        reply_markup = InlineKeyboardMarkup(keyboard)
        await query.edit_message_text(text=f"Выберите гивера:\n{balance_info}", reply_markup=reply_markup)
    elif query.data == 'confirm_purchase':
        user_address = context.user_data.get('user_address', None)
        token_amount = context.user_data.get('token_amount', None)
        giver_index = context.user_data.get('selected_giver', None)
        if user_address and token_amount and giver_index is not None:
            giver = context.bot_data['GIVERS'][giver_index]
            user_id = query.from_user.id

            memo = generate_memo()
            context.user_data['memo'] = memo

            payment_info = (
                f'Для завершения покупки, пожалуйста, отправьте необходимую сумму TON на следующий адрес:\n\n'
                f'Адрес: {giver["address"]}\n'
                f'Комментарий: {memo}\n\n'
                f'После отправки, подтвердите операцию, нажав кнопку ниже.'
            )
            confirm_keyboard = [
                [InlineKeyboardButton("Я отправил TON", callback_data='confirm_payment')],
                [InlineKeyboardButton("Отменить", callback_data='cancel_purchase')]
            ]
            confirm_reply_markup = InlineKeyboardMarkup(confirm_keyboard)
            context.user_data['previous_state'] = 'buy_giver'
            await query.edit_message_text(payment_info, reply_markup=confirm_reply_markup)

            context.user_data['awaiting_payment_confirmation'] = True
        else:
            await query.edit_message_text("Ошибка: Недостаточно данных для подтверждения покупки.")
    elif query.data == 'confirm_payment':
        await check_payment_status(update, context)
    elif query.data == 'check_payment':
        await check_payment_status(update, context)
    elif query.data == 'cancel_purchase':
        context.user_data['awaiting_amount'] = False
        context.user_data['awaiting_address'] = False
        context.user_data['awaiting_payment_confirmation'] = False
        await query.edit_message_text('Покупка отменена.')

async def check_payment_status(update: Update, context: CallbackContext) -> None:
    query = update.callback_query
    user_id = query.from_user.id
    giver_index = context.user_data.get('selected_giver')
    giver = context.bot_data['GIVERS'][giver_index]
    user_address = context.user_data.get('user_address')
    token_amount = context.user_data.get('token_amount')
    memo = context.user_data.get('memo')

    await context.bot.send_chat_action(chat_id=query.message.chat_id, action="typing")
    await asyncio.sleep(5)  # Задержка перед повторной проверкой

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
