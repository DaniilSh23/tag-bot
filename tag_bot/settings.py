"""
Django settings for tag_bot project.

Generated by 'django-admin startproject' using Django 4.2.6.

For more information on this file, see
https://docs.djangoproject.com/en/4.2/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/4.2/ref/settings/
"""
import asyncio
import os

import uvloop
from pyrogram import Client
from pathlib import Path
import loguru
import sys
from pathlib import Path
import environ
from celery.schedules import crontab


# Это отсюда https://django-environ.readthedocs.io/en/latest/quickstart.html
env = environ.Env(
    # set casting, default value
    DEBUG=bool,  # Для переменной DEBUG указываем тип данных, когда достаём из .env
    SECRET_KEY=str,
    DOMAIN_NAME=str,
    REDIS_HOST=str,
    REDIS_PORT=str,
    DATABASE_NAME=str,
    DATABASE_USER=str,
    DATABASE_PASSWORD=str,
    DATABASE_HOST=str,
    DATABASE_PORT=str,
    TG_API_ID=str,
    TG_API_HASH=str,
    BOT_TOKEN=str,
    SHOW_SQL_LOG=bool,
    SENTRY_DSN=str,
    BASE_HOST=str,
    DJANGO_SUPERUSER_USERNAME=str,
    DJANGO_SUPERUSER_PASSWORD=str,
    TAG_NOW_INTERVAL=int,
)

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent

# Take environment variables from .env file
# Это отсюда https://django-environ.readthedocs.io/en/latest/quickstart.html
environ.Env.read_env(BASE_DIR / '.env')

# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/4.2/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = env('SECRET_KEY')

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = env('DEBUG')

ALLOWED_HOSTS = ['*']
DOMAIN_NAME = env('DOMAIN_NAME')
BASE_HOST = env('BASE_HOST')
DJANGO_SUPERUSER_USERNAME = env('DJANGO_SUPERUSER_USERNAME')
DJANGO_SUPERUSER_PASSWORD = env('DJANGO_SUPERUSER_PASSWORD')

# Application definition

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',

    # свои приложения
    'webapp.apps.WebappConfig',
    'tgbot.apps.TgbotConfig',

    # сторонние приложения
    'rest_framework',
    'drf_spectacular',
    'django_filters',
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'tag_bot.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]

WSGI_APPLICATION = 'tag_bot.wsgi.application'

# Database
# https://docs.djangoproject.com/en/4.2/ref/settings/#databases

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql_psycopg2',
        'NAME': env('DATABASE_NAME'),
        'USER': env('DATABASE_USER'),
        'PASSWORD': env('DATABASE_PASSWORD'),
        'HOST': env('DATABASE_HOST'),
        'PORT': env('DATABASE_PORT'),
    }
}

# Password validation
# https://docs.djangoproject.com/en/4.2/ref/settings/#auth-password-validators

AUTH_PASSWORD_VALIDATORS = [
    {
        'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator',
    },
]

# REST FRAMEWORK settings
REST_FRAMEWORK = {
    'DEFAULT_SCHEMA_CLASS': 'drf_spectacular.openapi.AutoSchema',
    'DEFAULT_PAGINATION_CLASS': 'rest_framework.pagination.PageNumberPagination',
    'PAGE_SIZE': 10,
    'DEFAULT_FILTER_BACKENDS': ['django_filters.rest_framework.DjangoFilterBackend']
}

# DRF SPECTACULAR settings
SPECTACULAR_SETTINGS = {
    'TITLE': 'Tag Bot API',
    'DESCRIPTION': 'API for Tag Bot Project',
    'VERSION': '1.0.0',
    'SERVE_INCLUDE_SCHEMA': False,
}

# Internationalization
# https://docs.djangoproject.com/en/4.2/topics/i18n/

LANGUAGE_CODE = 'ru-ru'

TIME_ZONE = 'Europe/Moscow'

USE_I18N = True

USE_TZ = True

# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/4.2/howto/static-files/

STATIC_URL = 'static/'
if DEBUG:
    STATICFILES_DIRS = (
        BASE_DIR / 'static',
    )
else:
    STATIC_ROOT = BASE_DIR / "static"

MEDIA_URL = '/media/'  # путь в адресной строке для получения медиа-файлов
MEDIA_ROOT = BASE_DIR / 'media'  # путь к медиа-файлам на диске
if not os.path.exists(MEDIA_ROOT):  # если папки media нет, то создаём её
    os.mkdir(MEDIA_ROOT)

