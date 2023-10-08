from pyrogram.types import Message
from pyrogram import filters

from tgbot.db_work import get_bot_settings


async def func_confirm_payment(_, __, update: Message):
    """
    Функция фильтрации апдейтов для хэндлера получения команды на подтверждение платежа
    """
    values = await get_bot_settings(key='who_approve_payments')
    text_data = update.text if update.text else update.caption

    # Если в апдейте нет текста (ни в параметре text, ни в параметре caption)
    if not text_data:
        return
    return str(update.chat.id) in values and '$$$confirm_payment' in text_data


async def func_edit_msg_for_confirm_payment(_, __, update: Message):
    """
    Фильтр для сообщений от бота по изменению сообщения, связанного с подтверждением платежа.
    Нужен хэндлеру, который убирает сообщение с кнопкой для подтверждения платежа и отправляет
    вместо него инфо сообщение об уже совершенных админом действиях.
    """
    values = await get_bot_settings(key='who_approve_payments')

    # Если в апдейте нет текста (ни в параметре text, ни в параметре caption)
    if not update.text:
        return
    return str(update.chat.id) in values and '$$$del_msg' in update.text


confirm_payment_filter = filters.create(func=func_confirm_payment)
edit_msg_for_confirm_payment_filter = filters.create(func=func_edit_msg_for_confirm_payment)
