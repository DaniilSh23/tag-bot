from django.core.exceptions import ObjectDoesNotExist

from tag_bot.settings import MY_LOGGER
from webapp.models import PaymentBills, Profiles


class BalanceServices:
    """
    Сервисы для бизнес-логики, связанной с балансом и его пополнением.
    """
    @staticmethod
    def make_context_for_balance_page(tlg_id):
        """
        Метод для создания контекста для страницы баланса.
        """
        try:
            profile_obj = Profiles.objects.get(bot_user__tlg_id=tlg_id)
        except ObjectDoesNotExist:
            MY_LOGGER.warning(f'Не найден профиль юзера с tlg_id == {tlg_id}')
            return 404, f'User with TG ID == {tlg_id} not found'

        context = {
            'pay_methods': PaymentBills.pay_methods_tpl,
            'balance': profile_obj.balance,
        }
        return 200, context
