# apps/projetos/forms/ordem_forms.py
from django import forms
from ..models.ordem import Ordem

class OrdemForm(forms.ModelForm):
    class Meta:
        model = Ordem
        fields = [
            'cod_ordem',
            'cod_requisicao',
            'descricao', 
            'data_solicitacao', 
            'data_limite', 
            'valor', 
            'situacao'
        ]
        widgets = {
            'data_solicitacao': forms.DateInput(attrs={'type': 'date'}),
            'data_limite': forms.DateInput(attrs={'type': 'date'}),
            'situacao': forms.Select(attrs={'class': 'form-select'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field_name, field in self.fields.items():
            if not isinstance(field.widget, forms.Select):
                field.widget.attrs.update({'class': 'form-control'})