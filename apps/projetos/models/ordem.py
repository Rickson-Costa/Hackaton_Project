from django.db import models
from django.core.exceptions import ValidationError
from django.utils import timezone

class Ordem(models.Model):
    '''
    Modelo simplificado para Ordens de Serviço.
    '''
    
    SITUACAO_CHOICES = [
        ('1', 'Aguardando Início'),
        ('2', 'Em andamento'),
        ('3', 'Cancelada'),
        ('4', 'Concluída'),
    ]
    
    cod_ordem = models.IntegerField(
        primary_key=True,
        verbose_name='Código da Ordem',
        db_column='codOrdem'
    )
    cod_requisicao = models.ForeignKey(
        'projetos.Requisicao',
        on_delete=models.PROTECT,
        related_name='ordens',
        verbose_name='Requisição',
        db_column='codRequisicao'
    )
    descricao = models.CharField(
        max_length=500,
        verbose_name='Descrição da Ordem',
        db_column='descricao'
    )
    data_solicitacao = models.DateField(
        verbose_name='Data de Solicitação',
        db_column='dataSolicitacao'
    )
    data_limite = models.DateField(
        verbose_name='Data Limite',
        db_column='dataLimite'
    )
    valor = models.DecimalField(
        max_digits=14,
        decimal_places=2,
        verbose_name='Valor da Ordem',
        db_column='valor'
    )
    situacao = models.CharField(
        max_length=20,
        choices=SITUACAO_CHOICES,
        default='1',
        verbose_name='Situação',
        db_column='situacao'
    )
    executante = models.ForeignKey(
        'accounts.User',
        on_delete=models.PROTECT,
        related_name='ordens_executante',
        null=True,
        blank=True,
        verbose_name='Executante'
    )
    observacoes = models.TextField(
        'Observações',
        blank=True,
        null=True
    )
    
    # Campos de auditoria básicos
    created_at = models.DateTimeField(auto_now_add=True, null=True)
    updated_at = models.DateTimeField(auto_now=True, null=True)
    created_by = models.ForeignKey(
        'accounts.User',
        on_delete=models.PROTECT,
        related_name='ordens_criadas',
        null=True,
        blank=True
    )
    
    class Meta:
        db_table = 'ordem'
        verbose_name = 'Ordem de Serviço'
        verbose_name_plural = 'Ordens de Serviço'
        ordering = ['-data_solicitacao']
    
    def __str__(self):
        return f"OS-{self.cod_ordem}: {self.descricao[:50]}"
    
    def clean(self):
        '''Validação básica'''
        super().clean()
        
        if self.data_limite and self.data_solicitacao:
            if self.data_limite < self.data_solicitacao:
                raise ValidationError('Data limite deve ser maior que data de solicitação.')