from django.db import models
from django.core.exceptions import ValidationError

class Requisicao(models.Model):
    '''
    Modelo simplificado para Requisições.
    '''
    
    SITUACAO_CHOICES = [
        ('1', 'Aguardando Início'),
        ('2', 'Em andamento'),
        ('3', 'Suspensa'),
        ('4', 'Cancelada'),
        ('5', 'Concluída'),
    ]
    
    cod_requisicao = models.IntegerField(
        primary_key=True,
        verbose_name='Código da Requisição',
        db_column='codRequisicao'
    )
    cod_projeto = models.ForeignKey(
        'projetos.Projeto',
        on_delete=models.PROTECT,
        related_name='requisicoes',
        verbose_name='Projeto',
        db_column='codProjeto'
    )
    descricao = models.CharField(
        max_length=500,
        verbose_name='Descrição da Requisição',
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
        verbose_name='Valor da Requisição',
        db_column='valor'
    )
    situacao = models.CharField(
        max_length=20,
        choices=SITUACAO_CHOICES,
        default='1',
        verbose_name='Situação',
        db_column='situacao'
    )
    prioridade = models.CharField(
        'Prioridade',
        max_length=10,
        choices=[
            ('baixa', 'Baixa'),
            ('normal', 'Normal'),
            ('alta', 'Alta'),
            ('critica', 'Crítica'),
        ],
        default='normal',
        null=True
    )
    
    # Campos de auditoria básicos
    created_at = models.DateTimeField(auto_now_add=True, null=True)
    updated_at = models.DateTimeField(auto_now=True, null=True)
    created_by = models.ForeignKey(
        'accounts.User',
        on_delete=models.PROTECT,
        related_name='requisicoes_criadas',
        null=True,
        blank=True
    )
    
    class Meta:
        db_table = 'requisicao'
        verbose_name = 'Requisição'
        verbose_name_plural = 'Requisições'
        ordering = ['-data_solicitacao']
    
    def __str__(self):
        return f"REQ-{self.cod_requisicao}: {self.descricao[:50]}"
    
    def clean(self):
        '''Validação básica'''
        super().clean()
        
        if self.data_limite and self.data_solicitacao:
            if self.data_limite < self.data_solicitacao:
                raise ValidationError('Data limite deve ser maior que data de solicitação.')