# Default primary key field type
# https://docs.djangoproject.com/en/4.2/ref/settings/#default-auto-field

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

# Celery settings
REDIS_HOST = env('REDIS_HOST')
REDIS_PORT = env('REDIS_PORT')
CELERY_BROKER_URL = f"redis://{REDIS_HOST}:{REDIS_PORT}"  # Это адрес брокера сообщений (у нас Redis)
CELERY_RESULT_BACKEND = f"redis://{REDIS_HOST}:{REDIS_PORT}"  # Это адрес бэкэнда результатов (тоже у нас Redis)
CELERY_TIMEZONE = "Europe/Moscow"  # Временная зона для Celery
CELERY_BEAT_SCHEDULE = {  # Настройки шедуля
    # Закрытие истекших счетов на оплату
    'close_expired_bills': {
        'task': 'webapp.tasks.close_expired_bills',
        'schedule': 60 * 5,
    },
    # Проверка подписок
    'check_subs': {
        'task': 'webapp.tasks.check_subs',
        'schedule': 60 * 60,
        # 'schedule': 5,
    },
    # Примеры ниже
    'test_by_crontab': {
        'task': 'webapp.tasks.scheduled_task_example',
        'schedule': crontab(hour=11, minute=30, day_of_week=1),  # Запуск в понедельник в 11:30
    }
}

# Настройки логгера
MY_LOGGER = loguru.logger
MY_LOGGER.remove()  # Удаляем все предыдущие обработчики логов
MY_LOGGER.add(sink=sys.stdout, level='DEBUG')  # Все логи от DEBUG и выше в stdout
MY_LOGGER.add(  # системные логи в файл
    sink=f'{BASE_DIR}/logs/sys_log.log',
    level='DEBUG',
    rotation='2 MB',
    compression="zip",
    enqueue=True,
    backtrace=True,
    diagnose=True
)

# Настройки для Telegram
BOT_TOKEN = env('BOT_TOKEN')
TG_API_ID = env('TG_API_ID')
TG_API_HASH = env('TG_API_HASH')
LOOP = asyncio.new_event_loop()
asyncio.set_event_loop(LOOP)
TAG_NOW_INTERVAL = env('TAG_NOW_INTERVAL')
LAST_TAG_MESSAGES_IN_CHATS = dict()  # {pyro ID чата: объект TagMsgEntity | str, ...}

# Настройки для проксирования запросов от Nginx при деплое через докер
CSRF_TRUSTED_ORIGINS = ['http://0.0.0.0:8000']
SECURE_PROXY_SSL_HEADER = ('HTTP_X_FORWARDED_PROTO', 'https')
USE_X_FORWARDED_HOST = True

# Настройка логирование запросов к БД
SHOW_SQL_LOG = env('SHOW_SQL_LOG')
if SHOW_SQL_LOG:
    LOGGING = {
        'version': 1,
        'filters': {
            'require_debug_true': {
                '()': 'django.utils.log.RequireDebugTrue',
            },
        },
        'handlers': {
            'console': {
                'level': 'DEBUG',
                'filters': ['require_debug_true'],
                'class': 'logging.StreamHandler',
            },
        },
        'loggers': {
            'django.db.backends': {
                'level': 'DEBUG',
                'handlers': ['console'],
            },
        },
    }

# Настройки размера загружаемых файлов
DATA_UPLOAD_MAX_MEMORY_SIZE = 104857600  # 100 MB
DATA_UPLOAD_MAX_FILE_SIZE = 104857600  # 100 MB

# Настройка sentry для отлова ошибок
import sentry_sdk
from sentry_sdk.integrations.django import DjangoIntegration

SENTRY_DSN = env("SENTRY_DSN")
sentry_sdk.init(
    dsn=SENTRY_DSN,
    integrations=[DjangoIntegration()],
    # If you wish to associate users to errors (assuming you are using
    # django.contrib.auth) you may enable sending PII data.
    send_default_pii=True,
    # Set traces_sample_rate to 1.0 to capture 100%
    # of transactions for performance monitoring.
    # We recommend adjusting this value in production.
    traces_sample_rate=1.0,
    # Set profiles_sample_rate to 1.0 to profile 100%
    # of sampled transactions.
    # We recommend adjusting this value in production.
    profiles_sample_rate=1.0,
)
