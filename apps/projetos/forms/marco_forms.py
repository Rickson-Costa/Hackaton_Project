from django import forms
from ..models import MarcoProjeto

class MarcoProjetoForm(forms.ModelForm):
    class Meta:
        model = MarcoProjeto
        fields = ['descricao', 'data_prevista']
        widgets = {
            'data_prevista': forms.DateInput(attrs={'type': 'date'}),
        }
