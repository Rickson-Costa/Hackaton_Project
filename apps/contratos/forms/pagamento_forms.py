from django import forms
from ..models.item_contrato import ItemContrato

class ItemContratoForm(forms.ModelForm):
    class Meta:
        model = ItemContrato
        fields = ['data_vencimento', 'valor_parcela', 'situacao']
        widgets = {
            'data_vencimento': forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
            'valor_parcela': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01'}),
            'situacao': forms.Select(attrs={'class': 'form-control'}),
        }
        labels = {
            'data_vencimento': 'Data de Vencimento',
            'valor_parcela': 'Valor da Parcela (R$)',
            'situacao': 'Situação',
        }
