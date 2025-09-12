from django.views.generic import TemplateView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.db import models
from django.utils import timezone
from django.utils.decorators import method_decorator
from django.views.decorators.cache import cache_page

@method_decorator(cache_page(60 * 15), name='dispatch')
class DashboardView(LoginRequiredMixin, TemplateView):
    template_name = 'dashboard/index.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        # Importar modelos aqui para evitar import circular
        from apps.projetos.models import Projeto
        from apps.contratos.models import Contrato, ItemContrato

        # =====================================================================
        # Métricas de Projetos
        # =====================================================================
        projetos = Projeto.objects.all()
        total_projetos = projetos.count()
        em_andamento = projetos.filter(situacao='2').count()
        concluidos = projetos.filter(situacao='6').count()
        
        agregados_projetos = projetos.aggregate(
            valor_total=models.Sum('valor'),
            valor_realizado=models.Sum('valor_realizado'),
            custo_previsto=models.Sum('custo_previsto'),
            custo_realizado=models.Sum('custo_realizado')
        )
        
        custo_previsto_total = agregados_projetos.get('custo_previsto') or 0
        custo_realizado_total = agregados_projetos.get('custo_realizado') or 0

        context['metricas_projetos'] = {
            'total': total_projetos,
            'em_andamento': em_andamento,
            'concluidos': concluidos,
            'atrasados': 0,  # Lógica de atraso a ser implementada
            'valor_total': agregados_projetos.get('valor_total') or 0,
            'custo_previsto': custo_previsto_total,
            'custo_realizado': custo_realizado_total,
        }

        # =====================================================================
        # Gráficos
        # =====================================================================
        # Gráfico de Comparativo de Custos
        context['grafico_custos'] = {
            'labels': ['Custo Previsto', 'Custo Realizado'],
            'data': [float(custo_previsto_total), float(custo_realizado_total)],
            'backgroundColor': ['#007bff', '#28a745'],
        }

        # Manter outros dados estáticos por enquanto
        context.update({
            'metricas_contratos': {'total': 0, 'ativos': 0, 'pessoa_fisica': 0, 'pessoa_juridica': 0, 'valor_total': 0, 'valor_pago': 0, 'valor_pendente': 0, 'percentual_pago': 0},
            'metricas_financeiras': {'parcelas_vencidas': 0, 'valor_vencido': 0, 'parcelas_proximas': 0, 'valor_a_vencer': 0, 'status_cobranca': 'normal'},
            'alertas': [],
            'projetos_recentes': projetos.order_by('-created_at')[:5],
            'parcelas_vencimento': [],
        })

        return context