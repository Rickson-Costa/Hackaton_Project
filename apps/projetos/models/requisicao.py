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
        verbose_name='Código da Requisição'
    )
    cod_projeto = models.ForeignKey(
        'projetos.Projeto',  # Use string reference
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
    def save(self, *args, **kwargs):
        if not self.cod_requisicao:
            # Auto-gerar código da requisição
            ultima_req = Requisicao.objects.order_by('-cod_requisicao').first()
            self.cod_requisicao = (ultima_req.cod_requisicao + 1) if ultima_req else 1
        super().save(*args, **kwargs)
    class Meta:
        db_table = 'requisicao'
        verbose_name = 'Requisição'
        verbose_name_plural = 'Requisições'