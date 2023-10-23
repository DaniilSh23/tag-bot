import os

from pyrogram.types import InputMediaDocument, InputMediaPhoto, InputMediaVideo, InputMediaAudio, InputMediaAnimation

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


async def check_media_format_and_send_msg(file_path, chat_id, msg_text, client):
    """
    Функция для проверки формата медиа-файла и отправки сообщения с нужным вложением.
    """
    file_ext = os.path.splitext(file_path)[1]

    if file_ext.upper() in ('.MOV', '.AVI', '.MP4', '.MKV'):    # Отправка видео
        await client.send_video(
            chat_id=chat_id,
            video=file_path,
            caption=msg_text,
        )
    elif file_ext.upper() in ('.JPEG', '.JPG', '.PNG', '.BMP', '.SVG'):     # Отправка картинки
        await client.send_photo(
            chat_id=chat_id,
            photo=file_path,
            caption=msg_text,
        )
    elif file_ext.upper() in ('.GIF',):     # Отправки гифки
        await client.send_animation(
            chat_id=chat_id,
            animation=file_path,
            caption=msg_text,
        )
    elif file_ext.upper() in ('.MP3', '.WAV', '.MP4', '.WMA'):  # Отправка аудио
        await client.send_audio(
            chat_id=chat_id,
            audio=file_path,
            caption=msg_text,
        )
    else:   # Отправка файла, как документа
        await client.send_document(
            chat_id=chat_id,
            document=file_path,
            caption=msg_text,
        )


async def make_media_type(file_path):
    """
    Функция, которая проверяет по расширению тип медиа-файла и возвращает нужны InputMedia тип pyrogram
    """
    file_ext = os.path.splitext(file_path)[1]
    if file_ext.upper() in ('.MOV', '.AVI', '.MP4', '.MKV'):    # Видео
        return InputMediaVideo(media=file_path)
    elif file_ext.upper() in ('.GIF',):     # Гифка
        return InputMediaAnimation(media=file_path)
    elif file_ext.upper() in ('.JPEG', '.JPG', '.PNG', '.BMP', '.SVG'):     # Картинка
        return InputMediaPhoto(media=file_path)
    elif file_ext.upper() in ('.MP3', '.WAV', '.MP4', '.WMA'):  # Аудио
        return InputMediaAudio(media=file_path)
    else:   # Документ
        return InputMediaDocument(media=file_path)


async def send_tag_msg(group_chat: dict, client: Client, msg_text: str):
    """
    Функция для отправки сообщений с тегом.
    """
    # Отправляем сообщение с одним документом
    if len(group_chat.get('group_files')) == 1:

        # Получаем расширение файла и проверяем его формат, чтобы отправить правильно медиа
        file_path = group_chat.get('group_files')[0].path
        await check_media_format_and_send_msg(
            file_path=file_path,
            msg_text=msg_text,
            chat_id=group_chat.get('group_tg_id'),
            client=client,
        )

    # Отправляем сообщение с медиа-группой
    elif len(group_chat.get('group_files')) > 1:
        media_lst = []
        for indx, i_file in enumerate(group_chat.get('group_files')):
            input_media_obj = await make_media_type(file_path=i_file.path)  # Определяем тип медиа
            if indx == len(group_chat.get('group_files')) - 1:
                input_media_obj.caption = msg_text
                media_lst.append(input_media_obj)
            else:
                media_lst.append(input_media_obj)
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
