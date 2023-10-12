from pyrogram import Client, filters
from pyrogram.types import Message

from tag_bot.settings import MY_LOGGER
from tgbot.filters.group_chat_filters import get_cmnd_for_check_perm_filter


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


@Client.on_message()
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