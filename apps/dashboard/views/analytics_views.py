from django.views.generic import TemplateView, View
from django.contrib.auth.mixins import LoginRequiredMixin, PermissionRequiredMixin
from django.http import JsonResponse
from django.db.models import Sum, Count, Avg, Q
from django.utils import timezone
from datetime import timedelta, datetime
import json
from apps.projetos.models import Projeto
from apps.contratos.models import Contrato, ItemContrato

from apps.core.middleware import BaseService

from ..services.financeiro_analytics import FinanceiroAnalyticsService

class FinanceiroAnalyticsView(LoginRequiredMixin, TemplateView):
    template_name = "dashboard/analytics_financeiro.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        svc = FinanceiroAnalyticsService()
        context.update({
            'resumo': svc.get_resumo_financeiro(),
            'receitas_por_mes': svc.get_receitas_por_mes(),
            'despesas_por_mes': svc.get_despesas_por_mes(),
        })
        return context


class ProjetosAnalyticsView(LoginRequiredMixin, TemplateView):
    """View para analytics de projetos"""
    template_name = 'dashboard/analytics/projetos.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        analytics_service = ProjetosAnalyticsService(user=self.request.user)
        
        context.update({
            'metricas_gerais': analytics_service.get_metricas_gerais(),
            'distribuicao_responsaveis': analytics_service.get_distribuicao_responsaveis(),
            'projetos_por_cliente': analytics_service.get_projetos_por_cliente(),
            'performance_prazo': analytics_service.get_performance_prazo(),
            'evolucao_mensal': analytics_service.get_evolucao_mensal(),
        })
        
        return context


class ContratosAnalyticsView(LoginRequiredMixin, PermissionRequiredMixin, TemplateView):
    """View para analytics de contratos"""
    template_name = 'dashboard/analytics/contratos.html'
    permission_required = 'accounts.can_view_financial_data'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        analytics_service = ContratosAnalyticsService(user=self.request.user)
        
        context.update({
            'metricas_contratos': analytics_service.get_metricas_contratos(),
            'distribuicao_prestadores': analytics_service.get_distribuicao_prestadores(),
            'analise_pagamentos': analytics_service.get_analise_pagamentos(),
            'inadimplencia': analytics_service.get_inadimplencia(),
        })
        
        return context


class FinanceiroAnalyticsView(LoginRequiredMixin, PermissionRequiredMixin, TemplateView):
    """View para analytics financeiros"""
    template_name = 'dashboard/analytics/financeiro.html'
    permission_required = 'accounts.can_view_financial_data'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        analytics_service = FinanceiroAnalyticsService(user=self.request.user)
        
        context.update({
            'resumo_financeiro': analytics_service.get_resumo_financeiro(),
            'fluxo_caixa': analytics_service.get_fluxo_caixa(),
            'receitas_por_mes': analytics_service.get_receitas_por_mes(),
            'impostos_retidos': analytics_service.get_impostos_retidos(),
        })
        
        return context


# APIs para dados dos gráficos (AJAX)

class ProjetosChartDataView(LoginRequiredMixin, View):
    """API para dados de gráficos de projetos"""
    
    def get(self, request, *args, **kwargs):
        chart_type = request.GET.get('type', 'situacao')
        analytics_service = ProjetosAnalyticsService(user=request.user)
        
        data = {}
        
        if chart_type == 'situacao':
            data = analytics_service.get_chart_situacao()
        elif chart_type == 'evolucao':
            data = analytics_service.get_chart_evolucao()
        elif chart_type == 'responsaveis':
            data = analytics_service.get_chart_responsaveis()
        elif chart_type == 'clientes':
            data = analytics_service.get_chart_clientes()
        elif chart_type == 'status_prazo':
            data = analytics_service.get_chart_status_prazo()
        elif chart_type == 'status_custo':
            data = analytics_service.get_chart_status_custo()
        
        return JsonResponse(data)


