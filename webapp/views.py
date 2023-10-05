from django.http import HttpRequest, HttpResponse
from django.shortcuts import render
from django.views import View

from tag_bot.settings import MY_LOGGER, BOT_TOKEN
from webapp.services.balance_services import BalanceServices


class BalanceView(View):
    """
    Вьюшки для страницы баланса
    """
    def get(self, request: HttpRequest) -> HttpResponse:
        MY_LOGGER.info(f'Пришёл GET запрос на вьюшку BalanceView | {request.GET}')

        # Обработка невалидного токена в запросе
        if request.GET.get('token') != BOT_TOKEN:
            MY_LOGGER.warning(f'Неверный токен в запросе ! | {request.GET.get("token")!r} != {BOT_TOKEN!r}')
            return HttpResponse(content='invalid token!', status=400)

        # Обработка невалидного tlg_id
        tlg_id = request.GET.get("tlg_id")
        if not tlg_id or not tlg_id.isdigit():
            MY_LOGGER.warning(f'Отсутствует или невалидный параметр запроса tlg_id, '
                              f'его значение: {request.GET.get("tlg_id")}')
            return HttpResponse(content='invalid request params!', status=400)

        # Выполнение бизнес-логики
        status, context = BalanceServices.make_context_for_balance_page(tlg_id=tlg_id)
        if status != 200:
            return HttpResponse(content=context, status=status)

        return render(request, template_name='webapp/balance.html', context=context)
