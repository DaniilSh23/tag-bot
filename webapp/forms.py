from django import forms


class BalanceForm(forms.Form):
    """
    Форма для первого шага пополнения баланса. Приходи способ оплаты, сумма и tlg_id юзера.
    """
    tlg_id = forms.CharField()
    amount = forms.DecimalField()
    pay_method = forms.CharField()


class SecPayStepForm(forms.Form):
    """
    Форма для второго шага оплаты.
    """
    bill_file = forms.FileField()
    bill_hash = forms.CharField()

    class Meta:
        enctype = 'multipart/form-data'


class CheckPaymentForm(forms.Form):
    """
    Форма для подтверждения или отклонения платежа.
    """
    bill_hash = forms.CharField()
    bill_comment = forms.CharField(required=False)
    tg_msg_id = forms.IntegerField()
    accept_pay_flag = forms.IntegerField(min_value=0, max_value=1)


class GroupChatForm(forms.Form):
    """
    Форма для групповых чатов
    """
    group_name = forms.CharField(max_length=100)
    group_link = forms.URLField()
    tag_now = forms.BooleanField(
        required=False,
        widget=forms.CheckboxInput(
            attrs={
                'type': 'checkbox',
            }
        )
    )
    msg_text = forms.CharField()
    delete_files = forms.CharField(required=False)


""" В Django нашли уязвимость, связанную с multiple значением в ClearableFileInput, поэтому встречаем хуйню ниже """


class MultipleFileInput(forms.ClearableFileInput):
    allow_multiple_selected = True


class MultipleFileField(forms.FileField):
    def __init__(self, *args, **kwargs):
        kwargs.setdefault("widget", MultipleFileInput())
        super().__init__(*args, **kwargs)

    def clean(self, data, initial=None):
        single_file_clean = super().clean
        if isinstance(data, (list, tuple)):
            result = [single_file_clean(d, initial) for d in data]
        else:
            result = single_file_clean(data, initial)
        return result


class FileFieldForm(forms.Form):
    file_field = MultipleFileField()


class MultiplyFileForm(forms.Form):
    """
    Форма для загрузки нескольких файлов.
    """
    group_chat_files = MultipleFileField(required=False)