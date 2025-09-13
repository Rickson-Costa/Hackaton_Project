from django.db import models
from django.core.exceptions import ValidationError
from apps.core.models.base import AuditableModel, SituacaoMixin
from apps.core.models.mixins import ValorMixin, StatusMixin
from .projeto import Projeto
from .ordem import Ordem

class ItemOrdem(models.Model):
    '''
    Modelo alinhado com tabela itens_ordem
    '''
    
    SITUACAO_CHOICES = [
        ('1', 'Lançado'),
        ('2', 'Cancelado'),
        ('3', 'Entregue'),
    ]
    
    cod_ordem = models.ForeignKey(
        Ordem,
        on_delete=models.CASCADE,
        db_column='codOrdem',
        related_name='itens'
    )
    cod_item = models.IntegerField(
        verbose_name='Código do Item',
        db_column='codItem'
    )
    descricao = models.CharField(
        max_length=500,
        verbose_name='Descrição'
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
        verbose_name='Valor'
    )
    data_recebido = models.DateField(
        null=True,
        blank=True,
        db_column='dataRecebimento',
        verbose_name='Data de Recebimento'
    )
    situacao = models.CharField(
        max_length=20,
        choices=SITUACAO_CHOICES,
        verbose_name='Situação'
    )
    
    class Meta:
        db_table = 'itens_ordem'
        verbose_name = 'Item da Ordem'
        verbose_name_plural = 'Itens da Ordem'
        unique_together = [['cod_ordem', 'cod_item']]