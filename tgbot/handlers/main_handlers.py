"""
Основные хэндлеры бота.
"""
from pyrogram import Client, filters
from django.urls import reverse

from tag_bot.settings import MY_LOGGER, BOT_TOKEN, BASE_HOST, DJANGO_SUPERUSER_USERNAME, DJANGO_SUPERUSER_PASSWORD
from tgbot.keyboards.bot_keyboards import form_webapp_kbrd
from tgbot.db_work import update_or_create_bot_user, get_or_create_profile, get_bot_settings


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
        ('🗃 Мои группы', f"{BASE_HOST}{reverse(viewname='webapp:groups')}"
                         f"?token={BOT_TOKEN}&tlg_id={update.from_user.id}"),
        ('🛟 Поддержка & ❔ FAQ', f"{BASE_HOST}{reverse(viewname='webapp:support')}"),
    )
    await update.reply_text(
        text=f'👋 Привет!\n\nЭто бот теггер. Он тегает людей в Ваших групповых чатах.\n\n'
             f'🆔 Чтобы <b>получить ID чата</b>, добавьте в него бота и в самом чате напишите команду\n\n'
             f'<code>/id</code>\n\nБот отправит Вам ID.\n\n'
             f'↪️ Затем возвращайтесь сюда, жмите <b>"🗃 Мои группы"</b> и добавляйте новый чат для тега.',
        reply_markup=await form_webapp_kbrd(button_data)
    )

    # Получаем ID админа бота, и если стартовал он, то отдаем данные для входа в админку
    admin_id = await get_bot_settings(key='who_approve_payments')
    if int(admin_id[0]) == int(update.from_user.id):
        button_data = (
            ('🎛 Админ-панель', f"{BASE_HOST}/admin"),
        )
        await update.reply_text(
            text=f'<b>Данные для админки:</b>\n\nLOGIN:\t<code>{DJANGO_SUPERUSER_USERNAME}</code>\n'
                 f'PASSWD\t<code>{DJANGO_SUPERUSER_PASSWORD}</code>',
            reply_markup=await form_webapp_kbrd(button_data)
        )

