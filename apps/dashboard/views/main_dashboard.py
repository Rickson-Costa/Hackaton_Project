# apps/dashboard/views/main_dashboard.py
from django.views.generic import TemplateView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.db.models import Sum, Count, Q, F
from django.utils import timezone
from datetime import timedelta
from decimal import Decimal

from apps.projetos.models import Projeto, Requisicao, Ordem
from apps.contratos.models import Contrato, ItemContrato

class DashboardView(LoginRequiredMixin, TemplateView):
    template_name = 'dashboard/index.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        hoje = timezone.now().date()
        
        # KPIs reais
        projetos = Projeto.objects.all()
        contratos = Contrato.objects.all()
        
        # Projetos ativos (situação 1 ou 2)
        projetos_ativos = projetos.filter(situacao__in=['1', '2']).count()
        projetos_atrasados = projetos.filter(
            situacao__in=['1', '2'],
            data_encerramento__lt=hoje
        ).count()
        
        # Contratos por tipo
        contratos_pf = contratos.filter(tipo_pessoa=1)
        contratos_pj = contratos.filter(tipo_pessoa=2)
        
        # Inadimplência
        parcelas_vencidas = ItemContrato.objects.filter(
            situacao='1',
            data_vencimento__lt=hoje
        )
        valor_inadimplencia = sum(
            (p.valor_parcela - p.valor_pago) for p in parcelas_vencidas
        )
        
        context.update({
            'kpis': {
                'projetos_ativos': projetos_ativos,
                'projetos_atrasados': projetos_atrasados,
                'contratos_pf_total': contratos_pf.count(),
                'contratos_pj_total': contratos_pj.count(),
                'valor_inadimplencia': float(valor_inadimplencia),
                'percentual_inadimplencia': round(
                    (valor_inadimplencia / contratos.aggregate(
                        Sum('valor'))['valor__sum'] * 100) if contratos.exists() else 0, 2
                ),
            },
            # These methods are now defined below
            'alertas': self._get_alertas(),
            'projetos_criticos': self._get_projetos_criticos(),
        })
        
        return context

    
    def _get_projetos_criticos(self):
        """
        Returns a queryset of projects that are considered critical.
        A project is critical if it is overdue or has other issues.
        """
        hoje = timezone.now().date()
        
        # Example logic: Projects that are 'Em Andamento' but past their deadline.
        # This is similar to the 'projetos_atrasados' KPI, but returns the objects themselves.
        critical_projects_queryset = Projeto.objects.filter(
            situacao__in=['1', '2'], 
            data_encerramento__lt=hoje
        ).order_by('data_encerramento')

        return critical_projects_queryset[:5] # Return the top 5 critical projects

    def _get_alertas(self):
        alertas = []
        hoje = timezone.now().date()
        
        # Projetos com prazo próximo
        projetos_proximos = Projeto.objects.filter(
            situacao__in=['1', '2'],
            data_encerramento__lte=hoje + timedelta(days=7),
            data_encerramento__gte=hoje
        )[:3]
        
        for projeto in projetos_proximos:
            dias = (projeto.data_encerramento - hoje).days
            alertas.append({
                'tipo': 'warning',
                'titulo': f'Projeto #{projeto.cod_projeto} - Prazo Próximo',
                'mensagem': f'{projeto.nome[:40]} - Vence em {dias} dias',
                'url': f'/projetos/{projeto.pk}/'
            })
        
        # Parcelas vencidas
        parcelas_vencidas = ItemContrato.objects.filter(
            situacao='1',
            data_vencimento__lt=hoje
        )[:3]
        
        for parcela in parcelas_vencidas:
            dias_atraso = (hoje - parcela.data_vencimento).days
            alertas.append({
                'tipo': 'danger',
                'titulo': f'Parcela Vencida - Contrato {parcela.num_contrato.num_contrato}',
                'mensagem': f'R$ {parcela.valor_parcela} - {dias_atraso} dias de atraso',
                'url': f'/contratos/{parcela.num_contrato.pk}/'
            })
        
        return alertas
    
    def _calcular_crescimento_projetos(self):
        """Calcula crescimento percentual de projetos no mês"""
        hoje = timezone.now().date()
        inicio_mes = hoje.replace(day=1)
        mes_anterior = (inicio_mes - timedelta(days=1)).replace(day=1)
        
        projetos_mes_atual = Projeto.objects.filter(
            created_at__gte=inicio_mes
        ).count()
        
        projetos_mes_anterior = Projeto.objects.filter(
            created_at__gte=mes_anterior,
            created_at__lt=inicio_mes
        ).count()
        
        if projetos_mes_anterior > 0:
            crescimento = ((projetos_mes_atual - projetos_mes_anterior) / projetos_mes_anterior * 100)
            return round(crescimento, 1)
        return 0