from django.db import models
from .projeto import Projeto

class MarcoProjeto(models.Model):
    STATUS_CHOICES = (
        ('pendente', 'Pendente'),
        ('entregue', 'Entregue'),
        ('aprovado', 'Aprovado'),
    )
    projeto = models.ForeignKey(Projeto, on_delete=models.CASCADE, related_name='marcos')
    descricao = models.CharField(max_length=255)
    data_prevista = models.DateField()
    data_entrega = models.DateField(blank=True, null=True)
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='pendente')

    def __str__(self):
        return self.descricao
