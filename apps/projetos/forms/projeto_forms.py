# apps/projetos/forms/projeto_forms.py
from django import forms
from ..models.projeto import Projeto

class ProjetoForm(forms.ModelForm):
    # Sobrescrever o campo valor para aceitar formato brasileiro
    valor = forms.CharField(
        label='Valor Orçado (R$)',
        help_text='Use formato brasileiro: Ex: 25.000,00',
        widget=forms.TextInput(attrs={'placeholder': 'Ex: 25.000,00'})
    )
    
    # Campos extras para dados do cliente (não persistidos no modelo)
    cliente_nome = forms.CharField(
        max_length=200, 
        label='Nome do Cliente',
        required=False
    )
    cliente_email = forms.EmailField(
        label='Email do Cliente', 
        required=False
    )
    cliente_telefone = forms.CharField(
        max_length=20, 
        label='Telefone do Cliente',
        required=False
    )
    descricao_extra = forms.CharField(
        widget=forms.Textarea(attrs={'rows': 3}),
        label='Descrição do Projeto',
        required=False
    )
    
    class Meta:
        model = Projeto
        fields = [
            'cod_projeto',
            'nome',
            'data_inicio',
            'data_encerramento',
            'situacao',
        ]
        widgets = {
            'data_inicio': forms.DateInput(attrs={'type': 'date'}),
            'data_encerramento': forms.DateInput(attrs={'type': 'date'}),
        }
        labels = {
            'data_inicio': 'Data de Início',
            'data_encerramento': 'Data de Encerramento',
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Adiciona classes do Bootstrap aos campos
        for field_name, field in self.fields.items():
            if isinstance(field.widget, forms.Select):
                field.widget.attrs.update({'class': 'form-select'})
            elif not isinstance(field.widget, forms.CheckboxInput):
                field.widget.attrs.update({'class': 'form-control'})
                
        # Gerar próximo código de projeto automaticamente se for novo
        if not self.instance.pk:
            try:
                ultimo_projeto = Projeto.objects.order_by('-cod_projeto').first()
                proximo_codigo = (ultimo_projeto.cod_projeto + 1) if ultimo_projeto else 1
                self.fields['cod_projeto'].initial = proximo_codigo
            except:
                self.fields['cod_projeto'].initial = 1
    
    def clean_valor(self):
        """Converte valores em formato brasileiro para decimal"""
        valor = self.data.get('valor', '')  # Pega o valor bruto do form
        if isinstance(valor, str) and valor:
            # Remove espaços
            valor = valor.strip()
            # Se tem vírgula, assume formato brasileiro (ex: 1.234,56 ou 1234,56)
            if ',' in valor:
                # Remove pontos (separadores de milhares) e substitui vírgula por ponto
                valor_limpo = valor.replace('.', '').replace(',', '.')
            else:
                # Se não tem vírgula, assume formato americano (1234.56)
                valor_limpo = valor
            
            try:
                from decimal import Decimal
                return Decimal(valor_limpo)
            except:
                raise forms.ValidationError('Digite um valor válido (ex: 1234,56 ou 1234.56)')
        
        # Se chegou aqui, valor pode estar vazio ou None
        if not valor:
            raise forms.ValidationError('Este campo é obrigatório.')
        
        return valor
    
    def save(self, commit=True):
        """Salva o projeto com o valor convertido"""
        projeto = super().save(commit=False)
        
        # Definir o valor convertido no objeto
        if hasattr(self, 'cleaned_data') and 'valor' in self.cleaned_data:
            projeto.valor = self.cleaned_data['valor']
        
        if commit:
            projeto.save()
        return projeto