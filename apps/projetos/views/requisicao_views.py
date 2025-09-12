from django.urls import reverse_lazy
from django.shortcuts import get_object_or_404
from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic import ListView, DetailView, CreateView, UpdateView
from ..models.projeto import Projeto
from ..models.requisicao import Requisicao
from ..forms.requisicao_forms import RequisicaoForm

class RequisicaoCreateView(LoginRequiredMixin, CreateView):
    model = Requisicao
    form_class = RequisicaoForm
    template_name = 'requisicoes/requisicao_form.html'

    def form_valid(self, form):
        projeto = get_object_or_404(Projeto, pk=self.kwargs['projeto_id'])
        form.instance.cod_projeto = projeto
        form.instance.created_by = self.request.user
        return super().form_valid(form)

    def get_success_url(self):
        return reverse_lazy('projetos:projeto_detail', kwargs={'pk': self.kwargs['projeto_id']})
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['projeto'] = get_object_or_404(Projeto, pk=self.kwargs['projeto_id'])
        return context

class RequisicaoDetailView(LoginRequiredMixin, DetailView):
    model = Requisicao
    template_name = 'requisicoes/requisicao_detail.html'
    context_object_name = 'requisicao'

class RequisicaoListView(LoginRequiredMixin, ListView):
    model = Requisicao
    template_name = 'requisicoes/requisicao_list.html'
    context_object_name = 'requisicoes'
    paginate_by = 10

    def get_queryset(self):
        projeto_id = self.kwargs['projeto_id']
        return Requisicao.objects.filter(cod_projeto_id=projeto_id)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['projeto'] = get_object_or_404(Projeto, pk=self.kwargs['projeto_id'])
        return context

class RequisicaoUpdateView(LoginRequiredMixin, UpdateView):
    model = Requisicao
    form_class = RequisicaoForm
    template_name = 'requisicoes/requisicao_form.html'

    def get_success_url(self):
        return reverse_lazy('projetos:requisicao_detail', kwargs={'pk': self.object.pk})