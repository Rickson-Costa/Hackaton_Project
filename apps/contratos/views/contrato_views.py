from django.urls import reverse_lazy
from django.shortcuts import get_object_or_404
from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic import ListView, DetailView, CreateView, UpdateView

from ..models.contrato import Contrato
from ..models.prestador import Prestador
from ..forms.contrato_forms import ContratoForm, PrestadorForm
from apps.projetos.models.ordem import Ordem


class ContratoListView(LoginRequiredMixin, ListView):
    model = Contrato
    template_name = 'contratos/contrato_list.html'
    context_object_name = 'contratos'
    paginate_by = 10
    ordering = ['-data_inicio', 'num_contrato']  # Fix UnorderedObjectListWarning

    def get_queryset(self):
        queryset = super().get_queryset()
        
        # Filtro por tipo de pessoa (PF/PJ)
        tipo_pessoa = self.request.GET.get('tipo_pessoa')
        if tipo_pessoa:
            queryset = queryset.filter(tipo_pessoa=tipo_pessoa)
        
        # Filtro por inadimplência
        inadimplencia = self.request.GET.get('inadimplencia')
        if inadimplencia == 'true':
            # Filtra contratos com parcelas vencidas
            from ..models.item_contrato import ItemContrato
            from django.utils import timezone
            
            contratos_inadimplentes = ItemContrato.objects.filter(
                situacao='1',  # Pendente
                data_vencimento__lt=timezone.now().date()
            ).values_list('num_contrato', flat=True)
            
            queryset = queryset.filter(num_contrato__in=contratos_inadimplentes)
        
        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        # Adiciona informações sobre filtros ativos
        context['tipo_pessoa_filtro'] = self.request.GET.get('tipo_pessoa')
        context['inadimplencia_filtro'] = self.request.GET.get('inadimplencia')
        
        # Labels para os filtros
        if context['tipo_pessoa_filtro'] == '1':
            context['filtro_label'] = 'Contratos Pessoa Física (PF)'
        elif context['tipo_pessoa_filtro'] == '2':
            context['filtro_label'] = 'Contratos Pessoa Jurídica (PJ)'
        elif context['inadimplencia_filtro'] == 'true':
            context['filtro_label'] = 'Contratos em Inadimplência'
        else:
            context['filtro_label'] = 'Todos os Contratos'
            
        return context

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
    


# Temporarily commented out until Prestador model is created
class PrestadorListView(LoginRequiredMixin, ListView):
    model = Prestador
    template_name = 'contratos/prestador_list.html'
    context_object_name = 'prestadores'
    paginate_by = 10

class PrestadorCreateView(LoginRequiredMixin, CreateView):
    model = Prestador
    form_class = PrestadorForm
    template_name = 'contratos/prestador_form.html'
    
    def get_success_url(self):
        return reverse_lazy('contratos:prestador_list')

class PrestadorUpdateView(LoginRequiredMixin, UpdateView):
    model = Prestador
    form_class = PrestadorForm
    template_name = 'contratos/prestador_form.html'
    
    def get_success_url(self):
        return reverse_lazy('contratos:prestador_detail', kwargs={'pk': self.object.pk})

class PrestadorDetailView(LoginRequiredMixin, DetailView):
    model = Prestador
    template_name = 'contratos/prestador_detail.html'
    context_object_name = 'prestador'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        prestador = self.get_object()
        # context['contratos'] = Contrato.objects.filter(cpf_cnpj=prestador.cpf_cnpj)  # Temporarily disabled
        return context
