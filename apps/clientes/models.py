from django.db import models
from apps.core.models.base import BaseModel

class Cliente(BaseModel):
    TIPO_PESSOA_CHOICES = (
        ('F', 'Física'),
        ('J', 'Jurídica'),
    )
    tipo_pessoa = models.CharField(max_length=1, choices=TIPO_PESSOA_CHOICES)
    nome = models.CharField(max_length=255, help_text="Nome completo para Pessoa Física.")
    razao_social = models.CharField(max_length=255, blank=True, null=True, help_text="Razão Social para Pessoa Jurídica.")
    cpf = models.CharField(max_length=14, unique=True, blank=True, null=True)
    cnpj = models.CharField(max_length=18, unique=True, blank=True, null=True)
    email = models.EmailField(unique=True)
    telefone = models.CharField(max_length=20, blank=True, null=True)
    # Adicionar campos de endereço se necessário

    def __str__(self):
        return self.nome if self.tipo_pessoa == 'F' else self.razao_social
