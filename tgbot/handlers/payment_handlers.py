"""
Хэндлеры для всего, что связано с платежами
"""

from pyrogram import Client, filters
from pyrogram.types import Message
from django.urls import reverse

from tag_bot.settings import MY_LOGGER, BOT_TOKEN, BASE_HOST
from tgbot.filters.pay_filters import confirm_payment_filter
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
            '✔️ Подтвердить платёж',
            f"{BASE_HOST}{reverse(viewname='webapp:check_payment')}?token={BOT_TOKEN}&bill_hash={cmnd_data[1]}"
            f"&tg_msg_id={update.id}",
         ),
    )
    await update.edit_text(
        text='💸 <b>Летит бабосик!</b>\n\n✅<b>Пожалуйста, побыстрее обработайте платёж, чтобы клиент не ждал</b>',
        reply_markup=await form_webapp_kbrd(buttons_data=buttons_data),
    )