class ContratosChartDataView(LoginRequiredMixin, PermissionRequiredMixin, View):
    """API para dados de gráficos de contratos"""
    permission_required = 'accounts.can_view_financial_data'
    
    def get(self, request, *args, **kwargs):
        chart_type = request.GET.get('type', 'tipo_pessoa')
        analytics_service = ContratosAnalyticsService(user=request.user)
        
        data = {}
        
        if chart_type == 'tipo_pessoa':
            data = analytics_service.get_chart_tipo_pessoa()
        elif chart_type == 'situacao':
            data = analytics_service.get_chart_situacao()
        elif chart_type == 'valores_mensais':
            data = analytics_service.get_chart_valores_mensais()
        elif chart_type == 'prestadores_top':
            data = analytics_service.get_chart_prestadores_top()
        
        return JsonResponse(data)


class FinanceiroChartDataView(LoginRequiredMixin, PermissionRequiredMixin, View):
    """API para dados de gráficos financeiros"""
    permission_required = 'accounts.can_view_financial_data'
    
    def get(self, request, *args, **kwargs):
        chart_type = request.GET.get('type', 'fluxo_caixa')
        analytics_service = FinanceiroAnalyticsService(user=request.user)
        
        data = {}
        
        if chart_type == 'fluxo_caixa':
            data = analytics_service.get_chart_fluxo_caixa()
        elif chart_type == 'receitas':
            data = analytics_service.get_chart_receitas()
        elif chart_type == 'inadimplencia':
            data = analytics_service.get_chart_inadimplencia()
        elif chart_type == 'impostos':
            data = analytics_service.get_chart_impostos()
        
        return JsonResponse(data)


# Services para Analytics

