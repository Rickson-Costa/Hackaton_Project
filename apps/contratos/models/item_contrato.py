from django.db import models
from django.utils import timezone
from decimal import Decimal

class ItemContrato(models.Model):
    '''
    Modelo alinhado com tabela itens_contrato
    '''
    
    SITUACAO_CHOICES = [
        ('1', 'Lançado'),
        ('2', 'Cancelado'),
        ('3', 'Liquidado'),
    ]
    
    num_contrato = models.ForeignKey(
        Contrato,
        on_delete=models.CASCADE,
        db_column='numContrato',
        related_name='itens'
    )
    cod_lancamento = models.IntegerField(
        verbose_name='Código do Lançamento'
    )
    data_lancamento = models.DateField(
        verbose_name='Data de Lançamento'
    )
    num_parcela = models.IntegerField(
        verbose_name='Número da Parcela'
    )
    valor_parcela = models.DecimalField(
        max_digits=14,
        decimal_places=2,
        verbose_name='Valor da Parcela'
    )
    data_vencimento = models.DateField(
        verbose_name='Data de Vencimento'
    )
    valor_pago = models.DecimalField(
        max_digits=14,
        decimal_places=2,
        default=0,
        verbose_name='Valor Pago'
    )
    data_pagamento = models.DateField(
        null=True,
        blank=True,
        verbose_name='Data de Pagamento'
    )
    situacao = models.CharField(
        max_length=20,
        choices=SITUACAO_CHOICES,
        verbose_name='Situação'
    )
    
    class Meta:
        db_table = 'itens_contrato'
        verbose_name = 'Item do Contrato'
        verbose_name_plural = 'Itens do Contrato'
        unique_together = [['num_contrato', 'cod_lancamento']]