from tag_bot.settings import TG_CLIENT, BASE_HOST
from tgbot.keyboards.bot_keyboards import form_webapp_kbrd
from django.urls import reverse


async def send_msg_for_confirm_pay(msg_text, who_approve_pay):
    """
    Отправка сообщения пользователю для подтверждения платежа
    """
    buttons_data = (
        ('🔎 Проверить платёж', f"{BASE_HOST}{reverse(viewname='webapp:check_payment')}")
    )
    await TG_CLIENT.send_message(
        text=msg_text,
        chat_id=who_approve_pay,
        reply_markup=await form_webapp_kbrd(buttons_data=buttons_data)
    )
