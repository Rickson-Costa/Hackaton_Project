from django.db import models
from django.core.exceptions import ValidationError
from apps.core.models.base import AuditableModel, SituacaoMixin
from apps.core.models.mixins import ValorMixin, StatusMixin
from .projeto import Projeto
from .ordem import Ordem

class ItemOrdem(AuditableModel, SituacaoMixin, ValorMixin):
    """
    Modelo para Itens da Ordem de Serviço.
    Implementa padrão Composite para estrutura hierárquica.
    """
    
    SITUACAO_CHOICES = [
        ('1', 'Lançado'),
        ('2', 'Cancelado'),
        ('3', 'Entregue'),
    ]
    
    cod_ordem = models.ForeignKey(
        Ordem,
        on_delete=models.CASCADE,
        related_name='itens',
        verbose_name='Ordem de Serviço'
    )
    cod_item = models.IntegerField(
        verbose_name='Código do Item'
    )
    descricao = models.CharField(
        max_length=500,
        verbose_name='Descrição do Item'
    )
    data_solicitacao = models.DateField(
        verbose_name='Data de Solicitação'
    )
    data_limite = models.DateField(
        verbose_name='Data Limite de Entrega'
    )
    valor = models.DecimalField(
        max_digits=14,
        decimal_places=2,
        verbose_name='Valor do Item'
    )
    data_recebido = models.DateField(
        verbose_name='Data de Recebimento',
        null=True,
        blank=True
    )
    situacao = models.CharField(
        max_length=20,
        choices=SITUACAO_CHOICES,
        default='1',
        verbose_name='Situação'
    )
    
    # Campos de controle
    quantidade = models.DecimalField(
        'Quantidade',
        max_digits=10,
        decimal_places=2,
        default=1
    )
    unidade = models.CharField(
        'Unidade',
        max_length=10,
        default='UN'
    )
    valor_unitario = models.DecimalField(
        'Valor Unitário',
        max_digits=14,
        decimal_places=2,
        default=0
    )
    
    class Meta:
        verbose_name = 'Item da Ordem'
        verbose_name_plural = 'Itens da Ordem'
        ordering = ['cod_item']
        unique_together = [['cod_ordem', 'cod_item']]
        constraints = [
            models.CheckConstraint(
                check=models.Q(data_limite__gte=models.F('data_solicitacao')),
                name='item_ordem_data_limite_valida'
            ),
            models.CheckConstraint(
                check=models.Q(valor__gte=0),
                name='item_ordem_valor_positivo'
            ),
            models.CheckConstraint(
                check=models.Q(quantidade__gt=0),
                name='item_ordem_quantidade_positiva'
            )
        ]
    
    def __str__(self):
        return f"Item {self.cod_item} - OS {self.cod_ordem.cod_ordem}: {self.descricao[:30]}"
    
    def clean(self):
        """Validação customizada"""
        super().clean()
        
        # Calcular valor total baseado na quantidade e valor unitário
        if self.quantidade and self.valor_unitario:
            self.valor = self.quantidade * self.valor_unitario
        
        # Validar se ordem está ativa
        if self.cod_ordem and self.cod_ordem.situacao in ['3', '4']:
            raise ValidationError('Não é possível criar item para ordem cancelada ou concluída.')
    
    def entregar(self, user=None):
        """Command Pattern para entregar item"""
        if self.situacao == '1':  # Lançado
            self.situacao = '3'  # Entregue
            self.data_recebido = timezone.now().date()
            self.save(user=user)
            
            # Observer Pattern: Verificar se todos os itens foram entregues
            self._check_ordem_completion()
            return True
        return False
    
    def _check_ordem_completion(self):
        """Observer Pattern para verificar conclusão da ordem"""
        ordem = self.cod_ordem
        total_itens = ordem.itens.count()
        itens_entregues = ordem.itens.filter(situacao='3').count()
        
        # Se todos os itens foram entregues, marcar ordem como concluída
        if total_itens == itens_entregues and ordem.situacao == '2':
            ordem.concluir()
    
    def get_status_prazo(self):
        """Observer Pattern para status de prazo do item"""
        from django.utils import timezone
        hoje = timezone.now().date()
        
        if self.situacao in ['2', '3']:  # Cancelado ou Entregue
            return 'verde'
        
        dias_restantes = (self.data_limite - hoje).days
        
        if dias_restantes < 0:
            return 'vermelho'  # Atrasado
        elif dias_restantes <= 1:
            return 'amarelo'   # Próximo do prazo
        else:
            return 'verde'     # No prazo
    
    def save(self, *args, **kwargs):
        """Override do save com cálculos automáticos"""
        # Calcular valor total
        if self.quantidade and self.valor_unitario:
            self.valor = self.quantidade * self.valor_unitario
        
        super().save(*args, **kwargs)