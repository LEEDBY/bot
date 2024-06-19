from telegram import Update, InlineKeyboardMarkup, InlineKeyboardButton
from telegram.ext import CallbackContext
from helpers import validate_address_format
from services.ton_services import generate_memo

async def handle_message(update: Update, context: CallbackContext) -> None:
    if context.user_data.get('awaiting_address'):
        user_address = update.message.text
        if validate_address_format(user_address):
            context.user_data['user_address'] = user_address
            context.user_data['awaiting_address'] = False
            context.user_data['awaiting_amount'] = True
            await update.message.reply_text('Адрес подтвержден. Пожалуйста, введите количество токенов для покупки.')
        else:
            await update.message.reply_text('Введен некорректный адрес. Пожалуйста, введите правильный адрес TON.')
    elif context.user_data.get('awaiting_amount'):
        try:
            token_amount = int(update.message.text)
            context.user_data['token_amount'] = token_amount
            context.user_data['awaiting_amount'] = False

            giver_index = context.user_data['selected_giver']
            giver = context.bot_data['GIVERS'][giver_index]
            user_id = update.effective_user.id

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

            await update.message.reply_text(payment_info, reply_markup=confirm_reply_markup)

            context.user_data['awaiting_payment_confirmation'] = True
        except ValueError:
            await update.message.reply_text('Пожалуйста, введите корректное количество токенов.')
    else:
        await update.message.reply_text('Используйте /start для начала.')
