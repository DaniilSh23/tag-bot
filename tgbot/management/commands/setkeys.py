from django.core.management import BaseCommand

from tag_bot.settings import MY_LOGGER
from webapp.models import BotSettings


class Command(BaseCommand):
    def handle(self, *args, **options):
        MY_LOGGER.info('Запуск команды для установки настроек в BotSettings')

        bot_settings = (
            ('to_card_pay_data', 'Какие-либо данные для перевода на карту, такие как номер, получатель и т.д.'),
            ('who_approve_payments', '1978587604'),
        )
        for i_bot_sett in bot_settings:
            obj, created = BotSettings.objects.update_or_create(
                key=i_bot_sett[0],
                value=i_bot_sett[1],
            )
            MY_LOGGER.success(f'Настройка {obj.key!r} {"создана" if created else "обновлена"} '
                              f'в БД со значением {obj.value[:48]!r}...')

        MY_LOGGER.info('Окончание команды для установки настроек в BotSettings')