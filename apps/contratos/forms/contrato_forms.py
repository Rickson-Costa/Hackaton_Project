from django import forms
from ..models.contrato import Contrato

class ContratoForm(forms.ModelForm):
    class Meta:
        model = Contrato
        fields = [
            'descricao', 
            'cpf_cnpj',  # Corrigido
            'contratado', 
            'tipo_pessoa',  # Corrigido
            'data_inicio', 
            'data_fim',  # Corrigido
            'valor', 
            'parcelas', 
            'data_parcela_inicial',  # Corrigido
            'situacao'
        ]
        widgets = {
            'data_inicio': forms.DateInput(attrs={'type': 'date'}),
            'data_fim': forms.DateInput(attrs={'type': 'date'}),
            'data_parcela_inicial': forms.DateInput(attrs={'type': 'date'}),
            'tipo_pessoa': forms.Select(attrs={'class': 'form-select'}),
            'situacao': forms.Select(attrs={'class': 'form-select'}),
        }
        labels = {
            'cpf_cnpj': 'CPF/CNPJ',
            'tipo_pessoa': 'Tipo de Pessoa',
            'data_inicio': 'Data de Início da Vigência',
            'data_fim': 'Data de Fim da Vigência',
            'data_parcela_inicial': 'Vencimento da 1ª Parcela',
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field_name, field in self.fields.items():
            if not isinstance(field.widget, forms.Select):
                field.widget.attrs.update({'class': 'form-control'})