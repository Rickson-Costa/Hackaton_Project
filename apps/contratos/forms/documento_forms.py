from django import forms
from ..models.documento import DocumentoContrato

class DocumentoContratoForm(forms.ModelForm):
    class Meta:
        model = DocumentoContrato
        fields = ['nome', 'tipo', 'arquivo', 'descricao']
        widgets = {
            'nome': forms.TextInput(attrs={'class': 'form-control'}),
            'tipo': forms.Select(attrs={'class': 'form-select'}),
            'arquivo': forms.FileInput(attrs={'class': 'form-control', 'accept': '.pdf,.doc,.docx,.jpg,.png'}),
            'descricao': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['nome'].help_text = 'Nome descritivo para o documento'
        self.fields['arquivo'].help_text = 'Formatos aceitos: PDF, DOC, DOCX, JPG, PNG (max 10MB)'