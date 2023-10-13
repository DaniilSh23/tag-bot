from pyrogram import filters
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


get_cmnd_for_check_perm_filter = filters.create(func=func_get_cmnd_for_check_perm_filter)
tag_all_filter = filters.create(func=func_tag_all)
filter_by_group_id = filters.create(func=func_filter_by_group_id)