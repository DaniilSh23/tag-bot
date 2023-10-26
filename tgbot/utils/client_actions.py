import os
import time

from pyrogram.types import InputMediaDocument, InputMediaPhoto, InputMediaVideo, InputMediaAudio, InputMediaAnimation

from tag_bot.settings import BASE_HOST, TAG_NOW_INTERVAL, MY_LOGGER, LAST_TAG_MESSAGES_IN_CHATS
from tgbot.entities.tag_entities import TagMsgEntity
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
        sent_msg = await client.send_video(
            chat_id=chat_id,
            video=file_path,
            caption=msg_text,
        )
    elif file_ext.upper() in ('.JPEG', '.JPG', '.PNG', '.BMP', '.SVG'):     # Отправка картинки
        sent_msg = await client.send_photo(
            chat_id=chat_id,
            photo=file_path,
            caption=msg_text,
        )
    elif file_ext.upper() in ('.GIF',):     # Отправки гифки
        sent_msg = await client.send_animation(
            chat_id=chat_id,
            animation=file_path,
            caption=msg_text,
        )
    elif file_ext.upper() in ('.MP3', '.WAV', '.MP4', '.WMA'):  # Отправка аудио
        sent_msg = await client.send_audio(
            chat_id=chat_id,
            audio=file_path,
            caption=msg_text,
        )
    else:   # Отправка файла, как документа
        sent_msg = await client.send_document(
            chat_id=chat_id,
            document=file_path,
            caption=msg_text,
        )
    return sent_msg


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


async def edit_tag_msg(tag_msg_entity: TagMsgEntity, client: Client, chat_id: str, username: str):
    """
    Функция для редактирования сообщения с тегом и добавления в него нового юзернейма.
    Актуально, когда интервал между тегами менее 1 минуты.
    """
    MY_LOGGER.debug(f'Вызвана функция для изменения сообщения с тегом при теге сразу')
    new_msg_text = f"@{username} {tag_msg_entity.msg_text}"
    match tag_msg_entity.media_msg:
        case False:     # Редактируем текст сообщения БЕЗ медиа
            await client.edit_message_text(
                chat_id=chat_id,
                message_id=tag_msg_entity.msg_id,
                text=new_msg_text,
            )
        case True:  # Редактируем подпись сообщения С медиа
            await client.edit_message_caption(
                chat_id=chat_id,
                message_id=tag_msg_entity.msg_id,
                caption=new_msg_text,
            )
    # Обновляем инфу в дата классе о сообщении с тегом
    tag_msg_entity.msg_text = new_msg_text
    tag_msg_entity.last_tag_timestamp = time.time()


async def send_tag_msg(group_chat: dict, client: Client, msg_text: str, chat_id: str):
    """
    Функция для отправки сообщений с тегом.
    """
    MY_LOGGER.debug(f'Вызвана функция для отправки сообщения с тегом при теге сразу')
    # Отправляем сообщение с одним документом
    if len(group_chat.get('group_files')) == 1:

        # Получаем расширение файла и проверяем его формат, чтобы отправить правильно медиа
        file_path = group_chat.get('group_files')[0].path
        sent_msg = await check_media_format_and_send_msg(
            file_path=file_path,
            msg_text=msg_text,
            chat_id=group_chat.get('group_tg_id'),
            client=client,
        )
        media_msg = True

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
        sent_msg = await client.send_media_group(
            chat_id=group_chat.get('group_tg_id'),
            media=media_lst,
        )
        sent_msg = sent_msg[-1]
        media_msg = True

    # Отправляем сообщение без медиа
    else:
        sent_msg = await client.send_message(
            chat_id=group_chat.get('group_tg_id'),
            text=msg_text,
        )
        media_msg=False

    # Создаём инстанс дата класса для сообщений с тегом
    tag_msg_obj = TagMsgEntity(
        chat_id=chat_id,
        msg_id=sent_msg.id,
        send_msg_timestamp=time.time(),
        msg_text=msg_text,
        media_msg=media_msg,
    )
    LAST_TAG_MESSAGES_IN_CHATS[chat_id] = tag_msg_obj
