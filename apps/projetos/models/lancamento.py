from django.db import models
from .projeto import Projeto

class LancamentoCusto(models.Model):
    projeto = models.ForeignKey(Projeto, on_delete=models.CASCADE, related_name='lancamentos')
    descricao = models.CharField(max_length=255)
    valor = models.DecimalField(max_digits=10, decimal_places=2)
    data = models.DateField()

    def __str__(self):
        return f"{self.descricao} - {self.valor}"
