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
        verbose_name='Código do Projeto',
        db_column='codProjeto'
    )
    nome = models.CharField(
        max_length=200,
        verbose_name='Nome do Projeto'
    )
    data_inicio = models.DateField(
        verbose_name='Data de Início',
        db_column='dataInicio'
    )
    data_encerramento = models.DateField(
        verbose_name='Data de Encerramento',
        db_column='dataEncerramento'
    )
    valor = models.DecimalField(
        max_digits=14,
        decimal_places=2,
        verbose_name='Valor Orçado'
    )
    situacao = models.CharField(
        max_length=20,
        choices=SITUACAO_CHOICES,
        verbose_name='Situação'
    )

    def save(self, *args, **kwargs):
        if not self.cod_projeto:
            # Auto-gerar código do projeto
            ultimo_projeto = Projeto.objects.order_by('-cod_projeto').first()
            self.cod_projeto = (ultimo_projeto.cod_projeto + 1) if ultimo_projeto else 1
        super().save(*args, **kwargs)
    class Meta:
        db_table = 'projetos'
        verbose_name = 'Projeto'
        verbose_name_plural = 'Projetos'
    
    def __str__(self):
        return f"{self.cod_projeto} - {self.nome}"