from pyrogram import filters
from pyrogram.types import Message, CallbackQuery


async def what_was_interesting_func(_, __, update: Message):
    """
    Фильтр для апдейтов (сообщений) от лица бота. В которых содержиться строка $$$what_was_interesting
    """
    if update.text:
        return update.text.endswith('$$$what_was_interesting')


async def send_post_selection_func(_, __, update):
    """
    Фильтр для апдейтов от лица бота, в которых содержится строка $$$news_collection
    """
    if update.text:
        return '$$$news_collection' in update.text

what_was_interesting_filter = filters.create(what_was_interesting_func)
send_post_selection_filter = filters.create(send_post_selection_func)
