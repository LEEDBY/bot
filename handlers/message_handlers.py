from telegram import Update, InlineKeyboardMarkup, InlineKeyboardButton
from telegram.ext import CallbackContext
from helpers import validate_address_format
from services.ton_services import generate_memo
from handlers.languages import LANGUAGES

async def handle_message(update: Update, context: CallbackContext) -> None:
    user_data = context.user_data
    lang_code = context.user_data.get('language', 'en')

    if user_data.get('awaiting_address'):
        user_address = update.message.text
        if validate_address_format(user_address):
            user_data['user_address'] = user_address
            user_data['awaiting_address'] = False
            user_data['awaiting_amount'] = True
            await update.message.reply_text(LANGUAGES[lang_code]['address_confirmed'])
        else:
            await update.message.reply_text(LANGUAGES[lang_code]['invalid_address'])
    elif user_data.get('awaiting_amount'):
        try:
            token_amount = int(update.message.text)
            user_data['token_amount'] = token_amount
            user_data['awaiting_amount'] = False

            giver_index = user_data['selected_giver']
            giver = context.bot_data['GIVERS'][giver_index]
            user_id = update.effective_user.id

            memo = generate_memo()
            user_data['memo'] = memo

            payment_info = (
                f"{LANGUAGES[lang_code]['complete_purchase']}\n\n"
                f"{LANGUAGES[lang_code]['address']}: {giver['address']}\n"
                f"{LANGUAGES[lang_code]['comment']}: {memo}\n\n"
                f"{LANGUAGES[lang_code]['confirm_operation']}"
            )
            confirm_keyboard = [
                [InlineKeyboardButton(LANGUAGES[lang_code]['confirm_sent'], callback_data='confirm_payment')],
                [InlineKeyboardButton(LANGUAGES[lang_code]['cancel'], callback_data='cancel_purchase')]
            ]
            confirm_reply_markup = InlineKeyboardMarkup(confirm_keyboard)

            await update.message.reply_text(payment_info, reply_markup=confirm_reply_markup)

            user_data['awaiting_payment_confirmation'] = True
        except ValueError:
            await update.message.reply_text(LANGUAGES[lang_code]['enter_valid_amount'])
    else:
        await update.message.reply_text(LANGUAGES[lang_code]['use_start'])
