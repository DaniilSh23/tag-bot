from asgiref.sync import sync_to_async
from django.core.exceptions import ObjectDoesNotExist

from tag_bot.settings import MY_LOGGER
from webapp.models import BotUser, BotSettings, Profiles, GroupChats, GroupChatFiles


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


@sync_to_async
def get_group_ids_with_tag_now() -> list:
    """
    Функция для получения из БД ID групповых чатов, у которых установлен tag_now=True.
    """
    return [str(i_group.group_tg_id) for i_group in GroupChats.objects.filter(tag_now=True).only('group_tg_id')]


@sync_to_async
def get_group_detail(group_id: int = None, group_tg_id: str = None) -> dict | None:
    """
    Функция для получения записи модели GroupChats
    """
    # Пробуем достать объект GroupChats
    try:
        if group_id:
            group_obj = GroupChats.objects.get(pk=group_id)
        elif group_tg_id:
            group_obj = GroupChats.objects.get(group_tg_id=group_tg_id)
        else:
            MY_LOGGER.warning(f'В функцию get_group_detail не был передан параметр для получения объекта GroupChats')
            return None
    except ObjectDoesNotExist:
        MY_LOGGER.warning(f'Не удалось найти GroupChats c PK={group_id}')
        return None

    # Отфильтровываем файлы и возвращаем работу функции
    group_files = [i_file.file for i_file in GroupChatFiles.objects.filter(group_chat=group_obj).only('file')]
    group_dct = {
        'group_tg_id': group_obj.group_tg_id,
        'msg_text': group_obj.msg_text,
        'group_files': group_files,
    }
    return group_dct

