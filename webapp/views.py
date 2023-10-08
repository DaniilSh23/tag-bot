from django.core.files.storage import FileSystemStorage
from django.http import HttpRequest, HttpResponse, HttpResponseRedirect
from django.shortcuts import render, redirect
from django.urls import reverse_lazy
from django.views import View
from django.contrib import messages as err_msgs

from tag_bot.settings import MY_LOGGER, BOT_TOKEN
from webapp.forms import BalanceForm, SecPayStepForm, CheckPaymentForm
from webapp.services.balance_services import BalanceServices


class BalanceView(View):
    """
    Вьюшки для страницы баланса.
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
                return HttpResponseRedirect(request.META.get('HTTP_REFERER'))
                # return HttpResponse(content=payload, status=status)
            return render(request, template_name='webapp/sec_pay_step.html', context=payload)

        else:
            MY_LOGGER.warning(f'Данные формы невалидны | {form.errors!r}')
            err_msgs.error(request, f'Ошибка: неверные данные формы | {form.errors!r}')
            # Возвращаем юзера на страницу, откуда он пришёл, используя заголовок referer из его запроса
            return HttpResponseRedirect(request.META.get('HTTP_REFERER'))


def sec_pay_step(request: HttpRequest) -> HttpResponse:
    """
    Вьюшка для обработки POST запроса второго шага оплаты.
    """
    MY_LOGGER.info(f'Пришёл запрос на вьюшку второго шага оплаты.')

    # Если запрос выполнен неверным методом
    if request.method != 'POST':
        MY_LOGGER.warning(f'Метод {request.method!r} не разрешён!')
        return HttpResponse(status=405, content='method not allowed')

    form = SecPayStepForm(request.POST, request.FILES)
    if form.is_valid():

        # Вызов сервиса
        status, payload = BalanceServices.update_bill_and_send_for_confirmation(
            bill_file=form.cleaned_data['bill_file'],
            bill_hash=form.cleaned_data['bill_hash'],
        )

        # Обработка если сервис не выполнил бизнес-логику
        if status != 200:
            status, get_bill_rslt = BalanceServices.get_bill(bill_hash=form.cleaned_data['bill_hash'])
            if status != 200:   # Обработка на случай если счет не найден в БД
                return HttpResponse(content=get_bill_rslt, status=status)
            err_msgs.error(request, message=payload)
            return render(request, template_name='webapp/sec_pay_step.html', context=get_bill_rslt)

        return render(request, template_name='webapp/success.html', context=payload)

    # Обработка невалидной формы
    else:
        MY_LOGGER.warning(f'Данные формы не валидны | запрос: {request.POST!r} | ошибки формы: {form.errors!r}')

        # Достаём инфу по счету для рендера страницы и рендерим с сообщением об ошибке
        status, get_bill_rslt = BalanceServices.get_bill(bill_hash=form.cleaned_data['bill_hash'])
        if status != 200:  # Обработка на случай если счет не найден в БД
            return HttpResponse(content=get_bill_rslt, status=status)

        err_msgs.error(request, f'Ошибка: неверные данные формы | {form.errors!r}')
        return render(request, template_name='webapp/sec_pay_step.html', context=get_bill_rslt)


class CheckPayment(View):
    """
    Вьюшки для запросов проверки платежей.
    """
    def get(self, request):
        MY_LOGGER.info(f'Пришёл GET запрос на вьюшку CheckPayment')

        # Обработка невалидного токена в запросе
        if request.GET.get('token') != BOT_TOKEN:
            MY_LOGGER.warning(f'Неверный токен в запросе ! | {request.GET.get("token")!r} != {BOT_TOKEN!r}')
            return HttpResponse(content='invalid token!', status=400)

        # Обработка отсутствия
        if not request.GET.get('tg_msg_id'):
            MY_LOGGER.warning(f'В запросе отсутствует TG ID сообщения!')
            return HttpResponse(content='Message id is empty!', status=400)

        # Обработка невалидного bill_hash
        bill_hash = request.GET.get("bill_hash")
        if not bill_hash:
            MY_LOGGER.warning(f'Отсутствует или невалидный параметр запроса bill_hash, '
                              f'его значение: {request.GET.get("bill_hash")}')
            return HttpResponse(content='invalid request params!', status=400)

        # вызов сервиса для бизнес-логики
        status, get_bill_rslt = BalanceServices.get_bill(bill_hash=request.GET.get("bill_hash"))
        if status != 200:  # Обработка на случай если счет не найден в БД
            return HttpResponse(content=get_bill_rslt, status=status)
        get_bill_rslt['tg_msg_id'] = request.GET.get('tg_msg_id')
        return render(request, template_name='webapp/check_payment.html', context=get_bill_rslt)

    def post(self, request):
        MY_LOGGER.info(f"Получен POST запрос на вьюшку CheckPayment | {request.POST}")

        form = CheckPaymentForm(request.POST)
        if form.is_valid():

            # Вызов сервиса для выполнения бзнес-логики
            status, payload = BalanceServices.confirm_or_decline_payment(
                bill_hash=form.cleaned_data.get("bill_hash"),
                bill_comment=form.cleaned_data.get("bill_comment"),
                tg_msg_id=form.cleaned_data.get("tg_msg_id"),
                accept_pay_flag=form.cleaned_data.get("accept_pay_flag"),
            )
            if status != 200:
                return HttpResponse(content=payload, status=status)
            return render(request, template_name='webapp/success.html', context=payload)

        # Если форма невалидна
        MY_LOGGER.warning(f'Данные формы невалидны: {form.errors!r}')
        status, get_bill_rslt = BalanceServices.get_bill(bill_hash=request.GET.get("bill_hash"))
        if status != 200:  # Обработка на случай если счет не найден в БД
            return HttpResponse(content=get_bill_rslt, status=status)
        get_bill_rslt['tg_msg_id'] = request.GET.get('tg_msg_id')
        err_msgs.error(request, f'Ошибка: неверные данные формы | {form.errors!r}')
        return render(request, template_name='webapp/check_payment.html', context=get_bill_rslt)

