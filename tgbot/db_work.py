from asgiref.sync import sync_to_async
from django.core.exceptions import ObjectDoesNotExist

from webapp.models import BotUser, BotSettings


@sync_to_async
def update_or_create_bot_user(update):
    """
    Функция для обновления или создания записи модели BotUsers.
    """
    BotUser.objects.update_or_create(
        tlg_id=str(update.from_user.id),
        defaults={
            'tlg_username': update.from_user.username
        }
    )


@sync_to_async
def get_bot_settings(key: str):
    """
    Функция для получения записи модели BotSettings.
    """
    values = [i_obj.value for i_obj in BotSettings.objects.filter(key=key)]
    return values
