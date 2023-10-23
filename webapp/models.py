import os

from django.db import models
from django.db.models.signals import pre_delete, pre_save
from django.dispatch import receiver

from tag_bot import settings
from tag_bot.settings import MY_LOGGER


class BotUser(models.Model):
    """
    Модель для юзеров бота
    """
    tlg_id = models.CharField(verbose_name='tlg_id', max_length=30, db_index=True)
    tlg_username = models.CharField(verbose_name='username', max_length=100, blank=False, null=True)
    start_bot_at = models.DateTimeField(verbose_name='первый старт', auto_now_add=True)

    def __str__(self):
        return f'User TG_ID {self.tlg_id}'

    class Meta:
        ordering = ['-start_bot_at']
        verbose_name = 'юзер бота'
        verbose_name_plural = 'юзеры бота'


class Profiles(models.Model):
    """
    Модель для различных данных профиля пользователя
    """
    bot_user = models.OneToOneField(verbose_name='юзер', to=BotUser, on_delete=models.CASCADE)
    balance = models.DecimalField(verbose_name='баланс', max_digits=10, decimal_places=2)

    class Meta:
        ordering = ['-id']
        verbose_name = 'профиль юзера'
        verbose_name_plural = 'профили пользователей'

    def __str__(self):
        return f"профиль {self.bot_user.tlg_username if self.bot_user.tlg_username else self.bot_user.tlg_id}"


class BotSettings(models.Model):
    """
    Настройки бота.
    """
    key = models.CharField(verbose_name='ключ', max_length=50)
    value = models.TextField(verbose_name='значение')

    class Meta:
        ordering = ['-id']
        verbose_name = 'настройка бота'
        verbose_name_plural = 'настройки бота'


class PaymentBills(models.Model):
    """
    Счета для оплаты.
    """
    pay_methods_tpl = (
        ('to_card', 'перевод на карту'),
    )
    statuses_tpl = (
        ('created', 'создан'),
        ('on_check', 'на проверке'),
        ('payed', 'оплачен'),
        ('decline', 'отклонен'),
        ('close_without_pay', 'закрыт без оплаты'),
    )

    bot_user = models.ForeignKey(verbose_name='юзер', to=BotUser, on_delete=models.CASCADE)
    amount = models.DecimalField(verbose_name='сумма', decimal_places=2, max_digits=10)
    created_at = models.DateTimeField(verbose_name='когда создан', auto_now_add=True)
    pay_method = models.CharField(verbose_name='способ оплаты', choices=pay_methods_tpl)
    status = models.CharField(verbose_name='статус', choices=statuses_tpl, default='created')
    file = models.FileField(verbose_name='файл', null=True, upload_to='bill_files/')
    bill_hash = models.CharField(verbose_name='хэш', max_length=100, blank=True, null=True)

    class Meta:
        ordering = ['-id']
        verbose_name = 'счет на оплату'
        verbose_name_plural = 'счета на оплату'


@receiver(pre_delete, sender=PaymentBills)
def delete_group_chat_file(sender, instance, **kwargs):
    """
    Функция, которая получает сигнал при удалении модели PaymentBills и удаляет файл
    """
    if instance.file:
        file_path_string = os.path.join(settings.MEDIA_ROOT, instance.file.name)
        if os.path.exists(file_path_string):
            os.remove(file_path_string)  # Удаляем файл


class Transaction(models.Model):
    """
    Транзакции. Деньги пришли, деньги ушли, когда, сколько и почему.
    """
    operations_types_tpl = (
        ('depositing', 'зачисление'),
        ('writing_off', 'списание'),
    )

    bot_user = models.ForeignKey(verbose_name='юзер', to=BotUser, on_delete=models.CASCADE)
    amount = models.DecimalField(verbose_name='сумма', decimal_places=2, max_digits=10)
    operation_type = models.CharField(verbose_name='тип операции', choices=operations_types_tpl)
    created_at = models.DateTimeField(verbose_name='дата и время', auto_now_add=True)
    description = models.TextField(verbose_name='описание')

    class Meta:
        ordering = ['-id']
        verbose_name = 'транзакция'
        verbose_name_plural = 'транзакции'


class GroupChats(models.Model):
    """
    Модель для хранения инфы о подключенных групповых чатах.
    """
    bot_user = models.ForeignKey(verbose_name='владелец', to=BotUser, on_delete=models.CASCADE)
    name = models.CharField(verbose_name='название', max_length=100)
    link = models.URLField(verbose_name='ссылка', blank=True, null=True)
    group_tg_id = models.CharField(verbose_name='TG ID чата', max_length=200, blank=True, null=True)
    msg_text = models.TextField(verbose_name='текст сообщения')
    tag_now = models.BooleanField(verbose_name='тегать сразу', default=False)
    bot_rights_checked = models.BooleanField(verbose_name='права бота проверены', default=False)
    in_work = models.BooleanField(verbose_name='в работе', default=False)
    paid_by = models.DateTimeField(verbose_name='оплачена до', auto_now_add=False, auto_now=False, blank=True, null=True)
    created_at = models.DateTimeField(verbose_name='когда создана', auto_now_add=True)

    class Meta:
        ordering = ['-id']
        verbose_name = 'групповой чат'
        verbose_name_plural = 'групповые чаты'


class GroupChatFiles(models.Model):
    """
    Файлы для групповых чатов
    """
    group_chat = models.ForeignKey(verbose_name='групповой чат', to=GroupChats, on_delete=models.CASCADE)
    file = models.FileField(verbose_name='файл', upload_to='group_chats')
    file_name = models.CharField(verbose_name='имя', blank=True, null=True)

    class Meta:
        ordering = ['-id']
        verbose_name = 'файл для гр.чата'
        verbose_name_plural = 'файлы для гр.чатов'


@receiver(pre_save, sender=GroupChatFiles)
def generate_group_chat_file_name(sender, instance: GroupChatFiles, **kwargs):
    """
    Функция для генерации имени файла
    """
    MY_LOGGER.debug(f'Обработка сигнала pre_save от модели GroupChatFiles')
    instance.file_name = os.path.split(instance.file.name)[-1]


@receiver(pre_delete, sender=GroupChatFiles)
def delete_group_chat_file(sender, instance, **kwargs):
    """
    Функция, которая получает сигнал при удалении модели GroupChatFiles и удаляет файл
    """
    MY_LOGGER.debug(f'Обработка сигнала pre_delete от модели GroupChatFiles')
    if instance.file:
        file_path_string = os.path.join(settings.MEDIA_ROOT, instance.file.name)
        if os.path.exists(file_path_string):
            os.remove(file_path_string)  # Удаляем файл
