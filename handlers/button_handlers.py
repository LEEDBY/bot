from telegram import Update, InlineKeyboardMarkup, InlineKeyboardButton
from telegram.ext import CallbackContext
from .command_handlers import profile, start
from services.ton_services import check_transaction_status, send_toncoins, generate_memo
from handlers.profile_handlers import profile
from .start_handlers import start_from_callback
import asyncio
from handlers.language_handlers import choose_language
from handlers.languages import LANGUAGES
from handlers.language_handlers import set_language
import config
from services.ton_services import get_balance, update_giver_balances

async def button(update: Update, context: CallbackContext) -> None:
    query = update.callback_query
    lang_code = context.user_data.get('language', 'en')
    await query.answer()
    if query.data == 'buy':
        await update_giver_balances(config.GIVERS)
        balances = [giver['balance'] for giver in config.GIVERS]
        balance_info = '\n'.join([LANGUAGES[lang_code]['giver_balance'].format(i=i+1, balance=balance, total=giver['initial_balance']) for i, (balance, giver) in enumerate(zip(balances, config.GIVERS))])
        keyboard = [[InlineKeyboardButton(f"Giver {i+1}", callback_data=f'buy_giver_{i}') for i in range(len(config.GIVERS))]]
        keyboard.append([InlineKeyboardButton(LANGUAGES[lang_code]['back'], callback_data='back_to_main')])
        reply_markup = InlineKeyboardMarkup(keyboard)
        context.user_data['previous_state'] = 'main_menu'
        await query.edit_message_text(text=LANGUAGES[lang_code]['choose_giver'] + balance_info, reply_markup=reply_markup)
    elif query.data == 'choose_language':
        await choose_language(update, context)
    elif query.data.startswith('set_lang_'):
        await set_language(update, context)
    elif query.data == 'balance':
        await update_giver_balances(config.GIVERS)
        balances = [giver['balance'] for giver in config.GIVERS]
        balance_info = '\n'.join([LANGUAGES[lang_code]['giver_balance'].format(i=i+1, balance=balance, total=giver['initial_balance']) for i, (balance, giver) in enumerate(zip(balances, config.GIVERS))])
        keyboard = [[InlineKeyboardButton(LANGUAGES[lang_code]['back'], callback_data='back_to_main')]]
        reply_markup = InlineKeyboardMarkup(keyboard)
        context.user_data['previous_state'] = 'main_menu'
        await query.edit_message_text(text=LANGUAGES[lang_code]['balance_info'].format(balance_info=balance_info), reply_markup=reply_markup)
    elif query.data.startswith('buy_giver_'):
        giver_index = int(query.data.split('_')[-1])
        context.user_data['selected_giver'] = giver_index
        context.user_data['awaiting_address'] = True
        keyboard = [[InlineKeyboardButton(LANGUAGES[lang_code]['back'], callback_data='back_to_buy')]]
        reply_markup = InlineKeyboardMarkup(keyboard)
        context.user_data['previous_state'] = 'buy'
        await query.edit_message_text(
            text=LANGUAGES[lang_code]['enter_address'].format(giver_index=giver_index+1),
            reply_markup=reply_markup
        )
    elif query.data == 'back_to_main':
        await start(update, context)
    elif query.data == 'back_to_buy':
        await update_giver_balances(config.GIVERS)
        balances = [giver['balance'] for giver in config.GIVERS]
        balance_info = '\n'.join(
            [LANGUAGES[lang_code]['giver_balance'].format(i=i+1, balance=balance, total=giver['initial_balance']) for i, (balance, giver) in enumerate(zip(balances, config.GIVERS))]
        )
        keyboard = [[InlineKeyboardButton(f"Giver {i+1}", callback_data=f'buy_giver_{i}') for i in range(len(config.GIVERS))]]
        keyboard.append([InlineKeyboardButton(LANGUAGES[lang_code]['back'], callback_data='back_to_main')])
        reply_markup = InlineKeyboardMarkup(keyboard)
        context.user_data['previous_state'] = 'main_menu'
        await query.edit_message_text(text=LANGUAGES[lang_code]['choose_giver'] + '\n' + balance_info, reply_markup=reply_markup)
    elif query.data == 'profile':
        await profile(update, context)
        context.user_data['previous_state'] = 'main_menu'
    elif query.data == 'confirm_purchase':
        user_address = context.user_data.get('user_address', None)
        token_amount = context.user_data.get('token_amount', None)
        giver_index = context.user_data.get('selected_giver', None)
        if user_address and token_amount and giver_index is not None:
            giver = config.GIVERS[giver_index]
            user_id = query.from_user.id
            memo = generate_memo()
            context.user_data['memo'] = memo
            payment_info = LANGUAGES[lang_code]['confirm_purchase'].format(address=giver["address"], memo=memo)
            confirm_keyboard = [
                [InlineKeyboardButton(LANGUAGES[lang_code]['send_payment'], callback_data='confirm_payment')],
                [InlineKeyboardButton(LANGUAGES[lang_code]['cancel'], callback_data='cancel_purchase')]
            ]
            confirm_reply_markup = InlineKeyboardMarkup(confirm_keyboard)
            await query.edit_message_text(text=payment_info, reply_markup=confirm_reply_markup)
        else:
            await query.edit_message_text(LANGUAGES[lang_code]['error_occurred'])
    elif query.data == 'confirm_payment':
        giver_index = context.user_data.get('selected_giver', None)
        user_id = query.from_user.id
        memo = context.user_data.get('memo', None)
        giver = config.GIVERS[giver_index]
        if giver_index is not None and user_id and memo:
            status = await check_transaction_status(giver['address'], memo)
            if status:
                await query.edit_message_text(LANGUAGES[lang_code]['payment_successful'])
                await start(query.message, context)
            else:
                await query.edit_message_text(LANGUAGES[lang_code]['payment_failed'])
                await start(query.message, context)
        else:
            await query.edit_message_text(LANGUAGES[lang_code]['error_occurred'])
    elif query.data == 'cancel_purchase':
        context.user_data['awaiting_amount'] = False
        context.user_data['awaiting_address'] = False
        context.user_data['awaiting_payment_confirmation'] = False
        await query.edit_message_text(LANGUAGES[lang_code]['purchase_cancel'])
        await start(query.message, context)

