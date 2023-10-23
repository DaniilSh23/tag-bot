from pyrogram import filters
from pyrogram.raw.types import UpdateChannelParticipant, UpdateChatParticipant
from pyrogram.types import Message

from tgbot.db_work import get_group_ids_with_tag_now


async def func_get_cmnd_for_check_perm_filter(_, __, update: Message):
    """
    Фильтр для получения команды на проверку ботом своих прав в групповом чате
    """
    if update.text:
        return update.text.startswith('$$$check_bot_permissions')


async def func_tag_all(_, __, update: Message):
    """
    Фильтр для команды боту тегнуть всех в конкретном чате
    """
    if update.text:
        return update.text.startswith('$$$tag_all')


async def func_filter_by_group_id(_, __, update: Message):
    """
    Фильтр для апдейтов по конкретным ID групповых чатов.
    """
    groups_ids = await get_group_ids_with_tag_now()
    return str(update.chat.id) in groups_ids


async def func_filter_invite_user_in_group(update: UpdateChannelParticipant | UpdateChatParticipant):
    """
    Функция для фильтрации сырых апдейтов из групповых чатов.
    Работает для хэндлера, который отслеживает события инвайта новых юзеров.
    """
    # Проверяем, что пришёл подходящий апдейт
    if isinstance(update, UpdateChannelParticipant) or isinstance(update, UpdateChatParticipant):

        # Проверяем, что апдейт пришёл из подключенной группы
        groups_ids = await get_group_ids_with_tag_now()
        clear_group_ids = list()

        for i_group_id in groups_ids:

            # Форматируем ID, убираем пайрограмовские -100 и просто минус для обычных групп
            i_group_id = i_group_id.replace('-100', '') if i_group_id.startswith('-100') else i_group_id.replace('-', '')
            clear_group_ids.append(i_group_id)

        # Проверяем, что в списке групп есть ID апдейта
        chat_id = update.channel_id if isinstance(update, UpdateChannelParticipant) else update.chat_id
        if str(chat_id) not in clear_group_ids:
            return False
        return True

    # Пришёл неподходящий апдейт
    return False

get_cmnd_for_check_perm_filter = filters.create(func=func_get_cmnd_for_check_perm_filter)
tag_all_filter = filters.create(func=func_tag_all)
filter_by_group_id = filters.create(func=func_filter_by_group_id)