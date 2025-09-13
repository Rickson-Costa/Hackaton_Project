import os
from django.db import models
from django.conf import settings
from .contrato import Contrato

def upload_documento_contrato(instance, filename):
    """Caminho para upload de documentos do contrato"""
    return f'contratos/{instance.contrato.num_contrato}/documentos/{filename}'

class DocumentoContrato(models.Model):
    TIPO_CHOICES = [
        ('contrato', 'Contrato Assinado'),
        ('proposta', 'Proposta Comercial'),
        ('orcamento', 'Orçamento'),
        ('recibo', 'Recibo de Pagamento'),
        ('nota_fiscal', 'Nota Fiscal'),
        ('outros', 'Outros'),
    ]
    
    contrato = models.ForeignKey(
        Contrato,
        on_delete=models.CASCADE,
        related_name='documentos'
    )
    nome = models.CharField(max_length=255)
    tipo = models.CharField(max_length=20, choices=TIPO_CHOICES, default='outros')
    arquivo = models.FileField(upload_to=upload_documento_contrato)
    descricao = models.TextField(blank=True)
    
    criado_em = models.DateTimeField(auto_now_add=True)
    criado_por = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.PROTECT,
        related_name='documentos_criados'
    )
    
    class Meta:
        ordering = ['-criado_em']
        verbose_name = 'Documento do Contrato'
        verbose_name_plural = 'Documentos do Contrato'
    
    def __str__(self):
        return f"{self.nome} - {self.contrato.num_contrato}"
    
    def get_file_size(self):
        """Retorna tamanho do arquivo formatado"""
        if self.arquivo:
            size = self.arquivo.size
            for unit in ['B', 'KB', 'MB', 'GB']:
                if size < 1024.0:
                    return f"{size:.1f} {unit}"
                size /= 1024.0
        return "0 B"
    
    def get_file_extension(self):
        """Retorna extensão do arquivo"""
        if self.arquivo:
            return os.path.splitext(self.arquivo.name)[1].lower()
        return ""