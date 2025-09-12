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
        """Retorna dict {1..12: valor}. Inicialmente zerado; depois você integra com seus modelos."""
        ano = ano or self.hoje.year
        data = self._meses_zero()

        # TODO: integrar com seus modelos reais (ex.: Lancamento/Parcela/Pagamento).
        # Exemplo (ajuste aos seus nomes de modelo/campos):
        # from django.db.models import Sum
        # from django.db.models.functions import ExtractMonth
        # from django.apps import apps
        # Lancamento = apps.get_model('contratos', 'Lancamento')
        # qs = (Lancamento.objects
        #       .filter(tipo='receita', data_pagamento__year=ano, status='pago')
        #       .values(m=ExtractMonth('data_pagamento'))
        #       .annotate(total=Sum('valor')))
        # for row in qs:
        #     data[row['m']] = float(row['total'] or 0)
        return data

    def get_despesas_por_mes(self, ano=None):
        ano = ano or self.hoje.year
        data = self._meses_zero()
        # TODO: idem ao de cima, mas com tipo='despesa'
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
