from django.db import models
from django.core.exceptions import ValidationError

class Requisicao(models.Model):
    '''
    Modelo alinhado com tabela requisicao
    '''
    from .projeto import Projeto
    
    SITUACAO_CHOICES = [
        ('1', 'Aguardando Início'),
        ('2', 'Em andamento'),
        ('3', 'Suspensa'),
        ('4', 'Cancelada'),
        ('5', 'Concluída'),
    ]
    
    cod_requisicao = models.IntegerField(
        primary_key=True,
        db_column='codRequisicao',
        verbose_name='Código da Requisição'
    )
    cod_projeto = models.ForeignKey(
        'projetos.Projeto',
        on_delete=models.PROTECT,
        db_column='codProjeto',
        related_name='requisicoes',
        verbose_name='Projeto'
    )
    descricao = models.CharField(
        max_length=500,
        verbose_name='Descrição'
    )
    data_solicitacao = models.DateField(
        db_column='dataSolicitacao',
        verbose_name='Data de Solicitação'
    )
    data_limite = models.DateField(
        db_column='dataLimite',
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
        db_table = 'requisicao'
        verbose_name = 'Requisição'
        verbose_name_plural = 'Requisições'
    
    def __str__(self):
        return f"Req {self.cod_requisicao} - {self.descricao[:50]}"