class ProjetosAnalyticsService(BaseService):
    """Service para analytics de projetos"""
    
    def get_metricas_gerais(self):
        """Métricas gerais dos projetos"""
        projetos = self._get_projetos_queryset()
        
        return {
            'total_projetos': projetos.count(),
            'valor_total': projetos.aggregate(Sum('valor'))['valor__sum'] or 0,
            'valor_medio': projetos.aggregate(Avg('valor'))['valor__avg'] or 0,
            'taxa_conclusao': self._calcular_taxa_conclusao(projetos),
            'tempo_medio_execucao': self._calcular_tempo_medio_execucao(projetos),
            'projetos_no_prazo': self._contar_projetos_no_prazo(projetos),
        }
    
    def get_distribuicao_responsaveis(self):
        """Distribuição de projetos por responsável"""
        return self._get_projetos_queryset().values(
            'responsavel__first_name',
            'responsavel__last_name'
        ).annotate(
            count=Count('cod_projeto'),
            valor_total=Sum('valor')
        ).order_by('-count')[:10]
    
    def get_projetos_por_cliente(self):
        """Top clientes por número de projetos"""
        return self._get_projetos_queryset().values(
            'cliente_nome'
        ).annotate(
            count=Count('cod_projeto'),
            valor_total=Sum('valor')
        ).order_by('-valor_total')[:10]
    
    def get_performance_prazo(self):
        """Análise de performance de prazos"""
        projetos = self._get_projetos_queryset()
        
        no_prazo = 0
        atrasados = 0
        antecipados = 0
        
        for projeto in projetos.filter(situacao='6'):  # Concluídos
            if hasattr(projeto, 'data_conclusao_real'):
                if projeto.data_conclusao_real <= projeto.data_encerramento:
                    if projeto.data_conclusao_real < projeto.data_encerramento:
                        antecipados += 1
                    else:
                        no_prazo += 1
                else:
                    atrasados += 1
        
        return {
            'no_prazo': no_prazo,
            'atrasados': atrasados,
            'antecipados': antecipados,
            'total_analisados': no_prazo + atrasados + antecipados
        }
    
    def get_chart_situacao(self):
        """Dados para gráfico de pizza - situação dos projetos"""
        dados = self._get_projetos_queryset().values('situacao').annotate(
            count=Count('cod_projeto')
        )
        
        situacao_labels = {
            '1': 'Aguardando Início',
            '2': 'Em Andamento',
            '3': 'Paralisado',
            '4': 'Suspenso',
            '5': 'Cancelado',
            '6': 'Concluído'
        }
        
        return {
            'type': 'doughnut',
            'data': {
                'labels': [situacao_labels.get(item['situacao'], item['situacao']) for item in dados],
                'datasets': [{
                    'data': [item['count'] for item in dados],
                    'backgroundColor': [
                        '#6c757d', '#007bff', '#ffc107', 
                        '#fd7e14', '#dc3545', '#28a745'
                    ]
                }]
            },
            'options': {
                'responsive': True,
                'plugins': {
                    'legend': {'position': 'bottom'}
                }
            }
        }
    
    def get_chart_evolucao(self):
        """Dados para gráfico de linha - evolução temporal"""
        hoje = timezone.now().date()
        meses = []
        projetos_criados = []
        projetos_concluidos = []
        
        for i in range(12):
            mes = (hoje.replace(day=1) - timedelta(days=30*i))
            meses.insert(0, mes.strftime('%b/%Y'))
            
            criados = self._get_projetos_queryset().filter(
                created_at__year=mes.year,
                created_at__month=mes.month
            ).count()
            
            concluidos = self._get_projetos_queryset().filter(
                situacao='6',
                updated_at__year=mes.year,
                updated_at__month=mes.month
            ).count()
            
            projetos_criados.insert(0, criados)
            projetos_concluidos.insert(0, concluidos)
        
        return {
            'type': 'line',
            'data': {
                'labels': meses,
                'datasets': [
                    {
                        'label': 'Projetos Criados',
                        'data': projetos_criados,
                        'borderColor': '#007bff',
                        'backgroundColor': 'rgba(0, 123, 255, 0.1)',
                        'tension': 0.1
                    },
                    {
                        'label': 'Projetos Concluídos',
                        'data': projetos_concluidos,
                        'borderColor': '#28a745',
                        'backgroundColor': 'rgba(40, 167, 69, 0.1)',
                        'tension': 0.1
                    }
                ]
            },
            'options': {
                'responsive': True,
                'scales': {
                    'y': {'beginAtZero': True}
                }
            }
        }
    
    def _get_projetos_queryset(self):
        """Obter queryset de projetos baseado nas permissões"""
        if self.user.can_manage_projects():
            return Projeto.objects.all()
        elif self.user.is_cliente():
            return Projeto.objects.filter(cliente_email=self.user.email)
        else:
            return Projeto.objects.filter(responsavel=self.user)
    
    def _calcular_taxa_conclusao(self, projetos):
        """Calcular taxa de conclusão"""
        total = projetos.count()
        if total == 0:
            return 0
        
        concluidos = projetos.filter(situacao='6').count()
        return round((concluidos / total) * 100, 2)
    
    def _calcular_tempo_medio_execucao(self, projetos):
        """Calcular tempo médio de execução"""
        # Implementar lógica baseada nas datas de início e conclusão
        return 0  # Placeholder
    
    def _contar_projetos_no_prazo(self, projetos):
        """Contar projetos no prazo"""
        hoje = timezone.now().date()
        
        # Projetos em andamento dentro do prazo
        no_prazo = projetos.filter(
            situacao__in=['1', '2'],
            data_encerramento__gte=hoje
        ).count()
        
        # Projetos concluídos no prazo
        concluidos_no_prazo = projetos.filter(
            situacao='6'
            # TODO: Adicionar lógica para verificar se foi concluído no prazo
        ).count()
        
        return no_prazo + concluidos_no_prazo


