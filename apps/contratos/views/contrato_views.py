from django.urls import reverse_lazy
from django.shortcuts import get_object_or_404
from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic import ListView, DetailView, CreateView, UpdateView

from ..models.contrato import Contrato, Prestador
from ..forms.contrato_forms import ContratoForm
from apps.projetos.models.ordem import Ordem
from ..models.item_contrato import ItemContrato

class ContratoListView(LoginRequiredMixin, ListView):
    model = Contrato
    template_name = 'contratos/contrato_list.html'
    context_object_name = 'contratos'
    paginate_by = 10

class ContratoDetailView(LoginRequiredMixin, DetailView):
    model = Contrato
    template_name = 'contratos/contrato_detail.html'
    context_object_name = 'contrato'

class ContratoCreateView(LoginRequiredMixin, CreateView):
    model = Contrato
    form_class = ContratoForm
    template_name = 'contratos/contrato_form.html'

    def form_valid(self, form):
        # Associa a Ordem de Serviço que veio da URL
        ordem = get_object_or_404(Ordem, pk=self.kwargs['ordem_id'])
        form.instance.cod_ordem = ordem
        
        # Gera o número do contrato automaticamente
        form.instance.num_contrato = Contrato.gerar_numero_contrato()
        
        # Associa o usuário que criou
        form.instance.created_by = self.request.user
        
        return super().form_valid(form)

    def get_context_data(self, **kwargs):
        # Envia a Ordem para o template para podermos exibir suas informações
        context = super().get_context_data(**kwargs)
        context['ordem'] = get_object_or_404(Ordem, pk=self.kwargs['ordem_id'])
        return context

    def get_success_url(self):
        # Redireciona para a página de detalhes do contrato recém-criado
        return reverse_lazy('contratos:contrato_detail', kwargs={'pk': self.object.pk})

class ContratoUpdateView(LoginRequiredMixin, UpdateView):
    model = Contrato
    form_class = ContratoForm
    template_name = 'contratos/contrato_form.html'

    def get_success_url(self):
        return reverse_lazy('contratos:contrato_detail', kwargs={'pk': self.object.pk})
    


class PrestadorListView(LoginRequiredMixin, ListView):
    model = Prestador
    template_name = 'contratos/prestador_list.html'
    context_object_name = 'prestadores'
    paginate_by = 10

class PrestadorDetailView(LoginRequiredMixin, DetailView):
    model = Prestador
    template_name = 'contratos/prestador_detail.html'
    context_object_name = 'prestador'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        prestador = self.get_object()
        context['contratos'] = Contrato.objects.filter(cpf_cnpj=prestador.cpf_cnpj)
        return context

class ParcelaListView(LoginRequiredMixin, ListView):
    model = ItemContrato
    template_name = 'contratos/parcela_list.html'
    context_object_name = 'parcelas'
    paginate_by = 15

    def get_queryset(self):
        # Apenas um exemplo para listar todas as parcelas.
        # Pode ser filtrado por status, data, etc. no futuro.
        return ItemContrato.objects.select_related('num_contrato').all().order_by('data_vencimento')