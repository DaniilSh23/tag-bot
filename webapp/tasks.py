import datetime
import time

import pytz
from celery import shared_task

from tag_bot.settings import TIME_ZONE, MY_LOGGER
from webapp.models import PaymentBills, GroupChats
from webapp.services.balance_services import BalanceServices


@shared_task
def scheduled_task_example():
    """
    Пример отложенной задачи, которая печатает в консоль.
    """
    time.sleep(5)
    print(f'Привет мир, я отложенная задача. Сейчас: {datetime.datetime.utcnow()}')


@shared_task
def close_expired_bills():
    """
    Таск селери для закрытия истекших счетов на оплату.
    """
    MY_LOGGER.debug('Запущена задачка по закрытию устаревших счетов')
    expired_dt = datetime.datetime.now(tz=pytz.timezone(TIME_ZONE)) - datetime.timedelta(hours=3)
    bills_qset = PaymentBills.objects.filter(created_at__lt=expired_dt).only('id', 'status')
    bills_qset.update(status='close_without_pay')
    MY_LOGGER.debug('Окончена задачка по закрытию устаревших счетов')


@shared_task
def check_subs():
    """
    Таск селери для проверки подписок.
    """
    MY_LOGGER.debug(f'Запущен таск селери для проверки подписок.')

    # Достаём из БД истекшие группы и вытаскиваем отдельно PK юзеров бота
    now_dt = datetime.datetime.now(tz=pytz.timezone(TIME_ZONE))
    groups_qset = (GroupChats.objects.filter(paid_by__lt=now_dt)
                   .only('id', 'bot_user', 'in_work', 'paid_by').prefetch_related('bot_user'))
    users_pks = set([i_group.bot_user.pk for i_group in groups_qset])

    # Итерируемся по юзерам бота и обрабатываем группы каждого
    for i_usr_pk in users_pks:
        users_groups = groups_qset.filter(bot_user__pk=i_usr_pk)
        tlg_id = users_groups[0].bot_user.tlg_id

        # TODO: тут по-тупому списание, да и неоптимальная работа с БД. Надо обновлять множество групп за раз.
        #  Но будет финансирование - буду и тратить время на оптимизацию.
        # Итерируемся по группам конкретного юзера
        for i_group in users_groups:
            check_balance_rslt = BalanceServices.check_user_balance(tlg_id=tlg_id)

            # У юзера не хватает баланса, чтобы продлить группу
            if not check_balance_rslt:
                MY_LOGGER.debug(f'Останавливаем группу PK == {i_group.id} юзера PK == {i_usr_pk}')
                i_group.in_work = False
                i_group.save()
                continue

            # Продлеваем для юзера группу
            extend_until = now_dt + datetime.timedelta(days=1)
            BalanceServices.writing_off_money(tlg_id=tlg_id)
            i_group.in_work = True
            i_group.paid_by = extend_until
            i_group.save()
            MY_LOGGER.debug(f'Обслуживание группы PK = {i_group.id} юзера PK = {i_usr_pk} продлено до {extend_until}')

    MY_LOGGER.debug(f'Окончен таск селери для проверки подписок!')