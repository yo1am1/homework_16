from django import forms


class ExchangeForm(forms.Form):
    amount = forms.FloatField(label="Amount", min_value=0.01)
