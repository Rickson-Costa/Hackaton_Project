from django.db import models
from django.core.exceptions import ValidationError
from django.utils import timezone

class Ordem(models.Model):
    '''
    Modelo alinhado com tabela ordem
    '''
    
    SITUACAO_CHOICES = [
        ('1', 'Aguardando Início'),
        ('2', 'Em andamento'),
        ('3', 'Cancelada'),
        ('4', 'Concluída'),
    ]
    
    cod_ordem = models.IntegerField(
        primary_key=True,
        verbose_name='Código da Ordem'
    )
    cod_requisicao = models.ForeignKey(
        Requisicao,
        on_delete=models.RESTRICT,
        db_column='codRequisicao',
        related_name='ordens',
        verbose_name='Requisição'
    )
    descricao = models.CharField(
        max_length=500,
        verbose_name='Descrição'
    )
    data_solicitacao = models.DateField(
        verbose_name='Data de Solicitação'
    )
    data_limite = models.DateField(
        verbose_name='Data Limite'
    )
    valor = models.DecimalField(
        max_digits=14,
        decimal_places=2,
        verbose_name='Valor'
    )
    situacao = models.CharField(
        max_length=20,
        choices=SITUACAO_CHOICES,
        verbose_name='Situação'
    )
    
    class Meta:
        db_table = 'ordem'
        verbose_name = 'Ordem de Serviço'
        verbose_name_plural = 'Ordens de Serviço'