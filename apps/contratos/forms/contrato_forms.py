from django import forms
from ..models.contrato import Contrato
from ..models.prestador import Prestador

class ContratoForm(forms.ModelForm):
    class Meta:
        model = Contrato
        fields = [
            'num_contrato', 'cod_ordem', 'descricao', 'cpf_cnpj', 'contratado', 'tipo_pessoa',
            'data_inicio', 'data_fim', 'valor', 'parcelas',
            'data_parcela_inicial', 'situacao'
        ]
        widgets = {
            'data_inicio': forms.DateInput(attrs={'type': 'date'}),
            'data_fim': forms.DateInput(attrs={'type': 'date'}),
            'data_parcela_inicial': forms.DateInput(attrs={'type': 'date'}),
            'tipo_pessoa': forms.Select(attrs={'class': 'form-select'}),
            'situacao': forms.Select(attrs={'class': 'form-select'}),
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        
        # Aplicar classe form-control para todos os campos não-select
        for field_name, field in self.fields.items():
            if not isinstance(field.widget, forms.Select):
                field.widget.attrs.update({'class': 'form-control'})


class PrestadorForm(forms.ModelForm):
    """Formulário para cadastro de Prestadores - RF-02, RF-21"""
    
    class Meta:
        model = Prestador
        fields = [
            'tipo_pessoa', 'nome', 'nome_fantasia', 'cpf', 'cnpj', 'rg',
            'inscricao_estadual', 'inscricao_municipal', 'email', 'telefone',
            'cep', 'logradouro', 'numero', 'complemento', 'bairro', 'cidade', 'uf',
            'banco', 'agencia', 'conta', 'tipo_conta', 'ativo', 'observacoes'
        ]
        widgets = {
            'tipo_pessoa': forms.Select(attrs={'class': 'form-select'}),
            'observacoes': forms.Textarea(attrs={'rows': 3}),
            'ativo': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        
        # Aplicar classes Bootstrap
        for field_name, field in self.fields.items():
            if isinstance(field.widget, forms.CheckboxInput):
                continue
            elif isinstance(field.widget, forms.Select):
                field.widget.attrs.update({'class': 'form-select'})
            else:
                field.widget.attrs.update({'class': 'form-control'})
        
        # Configurações específicas para campos
        self.fields['cpf'].widget.attrs.update({'maxlength': '14'})
        self.fields['cnpj'].widget.attrs.update({'maxlength': '18'})
        self.fields['cep'].widget.attrs.update({'maxlength': '10'})
    
    def clean(self):
        cleaned_data = super().clean()
        tipo_pessoa = cleaned_data.get('tipo_pessoa')
        cpf = cleaned_data.get('cpf')
        cnpj = cleaned_data.get('cnpj')
        
        # Validações específicas para PF/PJ
        if tipo_pessoa == 'PF':
            if not cpf:
                raise forms.ValidationError({'cpf': 'CPF é obrigatório para Pessoa Física'})
            if cnpj:
                raise forms.ValidationError({'cnpj': 'CNPJ não deve ser preenchido para Pessoa Física'})
        elif tipo_pessoa == 'PJ':
            if not cnpj:
                raise forms.ValidationError({'cnpj': 'CNPJ é obrigatório para Pessoa Jurídica'})
            if cpf:
                raise forms.ValidationError({'cpf': 'CPF não deve ser preenchido para Pessoa Jurídica'})
        
        return cleaned_data