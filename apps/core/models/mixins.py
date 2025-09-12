from django.db import models
from django.contrib.auth import get_user_model
from django.utils import timezone
import logging

logger = logging.getLogger('apps')

User = get_user_model()


class TimestampMixin(models.Model):
    """
    Mixin para timestamps de criação e atualização.
    Implementa padrão Observer para notificação de mudanças.
    """
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='Criado em')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='Atualizado em')
    
    class Meta:
        abstract = True


class AuditMixin(models.Model):
    """
    Mixin para auditoria de usuário.
    Implementa padrão Observer para logging de ações.
    """
    created_by = models.ForeignKey(
        'accounts.User',
        on_delete=models.PROTECT,
        related_name='%(class)s_created',
        null=True,
        blank=True,
        verbose_name='Criado por'
    )
    updated_by = models.ForeignKey(
        'accounts.User',
        on_delete=models.PROTECT,
        related_name='%(class)s_updated',
        null=True,
        blank=True,
        verbose_name='Atualizado por'
    )
    
    class Meta:
        abstract = True
    
    def save(self, *args, **kwargs):
        """
        Override do save para implementar audit trail.
        Implementa padrão Template Method.
        """
        user = kwargs.pop('user', None)
        
        # Log da operação
        operation = 'UPDATE' if self.pk else 'CREATE'
        logger.info(f'{operation} {self.__class__.__name__} by {user}')
        
        # Definir usuário de auditoria
        if user:
            if not self.pk:  # Criação
                self.created_by = user
            self.updated_by = user
        
        super().save(*args, **kwargs)


class SoftDeleteMixin(models.Model):
    """
    Mixin para soft delete.
    Implementa padrão Strategy para diferentes tipos de exclusão.
    """
    deleted_at = models.DateTimeField(null=True, blank=True, verbose_name='Excluído em')
    deleted_by = models.ForeignKey(
        'accounts.User',
        on_delete=models.PROTECT,
        related_name='%(class)s_deleted',
        null=True,
        blank=True,
        verbose_name='Excluído por'
    )
    
    class Meta:
        abstract = True
    
    def delete(self, user=None, *args, **kwargs):
        """
        Soft delete implementation.
        Implementa padrão Strategy.
        """
        self.deleted_at = timezone.now()
        self.deleted_by = user
        self.is_active = False
        self.save(user=user)
        
        # Log da exclusão
        logger.info(f'SOFT_DELETE {self.__class__.__name__} by {user}')
    
    def hard_delete(self, *args, **kwargs):
        """Hard delete quando necessário"""
        logger.warning(f'HARD_DELETE {self.__class__.__name__}')
        super().delete(*args, **kwargs)
    
    def restore(self, user=None):
        """Restaurar registro excluído"""
        self.deleted_at = None
        self.deleted_by = None
        self.is_active = True
        self.save(user=user)
        
        logger.info(f'RESTORE {self.__class__.__name__} by {user}')


class ValorMixin(models.Model):
    """
    Mixin para campos monetários.
    Implementa padrão Value Object para valores monetários.
    """
    valor = models.DecimalField(
        max_digits=14,
        decimal_places=2,
        default=0,
        verbose_name='Valor'
    )
    
    class Meta:
        abstract = True
    
    def get_valor_formatado(self):
        """Formatar valor monetário"""
        return f"R$ {self.valor:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")


class DataMixin(models.Model):
    """
    Mixin para campos de data com validação.
    Implementa padrão Template Method para validações.
    """
    data_inicio = models.DateField(verbose_name='Data de Início')
    data_fim = models.DateField(null=True, blank=True, verbose_name='Data de Fim')
    
    class Meta:
        abstract = True
    
    def clean(self):
        """
        Validação customizada.
        Template Method para validações de data.
        """
        super().clean()
        
        if self.data_fim and self.data_inicio:
            if self.data_fim < self.data_inicio:
                from django.core.exceptions import ValidationError
                raise ValidationError('Data de fim deve ser maior que data de início.')
    
    def get_duracao_dias(self):
        """Calcular duração em dias"""
        if self.data_fim:
            return (self.data_fim - self.data_inicio).days
        return (timezone.now().date() - self.data_inicio).days


class StatusMixin(models.Model):
    """
    Mixin para controle de status com máquina de estados.
    Implementa padrão State Machine.
    """
    
    class Meta:
        abstract = True
    
    def can_change_status(self, new_status):
        """
        Verificar se mudança de status é permitida.
        Template Method para validação de transições.
        """
        return True  # Implementar lógica específica nas classes filhas
    
    def change_status(self, new_status, user=None):
        """
        Alterar status com validação.
        Implementa padrão Command para mudanças de estado.
        """
        if self.can_change_status(new_status):
            old_status = getattr(self, 'situacao', None)
            self.situacao = new_status
            self.save(user=user)
            
            # Log da mudança de status
            logger.info(f'STATUS_CHANGE {self.__class__.__name__} from {old_status} to {new_status} by {user}')
            return True
        return False