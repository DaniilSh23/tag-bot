import hashlib
import time

from django.core.exceptions import ObjectDoesNotExist
from django.core.files.uploadedfile import UploadedFile

from tag_bot.settings import MY_LOGGER
from webapp.models import PaymentBills, Profiles, Transaction, BotUser, BotSettings
from webapp.utils import handle_uploaded_file, send_command_to_bot


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
            'pay_method': bill_obj.pay_method,
            'amount': bill_obj.amount,
        }
        return 200, context

    @staticmethod
    def get_bill(bill_hash):
        """
        Метод для получения из БД инфы о созданном счете на оплату.
        """
        MY_LOGGER.debug(f'Запущен сервис BalanceServices.get_bill c хэшем {bill_hash!r}')
        try:
            bill_obj = PaymentBills.objects.get(bill_hash=bill_hash)
        except ObjectDoesNotExist:
            MY_LOGGER.warning(f'Объект счета на оплату с хэшем {bill_hash!r} не найден в БД!')
            return 404, 'Счет не найден'

        context = {
            'to_card_pay_data': BotSettings.objects.get(key='to_card_pay_data').value,
            'bill_hash': bill_obj.bill_hash,
            'pay_method': bill_obj.pay_method,
            'amount': bill_obj.amount,
            'created_at': bill_obj.created_at,
            'status': bill_obj.status,
            'bot_user': bill_obj.bot_user,
        }
        return 200, context

    @staticmethod
    def update_bill_and_send_for_confirmation(bill_file: UploadedFile, bill_hash: str):
        """
        Метод для обновления счета и отправки его для подтверждения.
        """
        MY_LOGGER.debug(f'Запущен сервис BalanceServices.update_bill_and_send_for_confirmation')

        try:
            bill_obj = PaymentBills.objects.get(bill_hash=bill_hash)
        except ObjectDoesNotExist:
            MY_LOGGER.warning(f'Объект счета с хэшем {bill_hash!r} не найден в БД!')
            return 404, 'Счет отсутствует или просрочен.'

        # Сохраняем файл на диск хоста
        file_path = handle_uploaded_file(file=bill_file, bill_pk=bill_obj.pk)

        # Отправка команды боту для выполнения логики по подтверждению платежа (см tgbot.handlers.payment_handlers)
        send_cmnd_rslt = send_command_to_bot(
            command=f'<tg-spoiler>$$$confirm_payment {bill_hash}</tg-spoiler>',
            file_path=file_path,
            disable_notification=False,
        )
        if not send_cmnd_rslt:
            return 400, 'Не удалось отправить платёж на подтверждение. Пожалуйста, повторите позже.'

        bill_obj.file = file_path
        bill_obj.status = 'on_check'
        bill_obj.save()

        context = {
            "header": f"☑️ Оплата по счету № {bill_obj.pk} проверяется",
            "description": f"💸 Оплата по счету № {bill_obj.pk} в размере {bill_obj.amount} отправлена на "
                           f"подтверждение. Проверка происходит в ручном режиме, поэтому нужно будет немного"
                           f" подождать ⌛️. Вы получите уведомление сразу же, как мы обработаем Ваш платёж 💬.",
            "btn_text": "👌 Спасибо, жду",
        }
        return 200, context
