from django.http import HttpRequest, HttpResponse, HttpResponseRedirect
from django.shortcuts import render, redirect
from django.urls import reverse_lazy, reverse
from django.views import View
from django.contrib import messages as err_msgs
from django.views.generic import DeleteView

from tag_bot.settings import MY_LOGGER, BOT_TOKEN
from webapp.forms import BalanceForm, SecPayStepForm, CheckPaymentForm, MultiplyFileForm, GroupChatForm
from webapp.services.balance_services import BalanceServices
from webapp.services.common_services import FAQandSupportService
from webapp.services.groups_services import GroupsService


class SupportView(View):
    """
    Вьюшка для страницы поддержки и FAQ
    """
    def get(self, request):
        MY_LOGGER.info(f'Получен GET запрос на вьюшку поддержки и FAQ')

        # Достаём контекст для поддержки
        support_context = FAQandSupportService.make_support_context()
        if not support_context:
            MY_LOGGER.warning('Не определены данные для контекста поддержки')
            return HttpResponse(content='Не определены данные для контекста поддержки', status=400)

        # Достаём контекст для FAQ
        faq_context = FAQandSupportService.make_faq_context()
        if not faq_context:
            MY_LOGGER.warning('Не определены данные для контекста FAQ')
            return HttpResponse(content='Не определены данные для контекста FAQ', status=400)

        # Достаем контекст для раздела отзывов
        reviews_context = FAQandSupportService.make_reviews_context()
        if not faq_context:
            MY_LOGGER.warning('Не определены данные для контекста FAQ')
            return HttpResponse(content='Не определены данные для контекста FAQ', status=400)

        return render(request, template_name='webapp/support_faq.html',
                      context=support_context | faq_context | reviews_context)


class TagAllView(View):
    """
    Вьюшка для функции тегнуть всех
    """
    def get(self, request, tlg_id, group_id):
        MY_LOGGER.info(f'Пришел GET запрос на вьюшку для тега всех | tlg_id={tlg_id}, group_id={group_id}')

        context = dict(tlg_id=tlg_id)
        # Вызов сервиса для бизнес-логики
        msg_type, msg = GroupsService.tag_all(group_id=group_id)
        context[msg_type] = msg

        # Вызов сервиса для получения детальной инфы о групповом чате
        status, payload = GroupsService.show_group_detail(group_id=group_id, tlg_id=tlg_id)
        if status != 200:
            return HttpResponse(content=payload, status=status)

        # Объединяем два словаря и рендерим страницу с деталями о групповом чате
        context = context | payload
        return render(request, template_name='webapp/groups_detail.html', context=context)


class GroupDetailView(View):
    """
    Вьюшки для работы с каждой группой детально.
    """

    def get(self, request, tlg_id, group_id):
        MY_LOGGER.info(f'Пришёл GET запрос на вьюшку детальной инфы о группе с PK={group_id}')

        # Проверяем данные запроса
        if not isinstance(tlg_id, int) or not isinstance(group_id, int):
            MY_LOGGER.warning(f'Данные запроса не валидны, tlg_id & group_id должны быть int. Запрос: {request.GET}')
            return HttpResponse(status=400, content='invalid request data!')

        # Вызываем сервис для выполнения бизнес-логики
        status, payload = GroupsService.show_group_detail(tlg_id=str(tlg_id), group_id=group_id)
        if status != 200:
            return HttpResponse(content=payload, status=status)
        payload['tlg_id'] = tlg_id
        return render(request, template_name='webapp/groups_detail.html', context=payload)

    def post(self, request, tlg_id, group_id):
        MY_LOGGER.info(f'POST запрос на вьюшку GroupDetailView для обновления данных о групповом чате {group_id!r}')

        # Проверяем данные запроса
        if not isinstance(tlg_id, int) or not isinstance(group_id, int):
            MY_LOGGER.warning(f'Данные запроса не валидны, tlg_id & group_id должны быть int. Запрос: {request.GET}')
            return HttpResponse(status=400, content='invalid request data!')

        form = GroupChatForm(request.POST)
        file_form = MultiplyFileForm(request.FILES)
        if form.is_valid() and file_form.is_valid():

            # Вызываем сервис для бизнес-логики
            status, payload = GroupsService.update_group_chat(
                tlg_id=str(tlg_id),
                group_id=group_id,
                delete_files_pk=request.POST.getlist("delete_files"),
                group_name=form.cleaned_data.get("group_name"),
                tag_now=form.cleaned_data.get("tag_now"),
                msg_text=form.cleaned_data.get("msg_text"),
                new_group_chat_files=request.FILES.getlist("group_chat_files"),
            )
            if status != 200:
                return HttpResponse(content=payload, status=status)
            payload['tlg_id'] = tlg_id
            return render(request, template_name='webapp/groups_detail.html', context=payload)
        else:
            MY_LOGGER.warning(f'Данные форм невалидны. Ошибки form: {form.errors!r} | '
                              f'Ошибки file_form: {file_form.errors!r} | {request.POST} | {request.FILES}')
            err_msgs.error(request, f'Ошибка: неверные данные формы | {form.errors!r} | {file_form.errors!r}')
            return redirect(to=reverse('webapp:group_detail', kwargs={'tlg_id': tlg_id, 'group_id': group_id}))


