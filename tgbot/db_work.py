from asgiref.sync import sync_to_async
from django.core.exceptions import ObjectDoesNotExist

from webapp.models import BotUser, BotSettings, Profiles


@sync_to_async
def update_or_create_bot_user(update):
    """
    Функция для обновления или создания записи модели BotUsers.
    """
    obj, created = BotUser.objects.update_or_create(
        tlg_id=str(update.from_user.id),
        defaults={
            'tlg_username': update.from_user.username
        }
    )
    return obj


@sync_to_async
def get_or_create_profile(bot_user: BotUser):
    """
    Функция для получения или создания объекта Profile
    """
    Profiles.objects.get_or_create(
        bot_user=bot_user,
        defaults={
            'balance': 0,
        }
    )


@sync_to_async
def get_bot_settings(key: str):
    """
    Функция для получения записи модели BotSettings.
    """
    values = [i_obj.value for i_obj in BotSettings.objects.filter(key=key)]
    return values
