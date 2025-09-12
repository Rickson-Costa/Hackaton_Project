from django import forms
from ..models import LancamentoCusto

class LancamentoCustoForm(forms.ModelForm):
    class Meta:
        model = LancamentoCusto
        fields = ['descricao', 'valor', 'data']
        widgets = {
            'data': forms.DateInput(attrs={'type': 'date'}),
        }
