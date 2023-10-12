import hashlib
import time
from typing import Tuple

from django.core.exceptions import ObjectDoesNotExist
from django.core.files.uploadedfile import UploadedFile
from django.db import transaction

from tag_bot.settings import MY_LOGGER
from webapp.models import PaymentBills, Profiles, Transaction, BotUser, BotSettings
from webapp.utils import handle_uploaded_file, send_message_from_bot


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
        send_cmnd_rslt = send_message_from_bot(
            text=f'<tg-spoiler>$$$confirm_payment {bill_hash}</tg-spoiler>',
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

    @staticmethod
    def confirm_or_decline_payment(bill_hash, bill_comment, tg_msg_id, accept_pay_flag):
        """
        Метод для подтверждения или отклонения платежа.
        """
        MY_LOGGER.debug(f'Вызван сервис подтверждения или отклонения платежа.')

        # Достаём из БД объект счета
        try:
            bill_obj = PaymentBills.objects.get(bill_hash=bill_hash)
        except ObjectDoesNotExist:
            MY_LOGGER.warning(f'Объект счета с хэшем {bill_hash!r} не найден в БД!')
            return 404, 'Счет отсутствует или просрочен.'

        if accept_pay_flag == 1:
            # Изменяем статус счет, создаем транзакцию и пополняем баланс
            with transaction.atomic():
                bill_obj.status = 'payed'
                bill_obj.save()
                profile_obj = Profiles.objects.get(bot_user=bill_obj.bot_user)
                profile_obj.balance = float(profile_obj.balance) + float(bill_obj.amount)
                profile_obj.save()
                Transaction.objects.create(
                    bot_user=bill_obj.bot_user,
                    amount=bill_obj.amount,
                    operation_type="depositing",
                    description=f'Пополнение баланса. Комментарий подтверждения: {bill_comment!r}',
                )

            # Отправляем уведомление для пользователя
            send_message_from_bot(
                text=f'💰 <b>Ваш баланс пополнен на {bill_obj.amount} руб.</b>\n\n'
                     f'💬 Комментарий: <i>{bill_comment!r}</i>',
                target_chat=bill_obj.bot_user.tlg_id,
                disable_notification=False,
            )

            # Изменяем сообщение с кнопкой у админа
            send_message_from_bot(
                text=f'$$$del_msg {tg_msg_id} confirm_pay {bill_obj.pk}',
                disable_notification=True,
            )

        # Если платёж отклонён
        else:
            bill_obj.status = 'decline'
            bill_obj.save()

            # Отправляем уведомление для пользователя
            send_message_from_bot(
                text=f'🙅‍♂️ <b>Ваш платёж по счету № {bill_obj.pk} был отклонён!</b>\n\n'
                     f'💬 Комментарий: <i>{bill_comment!r}</i>',
                target_chat=bill_obj.bot_user.tlg_id,
                disable_notification=False,
            )

            # Изменяем сообщение с кнопкой у админа
            send_message_from_bot(
                text=f'$$$del_msg {tg_msg_id} decline_pay {bill_obj.pk}',
                disable_notification=True,
            )
        return 200, {
            'header': 'Обработка платежа выполнена',
            'description': f'Счету № {bill_obj.pk} установлен статус {bill_obj.status}. '
                           f'Ваш комментарий отправлен пользователю с TG ID {bill_obj.bot_user.tlg_id}',
            'btn_text': 'Ок. Понял.'
        }

    @staticmethod
    def check_user_balance(tlg_id: str, groups_numb=1) -> bool:
        """
        Метод для проверки, что баланс пользователя позволяет ему оформить группу на следующие сутки
        """
        MY_LOGGER.debug(f'Запущен сервис BalanceServices.check_user_balance с параметрами: '
                        f'tlg_id == {tlg_id}, groups_numb == {groups_numb}')

        user_balance = float(Profiles.objects.get(bot_user__tlg_id=tlg_id).balance)
        tariff = float(BotSettings.objects.get(key='tariff').value)

        # Проверяем, что баланс юзера позволяет оплатить группы
        if user_balance >= tariff * groups_numb:
            return True
        return False

    @staticmethod
    def writing_off_money(tlg_id: str, groups_numb: int = 1):
        """
        Метод для списания денежных средств с баланса пользователя за обслуживание групповых чатов.
        """
        MY_LOGGER.debug(f'Запущен сервис BalanceServices.writing_off_money с параметрами: '
                        f'tlg_id == {tlg_id}, groups_numb == {groups_numb}')

        user_profile = Profiles.objects.get(bot_user__tlg_id=tlg_id)
        tariff = float(BotSettings.objects.get(key='tariff').value)
        pay_amount = tariff * groups_numb

        with transaction.atomic():

            # Списываем деньги
            user_profile.balance = float(user_profile.balance) - pay_amount
            user_profile.save()

            # Записываем операцию в транзакцию
            Transaction.objects.create(
                bot_user=user_profile.bot_user,
                amount=pay_amount,
                operation_type='writing_off',
                description=f'Суточная плата за обслуживание групп в кол-ве {groups_numb!r}',
            )


