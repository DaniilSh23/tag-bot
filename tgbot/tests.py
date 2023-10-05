from asgiref.sync import sync_to_async
from django.test import TestCase

from webapp.models import BotUser


# Create your tests here.
@sync_to_async
def update_or_create_bot_user(update):
    BotUser.objects.update_or_create(
        tlg_id=str(update.from_user.id),
        defaults={
            'tlg_username': update.from_user.username
        }
    )