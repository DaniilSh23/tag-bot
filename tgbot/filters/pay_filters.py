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


confirm_payment_filter = filters.create(func=func_confirm_payment)
