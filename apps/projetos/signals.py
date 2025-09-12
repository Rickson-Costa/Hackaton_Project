from django.db import models
from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver
from .models import LancamentoCusto

@receiver([post_save, post_delete], sender=LancamentoCusto)
def atualizar_custo_realizado_projeto(sender, instance, **kwargs):
    """
    Atualiza o custo realizado do projeto quando um lançamento é salvo ou deletado.
    """
    projeto = instance.projeto
    total_custo = projeto.lancamentos.aggregate(total=models.Sum('valor'))['total'] or 0.00
    
    # Evita recursão infinita do signal
    if projeto.custo_realizado != total_custo:
        projeto.custo_realizado = total_custo
        projeto.save(update_fields=['custo_realizado'])
