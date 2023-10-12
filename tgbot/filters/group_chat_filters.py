from pyrogram import filters
from pyrogram.types import Message


async def func_get_cmnd_for_check_perm_filter(_, __, update: Message):
    """
    Фильтр для получения команды на проверку ботом своих прав в групповом чате
    """
    if update.text:
        return update.text.startswith('$$$check_bot_permissions')


get_cmnd_for_check_perm_filter = filters.create(func=func_get_cmnd_for_check_perm_filter)
