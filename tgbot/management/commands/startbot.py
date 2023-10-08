import random
import uvloop
from pyrogram import Client
from django.core.management import BaseCommand

from tag_bot.settings import MY_LOGGER, TG_API_ID, TG_API_HASH, BOT_TOKEN, BASE_DIR


# TODO: возможно команда будет нах не нужна, но пускай пока полежит
class Command(BaseCommand):
    """
    Команды для старта бота
    """
    def handle(self, *args, **options):
        MY_LOGGER.info(f'Вызвана команда для старта бота')

        try:
            MY_LOGGER.info('BOT IS READY TO LAUNCH!\nstarting the countdown...')
            MY_LOGGER.info('3... SET PATH TO HANDLERS')

            plugins = dict(
                root=f"tgbot.handlers",  # Указываем директорию-корень, где лежат все обработчики
                include=[  # Явно прописываем какие файлы с хэндлерами подключаем
                    "main_handlers",
                    "payment_handlers",
                ]
            )  # Путь пакета с обработчиками

            MY_LOGGER.info('2... DO SOMETHING ELSE')

            MY_LOGGER.info('1... BOT SPEED BOOST')
            uvloop.install()  # Это для ускорения работы бота

            MY_LOGGER.info('LAUNCH THIS FU... BOT NOW!!!')
            MY_LOGGER.success(f'BOT HAS BEEN IN ORBIT...{random.choice(seq=("🛰", "🛸", "🌌", "🌠", "👨‍🚀"))}')
            Client("test_bot", TG_API_ID, TG_API_HASH, bot_token=BOT_TOKEN, plugins=plugins).run()
            # Client("prod_bot", plugins=plugins).run()
        except Exception as error:
            MY_LOGGER.error(f'BOT CRASHED WITH SOME ERROR\n\t{error}')
        except (KeyboardInterrupt, SystemExit):
            MY_LOGGER.warning('BOT STOPPED BY CTRL+C!')
