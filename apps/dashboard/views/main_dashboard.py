from django.views.generic import TemplateView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.db import models
from django.utils import timezone

class DashboardView(LoginRequiredMixin, TemplateView):
    template_name = 'dashboard/index.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        # Dados estáticos para evitar erros enquanto desenvolvemos
        context.update({
            'metricas_projetos': {
                'total': 0,
                'em_andamento': 0,
                'atrasados': 0,
                'concluidos': 0,
                'valor_total': 0,
                'valor_realizado': 0,
                'percentual_realizado': 0,
                'status_geral': 'normal'
            },
            'metricas_contratos': {
                'total': 0,
                'ativos': 0,
                'pessoa_fisica': 0,
                'pessoa_juridica': 0,
                'valor_total': 0,
                'valor_pago': 0,
                'valor_pendente': 0,
                'percentual_pago': 0
            },
            'metricas_financeiras': {
                'parcelas_vencidas': 0,
                'valor_vencido': 0,
                'parcelas_proximas': 0,
                'valor_a_vencer': 0,
                'status_cobranca': 'normal'
            },
            'alertas': [],
            'projetos_recentes': [],
            'parcelas_vencimento': [],
            'graficos_config': {
                'projetos_por_situacao': {
                    'labels': ['Aguardando', 'Em Andamento', 'Concluído'],
                    'data': [0, 0, 0],
                    'backgroundColor': ['#6c757d', '#007bff', '#28a745']
                },
                'contratos_por_tipo': {
                    'labels': ['Pessoa Física', 'Pessoa Jurídica'],
                    'data': [0, 0],
                    'backgroundColor': ['#007bff', '#28a745']
                },
                'evolucao_financeira': {
                    'labels': ['Jan', 'Fev', 'Mar', 'Abr', 'Mai', 'Jun'],
                    'datasets': [
                        {
                            'label': 'Valor Orçado',
                            'data': [0, 0, 0, 0, 0, 0],
                            'borderColor': '#007bff',
                            'backgroundColor': 'rgba(0, 123, 255, 0.1)'
                        },
                        {
                            'label': 'Valor Realizado',
                            'data': [0, 0, 0, 0, 0, 0],
                            'borderColor': '#28a745',
                            'backgroundColor': 'rgba(40, 167, 69, 0.1)'
                        }
                    ]
                },
                'status_projetos': {
                    'verde': 0,
                    'amarelo': 0,
                    'vermelho': 0,
                    'total': 0
                }
            }
        })
        
        return context