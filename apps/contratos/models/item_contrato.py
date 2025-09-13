# apps/contratos/models/item_contrato.py
from django.db import models
from django.utils import timezone
from decimal import Decimal

class ItemContrato(models.Model):
    '''
    Modelo alinhado com tabela itens_contrato
    '''
    
    SITUACAO_CHOICES = [
        ('1', 'Pendente'),
        ('2', 'Cancelado'),
        ('3', 'Paga'),
        ('4', 'Parcialmente Paga'),
    ]
    
    num_contrato = models.ForeignKey(
        'contratos.Contrato',
        on_delete=models.CASCADE,
        db_column='numContrato',
        related_name='itens',
        verbose_name='Contrato'
    )
    cod_lancamento = models.IntegerField(
        db_column='codLancamento',
        verbose_name='Código do Lançamento'
    )
    data_lancamento = models.DateField(
        db_column='dataLancamento',
        verbose_name='Data de Lançamento'
    )
    num_parcela = models.IntegerField(
        db_column='numParcela',
        verbose_name='Número da Parcela'
    )
    valor_parcela = models.DecimalField(
        max_digits=14,
        decimal_places=2,
        db_column='valorParcela',
        verbose_name='Valor da Parcela'
    )
    data_vencimento = models.DateField(
        db_column='dataVencimento',
        verbose_name='Data de Vencimento'
    )
    valor_pago = models.DecimalField(
        max_digits=14,
        decimal_places=2,
        default=0,
        db_column='valorPago',
        verbose_name='Valor Pago'
    )
    data_pagamento = models.DateField(
        null=True,
        blank=True,
        db_column='dataPagamento',
        verbose_name='Data de Pagamento'
    )
    situacao = models.CharField(
        max_length=20,
        choices=SITUACAO_CHOICES,
        default='1',
        db_column='situacao',
        verbose_name='Situação'
    )
    observacoes = models.TextField(
        blank=True,
        db_column='observacoes',
        verbose_name='Observações'
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def get_valor_pendente(self):
        """Retorna valor pendente da parcela"""
        return self.valor_parcela - self.valor_pago

    def get_valor_total(self):
        """Retorna valor total da parcela"""
        return self.valor_parcela

    def is_vencida(self):
        """Verifica se a parcela está vencida"""
        if self.situacao == '1':  # Pendente
            return self.data_vencimento < timezone.now().date()
        return False

    def get_dias_atraso(self):
        """Retorna quantidade de dias em atraso"""
        if self.is_vencida():
            return (timezone.now().date() - self.data_vencimento).days
        return 0

    def pode_receber_pagamento(self):
        """Verifica se pode receber pagamento"""
        return self.situacao in ['1', '4']  # Pendente ou Parcialmente Paga

    def __str__(self):
        return f"Parcela {self.num_parcela} - {self.num_contrato.num_contrato}"

    class Meta:
        db_table = 'itens_contrato'
        verbose_name = 'Item do Contrato'
        verbose_name_plural = 'Itens do Contrato'
        ordering = ['num_parcela']
        unique_together = [['num_contrato', 'cod_lancamento']]