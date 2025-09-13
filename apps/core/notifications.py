from django.contrib import messages
from django.utils import timezone
from datetime import timedelta
from apps.contratos.models import ItemContrato
from apps.projetos.models import Projeto

class NotificationService:
    @staticmethod
    def check_parcelas_vencendo(user, dias=7):
        """Verifica parcelas que vencem nos próximos X dias"""
        hoje = timezone.now().date()
        data_limite = hoje + timedelta(days=dias)
        
        parcelas = ItemContrato.objects.filter(
            situacao='1',
            data_vencimento__gte=hoje,
            data_vencimento__lte=data_limite
        )
        
        notifications = []
        for parcela in parcelas[:5]:  # Limitar a 5
            dias_restantes = (parcela.data_vencimento - hoje).days
            notifications.append({
                'type': 'warning',
                'title': f'Parcela vence em {dias_restantes} dias',
                'message': f'Contrato {parcela.num_contrato.num_contrato} - R$ {parcela.valor_parcela}',
                'url': f'/contratos/{parcela.num_contrato.pk}/',
                'icon': 'fas fa-clock'
            })
        
        return notifications
    
    @staticmethod
    def check_projetos_atrasados(user):
        """Verifica projetos atrasados"""
        hoje = timezone.now().date()
        
        projetos = Projeto.objects.filter(
            situacao__in=['1', '2'],
            data_encerramento__lt=hoje
        )
        
        notifications = []
        for projeto in projetos[:3]:
            dias_atraso = (hoje - projeto.data_encerramento).days
            notifications.append({
                'type': 'danger',
                'title': f'Projeto #{projeto.cod_projeto} atrasado',
                'message': f'{projeto.nome[:40]} - {dias_atraso} dias de atraso',
                'url': f'/projetos/{projeto.pk}/',
                'icon': 'fas fa-exclamation-triangle'
            })
        
        return notifications
    
    @staticmethod
    def get_all_notifications(user):
        """Retorna todas as notificações do usuário"""
        notifications = []
        
        if user.can_view_financial_data():
            notifications.extend(NotificationService.check_parcelas_vencendo(user))
        
        if user.can_manage_projects():
            notifications.extend(NotificationService.check_projetos_atrasados(user))
        
        return notifications