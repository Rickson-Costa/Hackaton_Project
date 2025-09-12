from django.db import models
from django.utils import timezone
from decimal import Decimal

class ItemContrato(models.Model):
    '''
    Modelo simplificado para Itens do Contrato (Parcelas).
    '''
    
    SITUACAO_CHOICES = [
        ('1', 'Lançado'),
        ('2', 'Cancelado'),
        ('3', 'Liquidado'),
    ]
    
    num_contrato = models.ForeignKey(
        'contratos.Contrato',
        on_delete=models.CASCADE,
        related_name='itens',
        verbose_name='Contrato'
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
        verbose_name='Data de Pagamento',
        null=True,
        blank=True
    )
    situacao = models.CharField(
        max_length=20,
        choices=SITUACAO_CHOICES,
        default='1',
        verbose_name='Situação'
    )
    observacoes = models.TextField(
        'Observações',
        blank=True
    )
    
    # Campos de auditoria básicos
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = 'Item do Contrato'
        verbose_name_plural = 'Itens do Contrato'
        ordering = ['num_parcela']
        unique_together = [['num_contrato', 'cod_lancamento']]
    
    def __str__(self):
        return f"Parcela {self.num_parcela} - {self.num_contrato.num_contrato}"
    
    def get_valor_pendente(self):
        '''Calcular valor pendente de pagamento'''
        return max(Decimal('0'), self.valor_parcela - self.valor_pago)
    
    def is_vencida(self):
        '''Verificar se parcela está vencida'''
        if self.situacao == '3':  # Liquidada
            return False
        return timezone.now().date() > self.data_vencimento