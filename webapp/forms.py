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
