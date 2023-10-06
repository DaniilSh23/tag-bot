from django.http import HttpRequest, HttpResponse, HttpResponseRedirect
from django.shortcuts import render, redirect
from django.urls import reverse_lazy
from django.views import View
from django.contrib import messages as err_msgs

from tag_bot.settings import MY_LOGGER, BOT_TOKEN
from webapp.forms import BalanceForm
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

    def post(self, request):
        """
        Обработка POST запроса. Сюда приходит способ оплаты, сумма и tlg_id юзера.
        """
        MY_LOGGER.info(f'Пришёл POST запрос на вьюшку BalanceView | {request.POST}')

        form = BalanceForm(request.POST)
        if form.is_valid():

            # Выполняем бизнес-логику
            status, payload = BalanceServices.create_new_bill(
                tlg_id=form.cleaned_data.get("tlg_id"),
                amount=form.cleaned_data.get("amount"),
                pay_method=form.cleaned_data.get("pay_method"),
            )
            if status != 200:
                MY_LOGGER.warning(f'Сервис неудачно обработал данные запроса и вернул: status=={status}, '
                                  f'description={payload}')
                err_msgs.error(request, message=payload)
                return HttpResponse(content=payload, status=status)
            return render(request, template_name='webapp/sec_pay_step.html', context=payload)

        else:
            MY_LOGGER.warning(f'Данные формы невалидны | {form.errors!r}')
            err_msgs.error(request, f'Ошибка: неверные данные формы | {form.errors!r}')
            # Возвращаем юзера на страницу, откуда он пришёл, используя заголовок referer из его запроса
            return HttpResponseRedirect(request.META.get('HTTP_REFERER'))

