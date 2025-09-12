from django.shortcuts import get_object_or_404, redirect
from django.views import View
from django.contrib import messages
from ..models.item_contrato import ItemContrato
from decimal import Decimal
from django.urls import reverse_lazy
from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic import ListView, CreateView
from ..forms.pagamento_forms import ItemContratoForm
from ..models.contrato import Contrato


class ParcelaListView(LoginRequiredMixin, ListView):
    model = ItemContrato
    template_name = 'contratos/parcela_list.html'
    context_object_name = 'parcelas'
    paginate_by = 15

    def get_queryset(self):
        # Apenas um exemplo para listar todas as parcelas.
        # Pode ser filtrado por status, data, etc. no futuro.
        return ItemContrato.objects.select_related('num_contrato').all().order_by('data_vencimento')


class ItemContratoCreateView(LoginRequiredMixin, CreateView):
    model = ItemContrato
    form_class = ItemContratoForm
    template_name = 'contratos/itemcontrato_form.html'

    def dispatch(self, request, *args, **kwargs):
        self.contrato = get_object_or_404(Contrato, pk=self.kwargs['contrato_pk'])
        projeto = self.contrato.cod_ordem.cod_requisicao.cod_projeto
        
        if not projeto.marcos.filter(status='aprovado').exists():
            messages.error(request, "Não é possível criar parcelas sem um marco de projeto aprovado.")
            return redirect('contratos:contrato_detail', pk=self.contrato.pk)
            
        return super().dispatch(request, *args, **kwargs)

    def form_valid(self, form):
        form.instance.num_contrato = self.contrato
        return super().form_valid(form)

    def get_success_url(self):
        return reverse_lazy('contratos:contrato_detail', kwargs={'pk': self.contrato.pk})


class RegistrarPagamentoView(View):
    def post(self, request, *args, **kwargs):
        parcela = get_object_or_404(ItemContrato, pk=self.kwargs['parcela_pk'])
        valor_pago_str = request.POST.get('valor_pago')

        if not valor_pago_str:
            messages.error(request, "O valor pago é obrigatório.")
            return redirect('contratos:contrato_detail', pk=parcela.num_contrato.pk)

        try:
            valor_pago = Decimal(valor_pago_str)
        except:
            messages.error(request, "Valor pago inválido.")
            return redirect('contratos:contrato_detail', pk=parcela.num_contrato.pk)

        if valor_pago <= 0:
            messages.error(request, "O valor pago deve ser maior que zero.")
            return redirect('contratos:contrato_detail', pk=parcela.num_contrato.pk)

        parcela.valor_pago += valor_pago
        
        if parcela.valor_pago >= parcela.valor_parcela:
            parcela.status = '3' # Paga
            parcela.valor_pago = parcela.valor_parcela # Evita pagar a mais
        elif parcela.valor_pago > 0:
            parcela.status = '4' # Parcialmente Paga
        
        parcela.save()

        messages.success(request, "Pagamento registrado com sucesso.")
        return redirect('contratos:contrato_detail', pk=parcela.num_contrato.pk)