class ContratosAnalyticsService(BaseService):
    """Service para analytics de contratos"""
    
    def get_metricas_contratos(self):
        """Métricas gerais dos contratos"""
        contratos = self._get_contratos_queryset()
        
        return {
            'total_contratos': contratos.count(),
            'valor_total': contratos.aggregate(Sum('valor'))['valor__sum'] or 0,
            'valor_pago': contratos.aggregate(Sum('valor_pago'))['valor_pago__sum'] or 0,
            'valor_pendente': contratos.aggregate(Sum('valor_pendente'))['valor_pendente__sum'] or 0,
            'contratos_pf': contratos.filter(tipo_pessoa=1).count(),
            'contratos_pj': contratos.filter(tipo_pessoa=2).count(),
            'ticket_medio': contratos.aggregate(Avg('valor'))['valor__avg'] or 0,
        }
    
    def get_distribuicao_prestadores(self):
        """Top prestadores por valor de contratos"""
        return self._get_contratos_queryset().values(
            'contratado', 'cpf_cnpj'
        ).annotate(
            total_contratos=Count('num_contrato'),
            valor_total=Sum('valor'),
            valor_pago=Sum('valor_pago')
        ).order_by('-valor_total')[:10]
    
    def get_analise_pagamentos(self):
        """Análise de pagamentos"""
        hoje = timezone.now().date()
        
        parcelas_total = ItemContrato.objects.count()
        parcelas_pagas = ItemContrato.objects.filter(situacao='3').count()
        parcelas_vencidas = ItemContrato.objects.filter(
            situacao='1',
            data_vencimento__lt=hoje
        ).count()
        
        return {
            'parcelas_total': parcelas_total,
            'parcelas_pagas': parcelas_pagas,
            'parcelas_pendentes': parcelas_total - parcelas_pagas,
            'parcelas_vencidas': parcelas_vencidas,
            'taxa_pagamento': round((parcelas_pagas / parcelas_total * 100) if parcelas_total > 0 else 0, 2),
            'taxa_inadimplencia': round((parcelas_vencidas / parcelas_total * 100) if parcelas_total > 0 else 0, 2)
        }
    
    def get_inadimplencia(self):
        """Análise de inadimplência por período"""
        hoje = timezone.now().date()
        
        inadimplencia = {
            '0-30': {'count': 0, 'valor': 0},
            '31-60': {'count': 0, 'valor': 0},
            '61-90': {'count': 0, 'valor': 0},
            '90+': {'count': 0, 'valor': 0}
        }
        
        parcelas_vencidas = ItemContrato.objects.filter(
            situacao='1',
            data_vencimento__lt=hoje
        )
        
        for parcela in parcelas_vencidas:
            dias_atraso = (hoje - parcela.data_vencimento).days
            valor_pendente = float(parcela.get_valor_pendente())
            
            if dias_atraso <= 30:
                periodo = '0-30'
            elif dias_atraso <= 60:
                periodo = '31-60'
            elif dias_atraso <= 90:
                periodo = '61-90'
            else:
                periodo = '90+'
            
            inadimplencia[periodo]['count'] += 1
            inadimplencia[periodo]['valor'] += valor_pendente
        
        return inadimplencia
    
    def get_chart_tipo_pessoa(self):
        """Gráfico de contratos por tipo de pessoa"""
        dados = self._get_contratos_queryset().values('tipo_pessoa').annotate(
            count=Count('num_contrato'),
            valor=Sum('valor')
        )
        
        labels = []
        counts = []
        valores = []
        
        for item in dados:
            label = 'Pessoa Física' if item['tipo_pessoa'] == 1 else 'Pessoa Jurídica'
            labels.append(label)
            counts.append(item['count'])
            valores.append(float(item['valor'] or 0))
        
        return {
            'type': 'bar',
            'data': {
                'labels': labels,
                'datasets': [
                    {
                        'label': 'Quantidade',
                        'data': counts,
                        'backgroundColor': '#007bff',
                        'yAxisID': 'y'
                    },
                    {
                        'label': 'Valor (R$)',
                        'data': valores,
                        'backgroundColor': '#28a745',
                        'yAxisID': 'y1'
                    }
                ]
            },
            'options': {
                'responsive': True,
                'scales': {
                    'y': {'type': 'linear', 'display': True, 'position': 'left'},
                    'y1': {'type': 'linear', 'display': True, 'position': 'right'}
                }
            }
        }
    
    def _get_contratos_queryset(self):
        """Obter queryset de contratos baseado nas permissões"""
        if self.user.can_manage_contracts():
            return Contrato.objects.all()
        else:
            # Filtrar baseado nos projetos acessíveis
            return Contrato.objects.none()  # Implementar lógica específica


