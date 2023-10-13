from pyrogram.types import InputMediaDocument

from tag_bot.settings import BASE_HOST
from tgbot.keyboards.bot_keyboards import form_webapp_kbrd
from django.urls import reverse
from pyrogram import Client


async def send_msg_for_confirm_pay(msg_text, who_approve_pay):
    """
    Отправка сообщения пользователю для подтверждения платежа
    """
    buttons_data = (
        ('🔎 Проверить платёж', f"{BASE_HOST}{reverse(viewname='webapp:check_payment')}")
    )
    await Client.send_message(
        text=msg_text,
        chat_id=who_approve_pay,
        reply_markup=await form_webapp_kbrd(buttons_data=buttons_data)
    )


async def send_tag_msg(group_chat: dict, client: Client, msg_text: str):
    """
    Функция для отправки сообщений с тегом.
    """
    # Отправляем сообщение с одним документом
    if len(group_chat.get('group_files')) == 1:
        await client.send_document(
            chat_id=group_chat.get('group_tg_id'),
            document=group_chat.get('group_files')[0].path,
            caption=msg_text,
        )

    # Отправляем сообщение с медиа-группой
    elif len(group_chat.get('group_files')) > 1:
        media_lst = []
        for indx, i_file in enumerate(group_chat.get('group_files')):
            if indx == len(group_chat.get('group_files')) - 1:
                media_lst.append(InputMediaDocument(
                    media=i_file.path,
                    caption=msg_text,
                ))
            else:
                media_lst.append(InputMediaDocument(
                    media=i_file.path,
                ))
        await client.send_media_group(
            chat_id=group_chat.get('group_tg_id'),
            media=media_lst,
        )

    # Отправляем сообщение без медиа
    else:
        await client.send_message(
            chat_id=group_chat.get('group_tg_id'),
            text=msg_text,
        )
