"""
Основные хэндлеры бота.
"""
from asgiref.sync import sync_to_async
from pyrogram import Client, filters
from django.urls import reverse

from tag_bot.settings import MY_LOGGER, BOT_TOKEN, BASE_HOST
from tgbot.keyboards.bot_keyboards import form_webapp_kbrd
from tgbot.tests import update_or_create_bot_user
from webapp.models import BotUser


@Client.on_message(filters.command(['start', 'menu']))
async def start_handler(_, update):
    """
    Хэндлер для старта бота. Отдаёт главное меню
    """
    MY_LOGGER.info(f'Стартовый хэндлер для юзера {update.from_user.id!r}')

    # Записываем или обновляем юзера в БД
    await update_or_create_bot_user(update)
    button_data = (
        ('💲 Мой баланс', f"{BASE_HOST}{reverse(viewname='webapp:balance')}?token={BOT_TOKEN}"),
    )
    await update.reply_text(
        text=f'👋 Привет!\n\nЭто бот теггер. Он тегает людей в Ваших групповых чатах.',
        reply_markup=await form_webapp_kbrd(button_data)
    )