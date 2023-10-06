from django import forms


class BalanceForm(forms.Form):
    """
    Форма для первого шага пополнения баланса. Приходи способ оплаты, сумма и tlg_id юзера.
    """
    tlg_id = forms.CharField()
    amount = forms.DecimalField()
    pay_method = forms.CharField()
