# apps/contratos/signals.py
from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver
from django.utils import timezone
from .models import ItemContrato, Contrato

@receiver([post_save, post_delete], sender=ItemContrato)
def atualizar_valores_contrato(sender, instance, **kwargs):
    """
    Atualiza os valores do contrato quando um item é modificado ou deletado.
    """
    try:
        contrato = instance.num_contrato
        contrato.atualizar_valores()
    except Exception as e:
        # Log do erro mas não quebra o processo
        import logging
        logger = logging.getLogger(__name__)
        logger.error(f"Erro ao atualizar valores do contrato {instance.num_contrato}: {e}")

@receiver(post_save, sender=ItemContrato)
def log_pagamento(sender, instance, created, **kwargs):
    """
    Log quando um pagamento é registrado.
    """
    if not created and instance.data_pagamento:
        import logging
        logger = logging.getLogger('contratos.pagamentos')
        logger.info(
            f"Pagamento registrado - Contrato: {instance.num_contrato.num_contrato}, "
            f"Parcela: {instance.num_parcela}, Valor: R$ {instance.valor_pago}"
        )

@receiver(post_save, sender=Contrato)
def gerar_parcelas_automaticamente(sender, instance, created, **kwargs):
    """
    Gera parcelas automaticamente quando um contrato é criado.
    """
    if created and instance.parcelas > 0:
        # Verificar se já tem parcelas (para evitar duplicação)
        if not instance.itens.exists():
            try:
                instance.gerar_parcelas()
            except Exception as e:
                import logging
                logger = logging.getLogger(__name__)
                logger.error(f"Erro ao gerar parcelas para contrato {instance.num_contrato}: {e}")

@receiver(post_save, sender=ItemContrato)
def notificar_vencimento(sender, instance, created, **kwargs):
    """
    Criar notificações para parcelas próximas do vencimento.
    """
    if created or instance.situacao == '1':  # Apenas para parcelas pendentes
        hoje = timezone.now().date()
        dias_para_vencimento = (instance.data_vencimento - hoje).days
        
        # Notificar 7 dias antes do vencimento
        if dias_para_vencimento == 7:
            from apps.core.notifications import NotificationService
            NotificationService.criar_notificacao_vencimento(instance)
        
        # Notificar no dia do vencimento
        elif dias_para_vencimento == 0:
            from apps.core.notifications import NotificationService
            NotificationService.criar_notificacao_vencimento_hoje(instance)