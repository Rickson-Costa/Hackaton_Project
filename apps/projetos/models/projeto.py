from django.db import models
from django.core.exceptions import ValidationError
from django.utils import timezone

class Projeto(models.Model):
    '''
    Modelo simplificado para Projetos.
    '''
    
    SITUACAO_CHOICES = [
        ('1', 'Aguardando Início'),
        ('2', 'Em andamento'),
        ('3', 'Paralisado'),
        ('4', 'Suspenso'),
        ('5', 'Cancelado'),
        ('6', 'Concluído'),
    ]
    
    cod_projeto = models.AutoField(
        primary_key=True,
        verbose_name='Código do Projeto'
    )
    nome = models.CharField(
        max_length=200,
        verbose_name='Nome do Projeto'
    )
    descricao = models.TextField(
        'Descrição',
        blank=True
    )
    data_inicio = models.DateField(
        verbose_name='Data de Início'
    )
    data_encerramento = models.DateField(
        verbose_name='Data de Encerramento'
    )
    valor = models.DecimalField(
        max_digits=14,
        decimal_places=2,
        verbose_name='Valor Orçado'
    )
    valor_realizado = models.DecimalField(
        'Valor Realizado',
        max_digits=14,
        decimal_places=2,
        default=0
    )
    custo_previsto = models.DecimalField(max_digits=12, decimal_places=2, default=0.00)
    custo_realizado = models.DecimalField(max_digits=12, decimal_places=2, default=0.00, editable=False)
    situacao = models.CharField(
        max_length=20,
        choices=SITUACAO_CHOICES,
        default='1',
        verbose_name='Situação'
    )
    responsavel = models.ForeignKey(
        'accounts.User',
        on_delete=models.PROTECT,
        related_name='projetos_responsavel',
        verbose_name='Responsável'
    )
    cliente_nome = models.CharField(
        'Nome do Cliente',
        max_length=200
    )
    cliente_email = models.EmailField(
        'Email do Cliente'
    )
    cliente_telefone = models.CharField(
        'Telefone do Cliente',
        max_length=20,
        blank=True
    )
    
    # Campos de auditoria básicos
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    created_by = models.ForeignKey(
        'accounts.User',
        on_delete=models.PROTECT,
        related_name='projetos_criados',
        null=True,
        blank=True
    )
    
    class Meta:
        verbose_name = 'Projeto'
        verbose_name_plural = 'Projetos'
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.cod_projeto} - {self.nome}"
    
    def clean(self):
        '''Validação básica'''
        super().clean()
        
        if self.data_encerramento and self.data_inicio:
            if self.data_encerramento < self.data_inicio:
                raise ValidationError('Data de encerramento deve ser maior que data de início.')