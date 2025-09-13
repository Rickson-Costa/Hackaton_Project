# apps/contratos/forms/contrato_forms.py
from django import forms
from django.core.exceptions import ValidationError
from crispy_forms.helper import FormHelper
from crispy_forms.layout import Layout, Field, Submit, Row, Column, HTML
from ..models.contrato import Contrato
from ..models.item_contrato import ItemContrato

class ContratoForm(forms.ModelForm):
    class Meta:
        model = Contrato
        fields = [
            'descricao', 
            'cpf_cnpj',
            'contratado', 
            'tipo_pessoa',
            'data_inicio', 
            'data_fim',
            'valor', 
            'parcelas', 
            'data_parcela_inicial',
            'situacao'
        ]
        widgets = {
            'data_inicio': forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
            'data_fim': forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
            'data_parcela_inicial': forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
            'tipo_pessoa': forms.Select(attrs={'class': 'form-select'}),
            'situacao': forms.Select(attrs={'class': 'form-select'}),
            'descricao': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'contratado': forms.TextInput(attrs={'class': 'form-control'}),
            'cpf_cnpj': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Apenas números'}),
            'valor': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01'}),
            'parcelas': forms.NumberInput(attrs={'class': 'form-control', 'min': '1'}),
        }
        labels = {
            'cpf_cnpj': 'CPF/CNPJ',
            'tipo_pessoa': 'Tipo de Pessoa',
            'data_inicio': 'Data de Início da Vigência',
            'data_fim': 'Data de Fim da Vigência',
            'data_parcela_inicial': 'Vencimento da 1ª Parcela',
            'descricao': 'Objeto do Contrato',
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        
        self.helper = FormHelper()
        self.helper.form_method = 'post'
        self.helper.form_class = 'contrato-form'
        
        self.helper.layout = Layout(
            HTML('<div class="row"><div class="col-12"><h5>Dados do Contrato</h5><hr></div></div>'),
            
            Field('descricao', css_class='mb-3'),
            
            Row(
                Column('contratado', css_class='form-group col-md-8'),
                Column('tipo_pessoa', css_class='form-group col-md-4'),
                css_class='form-row'
            ),
            
            Field('cpf_cnpj', css_class='mb-3'),
            
            HTML('<div class="row"><div class="col-12"><h5 class="mt-4">Vigência e Valores</h5><hr></div></div>'),
            
            Row(
                Column('data_inicio', css_class='form-group col-md-6'),
                Column('data_fim', css_class='form-group col-md-6'),
                css_class='form-row'
            ),
            
            Row(
                Column('valor', css_class='form-group col-md-4'),
                Column('parcelas', css_class='form-group col-md-4'),
                Column('situacao', css_class='form-group col-md-4'),
                css_class='form-row'
            ),
            
            Field('data_parcela_inicial', css_class='mb-3'),
            
            Submit('submit', 'Salvar Contrato', css_class='btn btn-success')
        )

    def clean_cpf_cnpj(self):
        """Validar e formatar CPF/CNPJ"""
        cpf_cnpj = self.cleaned_data.get('cpf_cnpj')
        if cpf_cnpj:
            # Remover formatação
            cpf_cnpj = ''.join(filter(str.isdigit, cpf_cnpj))
            
            # Validar tamanho
            if len(cpf_cnpj) not in [11, 14]:
                raise forms.ValidationError('CPF deve ter 11 dígitos ou CNPJ deve ter 14 dígitos.')
            
            return cpf_cnpj
        return cpf_cnpj

    def clean(self):
        """Validação customizada"""
        cleaned_data = super().clean()
        
        data_inicio = cleaned_data.get('data_inicio')
        data_fim = cleaned_data.get('data_fim')
        data_parcela_inicial = cleaned_data.get('data_parcela_inicial')
        
        if data_inicio and data_fim:
            if data_fim <= data_inicio:
                raise ValidationError('Data de fim deve ser posterior à data de início.')
        
        if data_inicio and data_parcela_inicial:
            if data_parcela_inicial < data_inicio:
                raise ValidationError('Data da primeira parcela deve ser posterior à data de início.')
        
        return cleaned_data


class ItemContratoForm(forms.ModelForm):
    class Meta:
        model = ItemContrato
        fields = ['data_vencimento', 'valor_parcela', 'situacao', 'observacoes']
        widgets = {
            'data_vencimento': forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
            'valor_parcela': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01'}),
            'situacao': forms.Select(attrs={'class': 'form-select'}),
            'observacoes': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        
        self.helper = FormHelper()
        self.helper.form_method = 'post'
        
        self.helper.layout = Layout(
            HTML('<h5>Nova Parcela</h5><hr>'),
            
            Row(
                Column('data_vencimento', css_class='form-group col-md-6'),
                Column('valor_parcela', css_class='form-group col-md-6'),
                css_class='form-row'
            ),
            
            Field('situacao', css_class='mb-3'),
            Field('observacoes', css_class='mb-3'),
            
            Submit('submit', 'Adicionar Parcela', css_class='btn btn-primary')
        )


class RegistrarPagamentoForm(forms.Form):
    """Formulário para registrar pagamento de parcela"""
    
    valor_pago = forms.DecimalField(
        max_digits=14,
        decimal_places=2,
        label='Valor Pago',
        widget=forms.NumberInput(attrs={
            'class': 'form-control',
            'step': '0.01',
            'placeholder': '0,00'
        })
    )
    
    data_pagamento = forms.DateField(
        label='Data do Pagamento',
        widget=forms.DateInput(attrs={
            'type': 'date',
            'class': 'form-control'
        }),
        initial=lambda: timezone.now().date()
    )
    
    observacoes = forms.CharField(
        label='Observações',
        required=False,
        widget=forms.Textarea(attrs={
            'class': 'form-control',
            'rows': 3,
            'placeholder': 'Informações adicionais sobre o pagamento'
        })
    )

    def __init__(self, parcela=None, *args, **kwargs):
        self.parcela = parcela
        super().__init__(*args, **kwargs)
        
        if parcela:
            # Preencher valor padrão com valor pendente
            valor_pendente = parcela.get_valor_pendente()
            self.fields['valor_pago'].initial = valor_pendente
            self.fields['valor_pago'].widget.attrs['max'] = str(valor_pendente)

    def clean_valor_pago(self):
        valor_pago = self.cleaned_data.get('valor_pago')
        
        if valor_pago <= 0:
            raise ValidationError('Valor pago deve ser maior que zero.')
        
        if self.parcela:
            valor_pendente = self.parcela.get_valor_pendente()
            if valor_pago > valor_pendente:
                raise ValidationError(f'Valor pago não pode ser maior que o valor pendente (R$ {valor_pendente}).')
        
        return valor_pago


class ContratoFilterForm(forms.Form):
    """Formulário para filtros da lista de contratos"""
    
    SITUACAO_CHOICES = [('', 'Todas')] + Contrato.SITUACAO_CHOICES
    TIPO_PESSOA_CHOICES = [('', 'Todos')] + Contrato.TIPO_PESSOA_CHOICES
    
    search = forms.CharField(
        label='Buscar',
        required=False,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Buscar por contrato, contratado ou CPF/CNPJ'
        })
    )
    
    situacao = forms.ChoiceField(
        label='Situação',
        choices=SITUACAO_CHOICES,
        required=False,
        widget=forms.Select(attrs={'class': 'form-select'})
    )
    
    tipo_pessoa = forms.ChoiceField(
        label='Tipo de Pessoa',
        choices=TIPO_PESSOA_CHOICES,
        required=False,
        widget=forms.Select(attrs={'class': 'form-select'})
    )
    
    data_inicio_de = forms.DateField(
        label='Data Início (De)',
        required=False,
        widget=forms.DateInput(attrs={'type': 'date', 'class': 'form-control'})
    )
    
    data_inicio_ate = forms.DateField(
        label='Data Início (Até)',
        required=False,
        widget=forms.DateInput(attrs={'type': 'date', 'class': 'form-control'})
    )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        
        self.helper = FormHelper()
        self.helper.form_method = 'get'
        self.helper.form_class = 'filter-form'
        
        self.helper.layout = Layout(
            Row(
                Column('search', css_class='form-group col-md-4'),
                Column('situacao', css_class='form-group col-md-2'),
                Column('tipo_pessoa', css_class='form-group col-md-2'),
                Column('data_inicio_de', css_class='form-group col-md-2'),
                Column('data_inicio_ate', css_class='form-group col-md-2'),
                css_class='form-row'
            ),
            Submit('submit', 'Filtrar', css_class='btn btn-primary btn-sm')
        )