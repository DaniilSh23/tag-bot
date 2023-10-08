"""
Основные хэндлеры бота.
"""
from pyrogram import Client, filters
from django.urls import reverse

from tag_bot.settings import MY_LOGGER, BOT_TOKEN, BASE_HOST
from tgbot.keyboards.bot_keyboards import form_webapp_kbrd
from tgbot.db_work import update_or_create_bot_user, get_or_create_profile


@Client.on_message(filters.command(['start', 'menu']))
async def start_handler(_, update):
    """
    Хэндлер для старта бота. Отдаёт главное меню
    """
    MY_LOGGER.info(f'Стартовый хэндлер для юзера {update.from_user.id!r}')

    # Записываем или обновляем юзера в БД, создаем запись в Profiles для него, если ещё не создана
    user_obj = await update_or_create_bot_user(update)
    await get_or_create_profile(bot_user=user_obj)

    button_data = (
        ('💲 Мой баланс', f"{BASE_HOST}{reverse(viewname='webapp:balance')}"
                         f"?token={BOT_TOKEN}&tlg_id={update.from_user.id}"),
    )
    await update.reply_text(
        text=f'👋 Привет!\n\nЭто бот теггер. Он тегает людей в Ваших групповых чатах.',
        reply_markup=await form_webapp_kbrd(button_data)
    )


# @Client.on_message()
async def test_handler(client, update):
    """
    Тестовый хэндлер
    """
    print(client)
    print(update)
