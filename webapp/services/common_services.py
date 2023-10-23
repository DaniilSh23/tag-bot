from django.core.exceptions import ObjectDoesNotExist

from tag_bot.settings import MY_LOGGER
from webapp.models import BotSettings


class FAQandSupportService:
    """
    Сервис для поддержки и FAQ.
    """
    @staticmethod
    def make_reviews_context():
        """
        Метод для формирования контекста для раздела с отзывами.
        """
        MY_LOGGER.debug('Вызван сервис для генерации контекста для раздела с отзывами')
        try:
            reviews_text = BotSettings.objects.get(key='reviews_text').value
            reviews_link = BotSettings.objects.get(key='reviews_link').value
        except ObjectDoesNotExist:
            MY_LOGGER.warning('Не найдена запись в BotSettings по ключу "reviews_text" или "reviews_link"!')
            return

        return {'reviews_link': reviews_link, 'reviews_text': reviews_text}

    @staticmethod
    def make_support_context():
        """
        Метод для формирования контекста для поддержки
        """
        MY_LOGGER.debug('Вызван сервис для генерации контекста для страницы поддержки')
        try:
            support_text = BotSettings.objects.get(key='support_text').value
            support_link = BotSettings.objects.get(key='support_link').value
        except ObjectDoesNotExist:
            MY_LOGGER.warning('Не найдена запись в BotSettings по ключу "support_text" или "support_link"!')
            return

        return {'support_link': support_link, 'support_text': support_text}

    @staticmethod
    def make_faq_context():
        """
        Метод для формирования контекста для FAQ.
        """
        MY_LOGGER.debug('Вызван сервис для генерации контекста для страницы FAQ')
        try:
            faq_info = BotSettings.objects.get(key='faq_info').value
        except ObjectDoesNotExist:
            MY_LOGGER.warning('Не найдена запись в BotSettings по ключу "faq_info"!')
            return
        return {'faq_info': faq_info}
