# apps/projetos/forms/projeto_forms.py
# Código corrigido

from django import forms
from ..models.projeto import Projeto # Corrigindo a importação relativa

class ProjetoForm(forms.ModelForm):
    class Meta:
        model = Projeto
        fields = [
            'nome',
            'data_inicio',
            'data_encerramento',
            'valor',
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
        for field_name, field in self.fields.items():
            if not isinstance(field.widget, (forms.CheckboxInput, forms.Select)):
                field.widget.attrs.update({'class': 'form-control'})