async def check_payment_status(update: Update, context: CallbackContext) -> None:
    query = update.callback_query
    lang_code = context.user_data.get('language', 'en')
    user_id = query.from_user.id
    giver_index = context.user_data.get('selected_giver')
    giver = context.bot_data['GIVERS'][giver_index]
    user_address = context.user_data.get('user_address')
    token_amount = context.user_data.get('token_amount')
    memo = context.user_data.get('memo')

    await context.bot.send_chat_action(chat_id=query.message.chat_id, action="typing")
    await asyncio.sleep(10)  # Задержка перед повторной проверкой

    transaction = check_transaction_status(giver['address'], memo)

    if transaction:
        result = send_toncoins(giver['address'], giver['secret'], user_address, token_amount, memo)
        if result.get('ok'):
            update_bought_tokens(user_id, token_amount)
            await query.edit_message_text(LANGUAGES[lang_code]['payment_received'].format(amount=token_amount, address=user_address))
        else:
            await query.edit_message_text(LANGUAGES[lang_code]['payment_error'])
    else:
        check_keyboard = [
            [InlineKeyboardButton(LANGUAGES[lang_code]['check_again'], callback_data='check_payment')],
            [InlineKeyboardButton(LANGUAGES[lang_code]['cancel'], callback_data='cancel_purchase')]
        ]
        check_reply_markup = InlineKeyboardMarkup(check_keyboard)
        await query.edit_message_text(
            text=LANGUAGES[lang_code]['check_payment'],
            reply_markup=check_reply_markup
        )
