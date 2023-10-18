from django.urls import reverse
from pyrogram import Client, filters
from pyrogram.raw.types import UpdateChannelParticipant
from pyrogram.types import Message

from tag_bot.settings import MY_LOGGER
from tgbot.db_work import get_group_detail
from tgbot.filters.group_chat_filters import tag_all_filter, filter_by_group_id, \
    func_filter_invite_user_in_group
from tgbot.utils.client_actions import send_tag_msg


@Client.on_raw_update(filters.group)
async def tag_now_by_invite_handler(client, update: UpdateChannelParticipant, raw_users, raw_channel):
    """
    Хэндлер для тега сразу пользователей, которые были приглашены в чат.
    """

    # Фильтруем апдейт и отсеиваем, если он не пройдет фильтр
    filter_rslt = await func_filter_invite_user_in_group(update=update)
    if not filter_rslt:
        return

    MY_LOGGER.info(f'Получен апдейт для тега сразу юзера, который был приглашен в чат.')
    bot_usr = await client.get_users(user_ids=update.user_id)

    # Достаём инфу о чате для тега
    group_chat = await get_group_detail(group_tg_id=f"-100{update.channel_id}")
    if not group_chat:
        MY_LOGGER.warning(f'Тег нового юзера в чате выполнен не будет. Чат с TG ID == f"-100{update.channel_id}"'
                          f' не найден в БД')
        return
    elif not bot_usr.username:
        MY_LOGGER.warning(f'Тег нового юзера в чате выполнен не будет. У юзера отсутствует username | '
                          f'его TG ID == {bot_usr.id}')
        return

    # Тегаем юзера в этом чате с рекламным текстом и файлами
    msg_text = f"@{bot_usr.username}\n\n{group_chat.get('msg_text')}"
    await send_tag_msg(
        client=client,
        group_chat=group_chat,
        msg_text=msg_text,
    )


@Client.on_message(filters.new_chat_members & filter_by_group_id)
async def tag_now_handler(client: Client, update: Message):
    """
    Хэндлер для апдейтов вступления новых юзеров в чаты из списка в БД, у которых установлен tag_now=True.
    """
    MY_LOGGER.info(f'Пришел апдейт в хэндлер для сервисных сообщений о вступлении нового юзера в чат.')

    # Достаём инфу о чате для тега
    group_chat = await get_group_detail(group_tg_id=str(update.chat.id))
    if not group_chat:
        MY_LOGGER.warning(f'Тег нового юзера в чате выполнен не будет. Чат с TG ID == {update.chat.id} не найден в БД')
        return
    elif not update.from_user.username:
        MY_LOGGER.warning(f'Тег нового юзера в чате выполнен не будет. У юзера отсутствует username | '
                          f'его TG ID == {update.from_user.id}')
        return

    # Тегаем юзера в этом чате с рекламным текстом и файлами
    msg_text = f"@{update.from_user.username}\n\n{group_chat.get('msg_text')}"
    await send_tag_msg(
        client=client,
        group_chat=group_chat,
        msg_text=msg_text,
    )


@Client.on_message(filters.me & filters.bot & tag_all_filter)
async def tag_all_handler(client: Client, update: Message):
    """
    Хэндлер для команды боту тегнуть всех.
    """
    MY_LOGGER.info(f'Сработал хэндлер для команды тенуть всех')

    await update.delete()
    _, group_id = update.text.split()
    group_chat = await get_group_detail(group_id=int(group_id))
    if not group_chat:
        MY_LOGGER.warning(f'Тег всех выполнен не будет.')
        return

    # Достаём юзеров и выполняем отправку
    members_lst = [member async for member in client.get_chat_members(group_chat.get('group_tg_id'))]
    msg_text = f"\n\n{group_chat.get('msg_text')}"

    for i_memb in members_lst:

        # Если у юзера нету username
        if not i_memb.user.username or i_memb.user.is_bot:
            continue

        # Обработка, на случай если длинна сообщения превысила 2000 символов
        if len(f'@{i_memb.user.username} {msg_text}') >= 2000:

            # Вызываем функцию по отправке сообщения с тегами и очищаем от тегов текст сообщения
            await send_tag_msg(
                client=client,
                group_chat=group_chat,
                msg_text=msg_text,
            )
            msg_text = f"\n\n\n{group_chat.get('msg_text')}"

        msg_text = f'@{i_memb.user.username} {msg_text}'
    else:
        # Вызываем функцию по отправке сообщения с тегами и очищаем от тегов текст сообщения
        await send_tag_msg(
            client=client,
            group_chat=group_chat,
            msg_text=msg_text,
        )


@Client.on_message(filters.group & filters.command(commands=['id']))
async def return_chat_id(_, update: Message):
    """
    Метод, который возвращает ID чата, если была выполнена команда /id в групповом чате.
    """
    MY_LOGGER.info(f'Получен апдейт на хэндлер возврата ID чата.')

    # Отправляем ID данного чата
    await update.reply_text(text=f'🆔 <b>ID данного чата:</b>\n\n'
                                 f'<code>{update.chat.id}</code>\n\n'
                                 f'➕ Он понадобиться, чтобы <b>подключить этот чат для тега пользователей</b>.\n\n'
                                 f'🗑 Вы можете <b>удалить это сообщение</b>, чтобы иные участники чата его не видели.')
