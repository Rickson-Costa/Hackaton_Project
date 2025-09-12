from django.http import HttpResponse
from django.views.generic import TemplateView
from django.contrib.auth.mixins import LoginRequiredMixin

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
    def get(self, request, *args, **kwargs):
        return HttpResponse("Histórico de pagamentos - Em desenvolvimento")