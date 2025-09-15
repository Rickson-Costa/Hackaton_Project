# apps/dashboard/services/financeiro_analytics.py
from calendar import monthrange
from django.utils import timezone

class FinanceiroAnalyticsService:
    """Service de analytics financeiro. Implementação mínima para não quebrar a view."""

    def __init__(self, hoje=None):
        self.hoje = hoje or timezone.now().date()

    def _meses_zero(self):
        # {1: 0, 2: 0, ..., 12: 0}
        return {m: 0 for m in range(1, 12 + 1)}

    def get_receitas_por_mes(self, ano=None):
        """Retorna dict {1..12: valor} baseado nos pagamentos de contratos."""
        ano = ano or self.hoje.year
        data = self._meses_zero()

        # Integrado com ItemContrato (parcelas pagas)
        from django.db.models import Sum
        from django.db.models.functions import ExtractMonth
        from django.apps import apps
        
        ItemContrato = apps.get_model('contratos', 'ItemContrato')
        qs = (ItemContrato.objects
              .filter(data_pagamento__year=ano, valor_pago__gt=0)
              .values(m=ExtractMonth('data_pagamento'))
              .annotate(total=Sum('valor_pago')))
        
        for row in qs:
            data[row['m']] = float(row['total'] or 0)
            
        return data

    def get_despesas_por_mes(self, ano=None):
        """Retorna dict {1..12: valor} baseado nas despesas."""
        ano = ano or self.hoje.year
        data = self._meses_zero()
        
        # Por enquanto, usando 0 para despesas - pode ser expandido no futuro
        # com modelos específicos de despesas quando implementados
        return data

    def get_resumo_financeiro(self, ano=None):
        """Totais simples para cards do dashboard."""
        ano = ano or self.hoje.year
        total_receitas = sum(self.get_receitas_por_mes(ano).values())
        total_despesas = sum(self.get_despesas_por_mes(ano).values())
        saldo = total_receitas - total_despesas
        return {
            'ano': ano,
            'total_receitas': total_receitas,
            'total_despesas': total_despesas,
            'saldo': saldo,
        }

    def get_periodo_mes(self, ano, mes):
        """Útil se for consolidar manualmente por mês."""
        from datetime import date
        _, last_day = monthrange(ano, mes)
        return date(ano, mes, 1), date(ano, mes, last_day)
    
    def get_fluxo_caixa(self, ano=None):
        """Retorna dados de fluxo de caixa para exibição."""
        ano = ano or self.hoje.year
        receitas = self.get_receitas_por_mes(ano)
        despesas = self.get_despesas_por_mes(ano)
        
        saldo_acumulado = 0
        fluxo = []
        
        for mes in range(1, 13):
            receita = receitas[mes]
            despesa = despesas[mes]
            saldo_mes = receita - despesa
            saldo_acumulado += saldo_mes
            
            fluxo.append({
                'mes': mes,
                'receita': receita,
                'despesa': despesa,
                'saldo_mes': saldo_mes,
                'saldo_acumulado': saldo_acumulado
            })
        
        return fluxo
    
    def get_impostos_retidos(self, ano=None):
        """Calcula impostos retidos baseado nos pagamentos."""
        ano = ano or self.hoje.year
        total_receitas = sum(self.get_receitas_por_mes(ano).values())
        
        # Estimativas de impostos (pode ser customizado conforme regras específicas)
        estimativas = {
            'irrf': total_receitas * 0.015,  # 1.5% IRRF
            'iss': total_receitas * 0.02,    # 2% ISS estimado
            'inss': total_receitas * 0.11,   # 11% INSS
            'total': 0
        }
        estimativas['total'] = sum([estimativas['irrf'], estimativas['iss'], estimativas['inss']])
        
        return estimativas
    
    # Métodos para gráficos (Chart.js)
    def get_chart_fluxo_caixa(self, ano=None):
        """Dados formatados para gráfico de fluxo de caixa."""
        fluxo = self.get_fluxo_caixa(ano)
        meses = ['Jan', 'Fev', 'Mar', 'Abr', 'Mai', 'Jun', 
                'Jul', 'Ago', 'Set', 'Out', 'Nov', 'Dez']
        
        return {
            'labels': meses,
            'datasets': [
                {
                    'label': 'Receitas',
                    'data': [item['receita'] for item in fluxo],
                    'backgroundColor': 'rgba(40, 167, 69, 0.8)',
                    'borderColor': 'rgba(40, 167, 69, 1)',
                    'borderWidth': 2
                },
                {
                    'label': 'Despesas',
                    'data': [item['despesa'] for item in fluxo],
                    'backgroundColor': 'rgba(220, 53, 69, 0.8)',
                    'borderColor': 'rgba(220, 53, 69, 1)',
                    'borderWidth': 2
                }
            ]
        }
    
    def get_chart_receitas(self, ano=None):
        """Dados formatados para gráfico de receitas mensais."""
        receitas = self.get_receitas_por_mes(ano)
        meses = ['Jan', 'Fev', 'Mar', 'Abr', 'Mai', 'Jun', 
                'Jul', 'Ago', 'Set', 'Out', 'Nov', 'Dez']
        
        return {
            'labels': meses,
            'datasets': [{
                'label': 'Receitas Mensais',
                'data': [receitas[mes] for mes in range(1, 13)],
                'backgroundColor': [
                    'rgba(54, 162, 235, 0.8)',
                    'rgba(255, 99, 132, 0.8)',
                    'rgba(255, 205, 86, 0.8)',
                    'rgba(75, 192, 192, 0.8)',
                    'rgba(153, 102, 255, 0.8)',
                    'rgba(255, 159, 64, 0.8)',
                    'rgba(199, 199, 199, 0.8)',
                    'rgba(83, 102, 255, 0.8)',
                    'rgba(255, 99, 255, 0.8)',
                    'rgba(99, 255, 132, 0.8)',
                    'rgba(255, 162, 99, 0.8)',
                    'rgba(162, 99, 255, 0.8)'
                ],
                'borderWidth': 1
            }]
        }
    
    def get_chart_inadimplencia(self, ano=None):
        """Dados para gráfico de inadimplência."""
        from django.apps import apps
        from django.utils import timezone
        from django.db.models import Q
        
        ItemContrato = apps.get_model('contratos', 'ItemContrato')
        hoje = timezone.now().date()
        
        # Parcelas vencidas e não pagas (inadimplentes)
        vencidas = ItemContrato.objects.filter(
            data_vencimento__lt=hoje,
            valor_pago=0
        ).count()
        
        # Parcelas em dia (não vencidas OU já pagas, mas sem dupla contagem)
        em_dia = ItemContrato.objects.filter(
            Q(data_vencimento__gte=hoje) | Q(valor_pago__gt=0)
        ).distinct().count()
        
        return {
            'labels': ['Em Dia', 'Vencidas'],
            'datasets': [{
                'data': [em_dia, vencidas],
                'backgroundColor': [
                    'rgba(40, 167, 69, 0.8)',
                    'rgba(220, 53, 69, 0.8)'
                ]
            }]
        }
    
    def get_chart_impostos(self, ano=None):
        """Dados para gráfico de impostos retidos."""
        impostos = self.get_impostos_retidos(ano)
        
        return {
            'labels': ['IRRF', 'ISS', 'INSS'],
            'datasets': [{
                'data': [impostos['irrf'], impostos['iss'], impostos['inss']],
                'backgroundColor': [
                    'rgba(255, 193, 7, 0.8)',
                    'rgba(0, 123, 255, 0.8)',
                    'rgba(108, 117, 125, 0.8)'
                ]
            }]
        }