class GroupsView(View):
    """
    Вьюшки для списка групповых чатов
    """

    def get(self, request):
        MY_LOGGER.info(f'GET запрос на вьюшку списка групповых чатов.')

        # Обработка невалидного токена в запросе
        # TODO: убрал из-за сложностей навигации с других страниц. Максимум что сможет свинтус - посмотреть
        #  чьи-то группы.
        # if request.GET.get('token') != BOT_TOKEN:
        #     MY_LOGGER.warning(f'Неверный токен в запросе ! | {request.GET.get("token")!r} != {BOT_TOKEN!r}')
        #     return HttpResponse(content='invalid token!', status=400)

        # Обработка невалидного tlg_id
        tlg_id = request.GET.get("tlg_id")
        if not tlg_id or not tlg_id.isdigit():
            MY_LOGGER.warning(f'Отсутствует или невалидный параметр запроса tlg_id, '
                              f'его значение: {request.GET.get("tlg_id")}')
            return HttpResponse(content='invalid request params!', status=400)

        status, payload = GroupsService.show_groups_lst(tlg_id=tlg_id)
        if status != 200:
            return HttpResponse(content=payload, status=status)
        payload['tlg_id'] = tlg_id
        return render(request, template_name='webapp/groups_list.html', context=payload)

    def post(self, request):
        MY_LOGGER.info(f'POST запрос на вьюшку GroupsView для создания нового группового чата.')

        form = GroupChatForm(request.POST)
        file_form = MultiplyFileForm(request.FILES)
        if form.is_valid() and file_form.is_valid():

            # Вызываем сервис для бизнес-логики
            status, payload = GroupsService.create_group_chat(
                tlg_id=request.POST.get("tlg_id"),
                group_name=form.cleaned_data.get("group_name"),
                group_tg_id=form.cleaned_data.get("group_tg_id"),
                tag_now=form.cleaned_data.get("tag_now"),
                msg_text=form.cleaned_data.get("msg_text"),
                new_group_chat_files=request.FILES.getlist("group_chat_files"),
            )
            if status != 200:
                return HttpResponse(content=payload, status=status)
            payload['tlg_id'] = request.POST.get("tlg_id")
            return render(request, template_name='webapp/groups_detail.html', context=payload)
        else:
            MY_LOGGER.warning(f'Данные форм невалидны. Ошибки form: {form.errors!r} | '
                              f'Ошибки file_form: {file_form.errors!r} | {request.POST} | {request.FILES}')
            err_msgs.error(request, f'Ошибка: неверные данные формы | {form.errors!r} | {file_form.errors!r}')
            return redirect(to=f"{reverse('webapp:groups')}?tlg_id={request.POST.get('tlg_id')}")


class GroupChatDeleteView(View):
    """
    Вьюшка для удаления записи о групповом чате
    """
    def get(self, request, tlg_id, group_id):
        """
        Обработка GET запроса для удаления группового чата.
        """
        MY_LOGGER.info(f'Пришёл GET запрос на вьюшку удаления группового чата')

        # Вызов сервиса для удаления
        status, payload = GroupsService.delete_group_chat(tlg_id=str(tlg_id), group_id=group_id)
        if status != 200:
            return HttpResponse(content=payload, status=status)

        return redirect(to=f"{reverse('webapp:groups')}?tlg_id={tlg_id}")


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
            if status != 200:  # Обработка на случай если счет не найден в БД
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
