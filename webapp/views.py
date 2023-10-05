from django.http import HttpRequest, HttpResponse
from django.shortcuts import render
from django.views import View

from tag_bot.settings import MY_LOGGER


class BalanceView(View):
    """
    Вьюшки для страницы баланса
    """
    def get(self, request: HttpRequest) -> HttpResponse:
        MY_LOGGER.info(f'Пришёл GET запрос на вьюшку BalanceView | {request.GET}')
        return HttpResponse(content='Okay!')
