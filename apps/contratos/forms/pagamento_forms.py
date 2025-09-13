from django import forms
from apps.contratos.models.item_contrato import ItemContrato

class ItemContratoForm(forms.ModelForm):
    class Meta:
        model = ItemContrato
        fields = ['data_vencimento', 'valor_parcela', 'situacao']
        widgets = {
            'data_vencimento': forms.DateInput(attrs={'type': 'date'}),
        }
class RegistrarPagamentoForm(forms.Form):
         # Add your form fields here
         pass