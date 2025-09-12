from django import forms
from ..models.item_contrato import ItemContrato

class PagamentoForm(forms.Form):
    valor_pago = forms.DecimalField(
        label="Valor a Pagar", 
        max_digits=14, 
        decimal_places=2,
        widget=forms.NumberInput(attrs={'class': 'form-control'})
    )
    data_pagamento = forms.DateField(
        label="Data do Pagamento",
        widget=forms.DateInput(attrs={'type': 'date', 'class': 'form-control'})
    )
    metodo_pagamento = forms.ChoiceField(
        label="Método de Pagamento",
        choices=[
            ('dinheiro', 'Dinheiro'),
            ('transferencia', 'Transferência'),
            ('pix', 'PIX'),
            ('cartao_credito', 'Cartão de Crédito'),
            ('cartao_debito', 'Cartão de Débito'),
            ('boleto', 'Boleto'),
        ],
        widget=forms.Select(attrs={'class': 'form-select'})
    )
    observacoes = forms.CharField(
        label="Observações",
        required=False,
        widget=forms.Textarea(attrs={'rows': 3, 'class': 'form-control'})
    )