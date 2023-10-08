"""
Хэндлеры для всего, что связано с платежами
"""

from pyrogram import Client, filters
from pyrogram.types import Message
from django.urls import reverse

from tag_bot.settings import MY_LOGGER, BOT_TOKEN, BASE_HOST
from tgbot.filters.pay_filters import confirm_payment_filter, edit_msg_for_confirm_payment_filter
from tgbot.keyboards.bot_keyboards import form_webapp_kbrd


@Client.on_message(filters.me & filters.bot & confirm_payment_filter)
async def get_command_for_confirm_payment(_, update: Message):
    """
    Хэндлер для получения команды на подтверждение платежа и выполнения соответствующей логики.
    """
    MY_LOGGER.info(f'Сработал хэндлер get_command_for_confirm_payment')

    text_data = update.text if update.text else update.caption
    cmnd_data = text_data.split()
    buttons_data = (
        (
            '✔️ Обработать платёж',
            f"{BASE_HOST}{reverse(viewname='webapp:check_payment')}?token={BOT_TOKEN}&bill_hash={cmnd_data[1]}"
            f"&tg_msg_id={update.id}",
         ),
    )
    await update.edit_text(
        text='💸 <b>Летит-летит бабосик!</b>\n\n❕<b>Пожалуйста, побыстрее обработайте платёж, чтобы клиент не ждал</b>',
        reply_markup=await form_webapp_kbrd(buttons_data=buttons_data),
    )


@Client.on_message(filters.me & filters.bot & edit_msg_for_confirm_payment_filter)
async def edit_msg_for_confirm_payment(client: Client, update: Message):
    """
    Хэндлер, который удаляет у админа сообщение с кнопкой для подтверждения платежа.
    И отправляет ему другое информационное сообщение с совершенным им действием по платежу (подтв./откл.)
    """
    MY_LOGGER.info(f'Сработал хэндлер edit_msg_for_confirm_payment')

    # Собираем данные в кучу
    _, msg_id, bill_action, bill_pk = update.text.split()
    if bill_action == 'confirm_pay':
        action_text = 'подтвержден'
        emoj_for_text = '✅'
    else:
        action_text = 'отклонён'
        emoj_for_text = '❌'

    # Изменяем старое сообщение с WebApp кнопкой для проверки платежа и удаляем информационное
    await client.edit_message_text(
        chat_id=update.chat.id,
        message_id=int(msg_id),
        text=f'{emoj_for_text} <b>Платёж по счету № {bill_pk} {action_text}!</b>'
    )
    await update.delete()