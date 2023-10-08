from django.db import models


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
