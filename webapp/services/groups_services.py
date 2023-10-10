from django.core.exceptions import ObjectDoesNotExist

from tag_bot.settings import MY_LOGGER
from webapp.models import GroupChats, BotUser


class GroupsService:
    """
    Сервис для групповых чатов.
    """
    @staticmethod
    def show_my_groups(tlg_id):
        """
        Метод для отображения списка групп юзера.
        """
        MY_LOGGER.debug(f'Вызван сервис GroupsService.show_my_groups с параметром tlg_id=={tlg_id}')

        try:
            bot_user = BotUser.objects.get(tlg_id=tlg_id)
        except ObjectDoesNotExist:
            return 404, f'Not found Bot User with TG ID == {tlg_id!r}'

        groups = GroupChats.objects.filter(bot_user=bot_user).only('id', 'name', 'in_work')
        payload = {
            'groups': groups,
        }
        return 200, payload

