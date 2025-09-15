# apps/projetos/models/projeto.py
from django.db import models
from django.core.exceptions import ValidationError

class Projeto(models.Model):
    '''
    Modelo alinhado com o dicionário de dados FUNETEC
    '''
    
    SITUACAO_CHOICES = [
        ('1', 'Aguardando Início'),
        ('2', 'Em andamento'),
        ('3', 'Paralisado'),
        ('4', 'Suspenso'),
        ('5', 'Cancelado'),
        ('6', 'Concluído'),
    ]
    
    cod_projeto = models.IntegerField(
        primary_key=True,
        db_column='codProjeto',
        verbose_name='Código do Projeto'
    )
    nome = models.CharField(
        max_length=200,
        verbose_name='Nome do Projeto'
    )
    data_inicio = models.DateField(
        db_column='dataInicio',
        verbose_name='Data de Início'
    )
    data_encerramento = models.DateField(
        db_column='dataEncerramento',
        verbose_name='Data de Encerramento'
    )
    valor = models.DecimalField(
        max_digits=14,
        decimal_places=2,
        verbose_name='Valor Orçado'
    )
    situacao = models.CharField(
        max_length=20,
        choices=SITUACAO_CHOICES,
        default='1',  # Default to 'Aguardando Início'
        verbose_name='Situação'
    )
    
    class Meta:
        db_table = 'projetos'
        verbose_name = 'Projeto'
        verbose_name_plural = 'Projetos'
    
    def __str__(self):
        return f"{self.cod_projeto} - {self.nome}"