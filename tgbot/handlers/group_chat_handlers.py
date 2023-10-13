from pyrogram import Client, filters
from pyrogram.types import Message

from tag_bot.settings import MY_LOGGER
from tgbot.db_work import get_group_detail
from tgbot.filters.group_chat_filters import get_cmnd_for_check_perm_filter, tag_all_filter, filter_by_group_id
from tgbot.utils.client_actions import send_tag_msg


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


@Client.on_message(filters.command(['test']) | filters.me & filters.bot & get_cmnd_for_check_perm_filter)
async def get_command_for_check_perm(client: Client, update: Message):
    """
    Хэндлер для проверки прав бота в групповом чате.
    """
    # Get members
    chat_id = '-1001854849400'
    # async for member in client.get_chat_members(chat_id):
    #     print(member)

    # Получаем членов
    members_lst = [member async for member in client.get_chat_members(chat_id)]
    print(members_lst[0].user.username)

    msg_str = ''
    for i_member in members_lst:
        if i_member.user.username:
            msg_str = f"{msg_str} @{i_member.user.username}"
    await client.send_message(
        chat_id=chat_id,
        text=f"{msg_str} хуй.\n\n\nСпасибо за внимание."
    )

    # TODO: это не дописано. Чет хуета была. Почему-то бот не мог получить инфу о чате, даже в котором состоит как
    #  админ, получал ошибку Telegram says: [400 BOT_METHOD_INVALID] ... ХЗ, что делать, опускаю этот шаг пока что
    MY_LOGGER.info(f'Апдейт в хэндлере бота get_command_for_check_perm')

    # # _, group_lnk = update.text.split()
    # group_lnk = 'https://t.me/+1ZKtuEk_ivk2NmZi'
    # # group_hash = group_lnk.split('/')[-1]
    # print(group_lnk)
    # group_chat_obj = await client.get_chat(group_lnk)
    # print(group_chat_obj)


@Client.on_message(filters.private)
async def return_chat_id(_, update: Message):
    """
    Метод, который возвращает ID чата, если в бота было переслано сообщение из него.
    """
    MY_LOGGER.info(f'Получен апдейт на хэндлер возврата ID чата из которого переслано сообщение')

    if update.forward_from_chat:
        await update.reply_text(text=f'🆔 ID чата, из которого переслано это сообщение:\n\n'
                                     f'<code>{update.forward_from_chat.id}</code>\n\n'
                                     f'➕ Вы можете использовать его <b>для подключения собственной группы.</b>')
    else:
        await update.reply_text(text='🆔 Я могу предоставить ID чата, из которого Вы мне перешлете сообщение.\n\n'
                                     '✖️ Это сообщение не было переслано из другого чата.')