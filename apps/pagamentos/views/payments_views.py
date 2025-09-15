from django.http import HttpResponse
from django.views.generic import TemplateView, ListView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.db.models import Sum, Q
from django.db.models.functions import Extract, TruncMonth
from django.utils import timezone
from apps.contratos.models.item_contrato import ItemContrato

class CreatePaymentView(LoginRequiredMixin, TemplateView):
    def get(self, request, *args, **kwargs):
        return HttpResponse("Criar pagamento - Em desenvolvimento")

class PaymentSuccessView(TemplateView):
    def get(self, request, *args, **kwargs):
        return HttpResponse("Pagamento realizado com sucesso!")

class PaymentFailureView(TemplateView):
    def get(self, request, *args, **kwargs):
        return HttpResponse("Falha no pagamento.")

class PaymentPendingView(TemplateView):
    def get(self, request, *args, **kwargs):
        return HttpResponse("Pagamento pendente.")

class PaymentHistoryView(LoginRequiredMixin, TemplateView):
    template_name = 'pagamentos/payment_history.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        # Filtros da URL
        year_filter = self.request.GET.get('year')
        month_filter = self.request.GET.get('month')
        contrato_filter = self.request.GET.get('contrato')
        
        # Base queryset - parcelas com pagamentos
        payments = ItemContrato.objects.filter(
            valor_pago__gt=0,
            data_pagamento__isnull=False
        ).select_related('num_contrato').order_by('-data_pagamento')
        
        # Aplicar filtros
        if year_filter:
            payments = payments.filter(data_pagamento__year=year_filter)
        if month_filter:
            payments = payments.filter(data_pagamento__month=month_filter)
        if contrato_filter:
            payments = payments.filter(num_contrato__id=contrato_filter)
        
        # Resumos estatísticos
        total_payments = payments.aggregate(
            total_valor=Sum('valor_pago'),
            count=Sum('id') / Sum('id')  # Trick to count
        )
        
        # Resumo por mês (últimos 12 meses)
        monthly_summary = ItemContrato.objects.filter(
            valor_pago__gt=0,
            data_pagamento__isnull=False,
            data_pagamento__year=timezone.now().year
        ).values(
            month=Extract('data_pagamento', 'month')
        ).annotate(
            total=Sum('valor_pago'),
            count=Sum('id') / Sum('id')
        ).order_by('month')
        
        # Contratos únicos para filtro
        contratos_com_pagamentos = ItemContrato.objects.filter(
            valor_pago__gt=0
        ).values_list('num_contrato', 'num_contrato__num_contrato').distinct()
        
        # Pagamentos com paginação (últimos 50)
        recent_payments = payments[:50]
        
        # Calcular média mensal
        total_valor = total_payments.get('total_valor', 0) or 0
        media_mensal = total_valor / 12 if total_valor > 0 else 0
        
        context.update({
            'payments': recent_payments,
            'total_valor': total_valor,
            'media_mensal': media_mensal,
            'total_count': payments.count(),
            'monthly_summary': monthly_summary,
            'contratos_options': contratos_com_pagamentos,
            'year_filter': year_filter,
            'month_filter': month_filter,
            'contrato_filter': contrato_filter,
            'current_year': timezone.now().year,
            'months': [
                (1, 'Janeiro'), (2, 'Fevereiro'), (3, 'Março'),
                (4, 'Abril'), (5, 'Maio'), (6, 'Junho'),
                (7, 'Julho'), (8, 'Agosto'), (9, 'Setembro'),
                (10, 'Outubro'), (11, 'Novembro'), (12, 'Dezembro')
            ]
        })
        
        return context