from django import forms
from django.utils import timezone
from apps.projetos.models import Projeto
from apps.contratos.models import Contrato


class RelatorioCustomForm(forms.Form):
    """Formulário para relatórios customizados com filtros"""
    
    # Tipo de relatório
    TIPO_CHOICES = [
        ('projetos', 'Projetos'),
        ('contratos', 'Contratos'),
        ('financeiro', 'Financeiro'),
        ('mixto', 'Misto (Projetos + Contratos)'),
    ]
    
    tipo_relatorio = forms.ChoiceField(
        choices=TIPO_CHOICES,
        widget=forms.Select(attrs={'class': 'form-select'}),
        label='Tipo de Relatório'
    )
    
    # Filtros de data
    data_inicio = forms.DateField(
        required=False,
        widget=forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
        label='Data Início (a partir de)'
    )
    
    data_fim = forms.DateField(
        required=False,
        widget=forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
        label='Data Fim (até)'
    )
    
    # Filtros de valor
    valor_minimo = forms.DecimalField(
        required=False,
        max_digits=12,
        decimal_places=2,
        widget=forms.NumberInput(attrs={'class': 'form-control', 'placeholder': '0.00'}),
        label='Valor Mínimo (R$)'
    )
    
    valor_maximo = forms.DecimalField(
        required=False,
        max_digits=12,
        decimal_places=2,
        widget=forms.NumberInput(attrs={'class': 'form-control', 'placeholder': '999999.00'}),
        label='Valor Máximo (R$)'
    )
    
    # Filtros de situação
    SITUACAO_CHOICES = [
        ('', 'Todas as situações'),
        ('1', 'Aguardando Início'),
        ('2', 'Em Andamento'),
        ('3', 'Paralisado'),
        ('4', 'Suspenso'),
        ('5', 'Cancelado'),
        ('6', 'Concluído'),
    ]
    
    situacao = forms.ChoiceField(
        choices=SITUACAO_CHOICES,
        required=False,
        widget=forms.Select(attrs={'class': 'form-select'}),
        label='Situação'
    )
    
    # Filtros específicos para contratos
    TIPO_PESSOA_CHOICES = [
        ('', 'Todos os tipos'),
        ('1', 'Pessoa Física'),
        ('2', 'Pessoa Jurídica'),
    ]
    
    tipo_pessoa = forms.ChoiceField(
        choices=TIPO_PESSOA_CHOICES,
        required=False,
        widget=forms.Select(attrs={'class': 'form-select'}),
        label='Tipo de Pessoa (Contratos)'
    )
    
    # Filtros de texto
    nome_projeto = forms.CharField(
        required=False,
        max_length=100,
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Buscar por nome do projeto'}),
        label='Nome do Projeto (contém)'
    )
    
    contratado = forms.CharField(
        required=False,
        max_length=100,
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Buscar por nome do contratado'}),
        label='Nome do Contratado (contém)'
    )
    
    # Opções de visualização
    incluir_totais = forms.BooleanField(
        required=False,
        initial=True,
        widget=forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        label='Incluir totalizadores'
    )
    
    incluir_graficos = forms.BooleanField(
        required=False,
        initial=False,
        widget=forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        label='Incluir gráficos (apenas visualização)'
    )
    
    ordenacao = forms.ChoiceField(
        choices=[
            ('nome', 'Nome/Contratado'),
            ('valor', 'Valor'),
            ('data_inicio', 'Data de Início'),
            ('data_fim', 'Data de Fim'),
            ('situacao', 'Situação'),
        ],
        initial='nome',
        required=False,
        widget=forms.Select(attrs={'class': 'form-select'}),
        label='Ordenar por'
    )
    
    ordem_desc = forms.BooleanField(
        required=False,
        widget=forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        label='Ordem decrescente'
    )

    def clean(self):
        cleaned_data = super().clean()
        data_inicio = cleaned_data.get('data_inicio')
        data_fim = cleaned_data.get('data_fim')
        valor_minimo = cleaned_data.get('valor_minimo')
        valor_maximo = cleaned_data.get('valor_maximo')
        
        # Validar datas
        if data_inicio and data_fim and data_inicio > data_fim:
            raise forms.ValidationError('A data de início deve ser anterior à data de fim.')
        
        # Validar valores
        if valor_minimo and valor_maximo and valor_minimo > valor_maximo:
            raise forms.ValidationError('O valor mínimo deve ser menor que o valor máximo.')
        
        # Validar data não futura para início
        if data_inicio and data_inicio > timezone.now().date():
            raise forms.ValidationError('A data de início não pode ser no futuro.')
        
        return cleaned_data