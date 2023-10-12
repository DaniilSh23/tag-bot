import datetime
import os

from django.core.exceptions import ObjectDoesNotExist
from django.db import transaction

from tag_bot.settings import MY_LOGGER
from webapp.models import GroupChats, BotUser, GroupChatFiles
from webapp.services.balance_services import BalanceServices


class GroupsService:
    """
    Сервис для групповых чатов.
    """

    @staticmethod
    def show_groups_lst(tlg_id):
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

    @staticmethod
    def delete_group_chat(tlg_id: str, group_id: str):
        """
        Метод для удаления группового чата.
        """
        MY_LOGGER.debug(f'Вызван сервис (GroupsService.delete_group_chat) для удаления группового чата.')

        # Проверка, что есть такой юзер бота
        try:
            bot_user = BotUser.objects.get(tlg_id=tlg_id)
        except ObjectDoesNotExist:
            return 404, f'Not found Bot User with TG ID == {tlg_id!r}'

        # Проверяем, что в БД есть групповой чат для данного пользователя с таким PK
        try:
            group_chat = GroupChats.objects.get(pk=group_id, bot_user=bot_user)
        except ObjectDoesNotExist:
            return 404, f'Not found Bot Group Chat with ID == {group_id!r} for User TG ID == {tlg_id!r}'

        group_chat.delete()
        return 200, 'ok'

    @staticmethod
    def show_group_detail(tlg_id: str, group_id: int):
        """
        Сервис для детального отображения инфы о группе.
        """
        MY_LOGGER.debug(f'Вызван сервис GroupsService.show_group_detail с пар-ми: '
                        f'tlg_id=={tlg_id} & group_id={group_id}')

        # Проверяем наличие в БД юзера
        try:
            bot_user = BotUser.objects.get(tlg_id=tlg_id)
        except ObjectDoesNotExist:
            return 404, f'Not found Bot User with TG ID == {tlg_id!r}'

        # Проверяем наличие в БД группового чата
        try:
            group_chat = GroupChats.objects.get(pk=group_id, bot_user=bot_user)
        except ObjectDoesNotExist:
            return 404, f'Not found Bot Group Chat with ID == {group_id!r} for User TG ID == {tlg_id!r}'

        group_chat_files = GroupChatFiles.objects.filter(group_chat=group_chat)
        return 200, {
            'group_chat': group_chat,
            'group_chat_files': group_chat_files,
        }

    @staticmethod
    def create_group_chat(tlg_id: str, group_name: str, tag_now: bool, msg_text: str,
                          new_group_chat_files: list, group_tg_id: str):
        """
        Метод для создания группового чата.
        """
        MY_LOGGER.debug(f'Вызван сервис (GroupsService.create_group_chat) для создания группового чата.')

        # Проверяем наличие в БД юзера
        try:
            bot_user = BotUser.objects.get(tlg_id=tlg_id)
        except ObjectDoesNotExist:
            MY_LOGGER.warning(f'Не удалось найти юзера с tlg_id == {tlg_id}')
            return 404, f'Not found Bot User with TG ID == {tlg_id!r}'

        # Проверка, что баланс позволяет оплатить группу на сутки
        if not BalanceServices.check_user_balance(tlg_id=tlg_id):
            return 400, f'Недостаточно средств'

        # TODO: пока этот шаг опускаем, почему-то бот не может получить инфу о чате
        # Отправляем боту команду на проверку своих прав в групповом чате
        # send_message_from_bot(text=f'$$$check_bot_permissions {group_link}')

        # Кидаем в одну транзакцию списание средств и создание групповых чатов
        with transaction.atomic():

            # Списываем деньги
            BalanceServices.writing_off_money(tlg_id=tlg_id)

            # Создаём групповой чат
            group_chat = GroupChats.objects.create(
                bot_user=bot_user,
                name=group_name,
                group_tg_id=group_tg_id,
                msg_text=msg_text,
                tag_now=tag_now,
                paid_by=datetime.datetime.now() + datetime.timedelta(days=1),
                in_work=True
            )

            # Создаём файлы для группового чата
            if new_group_chat_files:
                GroupChatFiles.objects.bulk_create(
                    [
                        GroupChatFiles(group_chat=group_chat, file=i_file, file_name=os.path.split(i_file.name)[-1])
                        for i_file in new_group_chat_files
                    ]
                )

        # Даём успешный ответ работы сервиса
        group_chat_files = GroupChatFiles.objects.filter(group_chat=group_chat)
        return 200, {
            'group_chat': group_chat,
            'group_chat_files': group_chat_files,
        }

    @staticmethod
    def update_group_chat(tlg_id: str, group_id: int, delete_files_pk: list, group_name: str, tag_now: bool,
                          msg_text: str, new_group_chat_files: list):
        """
        Метод для обновления группового чата
        """
        MY_LOGGER.debug(f'Вызван сервис (GroupsService.update_group_chat) для обновления группового чата '
                        f'с PK {group_id}')

        # Проверяем наличие в БД юзера
        try:
            bot_user = BotUser.objects.get(tlg_id=tlg_id)
        except ObjectDoesNotExist:
            return 404, f'Not found Bot User with TG ID == {tlg_id!r}'

        # Проверяем наличие в БД группового чата
        try:
            group_chat = GroupChats.objects.get(pk=group_id, bot_user=bot_user)
        except ObjectDoesNotExist:
            return 404, f'Not found Bot Group Chat with ID == {group_id!r} for User TG ID == {tlg_id!r}'

        # Обновляем данные группового чата
        group_chat.name = group_name
        group_chat.tag_now = tag_now
        group_chat.msg_text = msg_text
        group_chat.save()

        # Удаляем файлы
        del_files_numb = GroupChatFiles.objects.filter(pk__in=delete_files_pk).delete()
        MY_LOGGER.debug(f'Удалено {del_files_numb!r} объектов GroupChatFiles, pk in {delete_files_pk!r}')

        # Создаём новые файлы
        if new_group_chat_files:
            GroupChatFiles.objects.bulk_create(
                [
                    GroupChatFiles(group_chat=group_chat, file=i_file, file_name=os.path.split(i_file.name)[-1])
                    for i_file in new_group_chat_files
                ]
            )

        group_chat_files = GroupChatFiles.objects.filter(group_chat=group_chat)
        return 200, {
            'update_rslt': 'Успешно обновлено!',
            'group_chat': group_chat,
            'group_chat_files': group_chat_files,
        }
