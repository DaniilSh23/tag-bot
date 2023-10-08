from django.apps import AppConfig

# from tgbot.handlers.main_handlers import bot_hello_world
# from tgbot.start_bot import start_bot


class TgbotConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'tgbot'

    # def ready(self):
    #     """
    #     Переопределяем стандартный метод, добавляя в него логику, которая выполнится при старте данного приложения.
    #     :return:
    #     """
    #     super().ready()
    #     start_bot()
