import os
from PIL import Image
from django.core.files.uploadedfile import UploadedFile

from tag_bot.settings import MEDIA_ROOT, MY_LOGGER, BOT_TOKEN
from webapp.models import BotSettings
import requests


def handle_uploaded_file(file: UploadedFile, bill_pk: int):
    """
    Обработка загружаемых файлов
    """
    # Создаём папку bill_files, если её ещё нет
    if not os.path.exists(os.path.join(MEDIA_ROOT, 'bill_files')):
        os.mkdir(os.path.join(MEDIA_ROOT, 'bill_files'))

    file_path = os.path.join(MEDIA_ROOT, 'bill_files', f"{bill_pk}_{file.name}")

    # Файл открыт для дозаписи (wb+), так как он будет разбит на чанки
    with open(file_path, mode='wb+') as destination:

        # Использование UploadedFile.chunks() гарантирует что оперативка системы не будет перегружена большим файлом
        for chunk in file.chunks():
            destination.write(chunk)

    return file_path


def send_message_from_bot(text, disable_notification=True, file_path=None, target_chat=None):
    """
    Функция для отправки сообщений от лица бота.
    Если не указан file_path, то будет выполнен метод TG API sendMessage, иначе sendDocument.
    Если не указан target_chat, то из БД будет взят ID юзера, под ключом who_approve_payments
    """
    MY_LOGGER.info(f'Выполняем функцию для отправки сообщения от лица бота. Текст: {text!r}.')

    if not target_chat:
        target_chat = BotSettings.objects.get(key='who_approve_payments').value
    url = f'https://api.telegram.org/bot{BOT_TOKEN}/'
    data = {'chat_id': target_chat, 'disable_notification': disable_notification, 'parse_mode': 'HTML'}

    # Ветвление: команда сразу с файлом или без
    MY_LOGGER.debug(f'Готовим данные и выполняем запрос на отправку сообщения от бота, данные запроса: {data}')
    if file_path:

        # Открываем файл, как байты и посылаем запрос
        with open(file=file_path, mode='rb') as file:
            file_name = os.path.split(file_path)[-1]
            data['caption'] = text
            files = {'document': (file_name, file)}
            response = requests.post(url=f"{url}sendDocument", data=data, files=files)
    else:
        data['text'] = text
        response = requests.post(url=f"{url}sendMessage", data=data)

    if response.status_code != 200:  # Обработка неудачного запроса на отправку
        MY_LOGGER.error(f'Неудачная отправка сообщения от лица бота.\n'
                        f'Запрос: url={url} | data={data}\n'
                        f'Ответ:{response.json()}')
        return
    MY_LOGGER.success(f'Успешная отправка сообщения {text!r} от лица бота.')
    return True


def is_image(file_path: str) -> bool:
    """
    Функция для проверки, что файл является изображением
    """
    try:
        img = Image.open(file_path)
        img.verify()
        return True
    except Exception:
        return False