import hashlib
import time

from django.core.exceptions import ObjectDoesNotExist

from tag_bot.settings import MY_LOGGER
from webapp.models import PaymentBills, Profiles, Transaction, BotUser, BotSettings


class BalanceServices:
    """
    Сервисы для бизнес-логики, связанной с балансом и его пополнением.
    """
    @staticmethod
    def make_context_for_balance_page(tlg_id):
        """
        Метод для создания контекста для страницы баланса.
        """
        MY_LOGGER.debug(f'Вызван сервис BalanceServices.make_context_for_balance_page | tlg_id=={tlg_id}')
        try:
            profile_obj = Profiles.objects.get(bot_user__tlg_id=tlg_id)
        except ObjectDoesNotExist:
            MY_LOGGER.warning(f'Не найден профиль юзера с tlg_id == {tlg_id}')
            return 404, f'User with TG ID == {tlg_id} not found'

        context = {
            'pay_methods': PaymentBills.pay_methods_tpl,
            'balance': profile_obj.balance,
            'transaction': Transaction.objects.filter(bot_user__tlg_id=tlg_id)
        }
        return 200, context

    @staticmethod
    def create_new_bill(tlg_id, amount, pay_method):
        """
        Метод для создания нового счёта на оплату и формировании контекста для рендера страницы со 2 шагом оплаты.
        """
        try:
            bot_user = BotUser.objects.get(tlg_id=tlg_id)
        except ObjectDoesNotExist:
            MY_LOGGER.warning(f'BotUser с tlg_id == {tlg_id} не найден в БД.')
            return 404, f'BotUser с TG ID == {tlg_id} не найден!'

        bill_obj = PaymentBills.objects.create(
            bot_user=bot_user,
            amount=amount,
            pay_method=pay_method,
            bill_hash=hashlib.md5(string=f'{bot_user}{amount}{pay_method}{time.time()}'.encode('utf-8')).hexdigest()
        )
        context = {
            'to_card_pay_data': BotSettings.objects.get(key='to_card_pay_data').value,
            'bill_hash': bill_obj.bill_hash,
        }
        return 200, context
