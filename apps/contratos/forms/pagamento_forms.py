from django import forms
from ..models.item_contrato import ItemContrato

class ItemContratoForm(forms.ModelForm):
    class Meta:
        model = ItemContrato
        fields = ['data_vencimento', 'valor_parcela', 'situacao']
        widgets = {
            'data_vencimento': forms.DateInput(attrs={'type': 'date'}),
        }
