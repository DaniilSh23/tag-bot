import datetime
import time

import pytz
from celery import shared_task

from tag_bot.settings import TIME_ZONE, MY_LOGGER
from webapp.models import PaymentBills


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