class FinanceiroAnalyticsService(BaseService):
    """Service para analytics financeiros"""
    
    def get_resumo_financeiro(self):
        """Resumo financeiro geral"""
        hoje = timezone.now().date()
        mes_atual = hoje.replace(day=1)
        mes_anterior = (mes_atual - timedelta(days=1)).replace(day=1)
        
        # Valores do mês atual
        contratos_mes = Contrato.objects.filter(created_at__gte=mes_atual)
        valor_mes = contratos_mes.aggregate(Sum('valor'))['valor__sum'] or 0
        
        # Valores do mês anterior
        contratos_mes_anterior = Contrato.objects.filter(
            created_at__gte=mes_anterior,
            created_at__lt=mes_atual
        )
        valor_mes_anterior = contratos_mes_anterior.aggregate(Sum('valor'))['valor__sum'] or 0
        
        # Crescimento
        crescimento = 0
        if valor_mes_anterior > 0:
            crescimento = ((valor_mes - valor_mes_anterior) / valor_mes_anterior) * 100
        
        return {
            'valor_mes_atual': valor_mes,
            'valor_mes_anterior': valor_mes_anterior,
            'crescimento_percentual': round(crescimento, 2),
            'total_recebido': self._calcular_total_recebido(),
            'total_pendente': self._calcular_total_pendente(),
            'inadimplencia_total': self._calcular_inadimplencia_total(),
        }
    
    def get_fluxo_caixa(self):
        """Dados para fluxo de caixa projetado"""
        hoje = timezone.now().date()
        fluxo = []
        
        # Próximos 12 meses
        for i in range(12):
            mes = hoje.replace(day=1) + timedelta(days=30*i)
            
            # Parcelas que vencem no mês
            parcelas_mes = ItemContrato.objects.filter(
                situacao='1',
                data_vencimento__year=mes.year,
                data_vencimento__month=mes.month
            )
            
            valor_previsto = sum(float(p.get_valor_total()) for p in parcelas_mes)
            
            fluxo.append({
                'mes': mes.strftime('%b/%Y'),
                'valor_previsto': valor_previsto,
                'parcelas_count': parcelas_mes.count()
            })
        
        return fluxo
    
    def get_chart_fluxo_caixa(self):
        """Gráfico de fluxo de caixa"""
        fluxo = self.get_fluxo_caixa()
        
        return {
            'type': 'line',
            'data': {
                'labels': [item['mes'] for item in fluxo],
                'datasets': [{
                    'label': 'Receita Prevista (R$)',
                    'data': [item['valor_previsto'] for item in fluxo],
                    'borderColor': '#28a745',
                    'backgroundColor': 'rgba(40, 167, 69, 0.1)',
                    'tension': 0.1,
                    'fill': True
                }]
            },
            'options': {
                'responsive': True,
                'scales': {
                    'y': {
                        'beginAtZero': True,
                        'ticks': {
                            'callback': 'function(value) { return "R$ " + value.toLocaleString(); }'
                        }
                    }
                },
                'plugins': {
                    'tooltip': {
                        'callbacks': {
                            'label': 'function(context) { return "R$ " + context.parsed.y.toLocaleString(); }'
                        }
                    }
                }
            }
        }
    
    def _calcular_total_recebido(self):
        """Calcular total recebido"""
        return ItemContrato.objects.filter(situacao='3').aggregate(
            Sum('valor_pago')
        )['valor_pago__sum'] or 0
    
    def _calcular_total_pendente(self):
        """Calcular total pendente"""
        parcelas_pendentes = ItemContrato.objects.filter(situacao='1')
        return sum(float(p.get_valor_pendente()) for p in parcelas_pendentes)
    
    def _calcular_inadimplencia_total(self):
        """Calcular total em inadimplência"""
        hoje = timezone.now().date()
        parcelas_vencidas = ItemContrato.objects.filter(
            situacao='1',
            data_vencimento__lt=hoje
        )
        return sum(float(p.get_valor_pendente()) for p in parcelas_vencidas)