from django.urls import reverse_lazy
from django.shortcuts import get_object_or_404
from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic import CreateView, DetailView, ListView, UpdateView
from ..models.requisicao import Requisicao
from ..models.ordem import Ordem
from ..forms.ordem_forms import OrdemForm

class OrdemCreateView(LoginRequiredMixin, CreateView):
    model = Ordem
    form_class = OrdemForm
    template_name = 'ordens/ordem_form.html'

    def form_valid(self, form):
        requisicao = get_object_or_404(Requisicao, pk=self.kwargs['requisicao_id'])
        form.instance.cod_requisicao = requisicao
        form.instance.created_by = self.request.user
        return super().form_valid(form)

    def get_success_url(self):
        return reverse_lazy('projetos:requisicao_detail', kwargs={'pk': self.kwargs['requisicao_id']})

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['requisicao'] = get_object_or_404(Requisicao, pk=self.kwargs['requisicao_id'])
        return context

class OrdemDetailView(LoginRequiredMixin, DetailView):
    model = Ordem
    template_name = 'ordens/ordem_detail.html'
    context_object_name = 'ordem'

class OrdemListView(LoginRequiredMixin, ListView):
    model = Ordem
    template_name = 'ordens/ordem_list.html'
    context_object_name = 'ordens'
    paginate_by = 10

    def get_queryset(self):
        requisicao_id = self.kwargs['requisicao_id']
        return Ordem.objects.filter(cod_requisicao_id=requisicao_id)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['requisicao'] = get_object_or_404(Requisicao, pk=self.kwargs['requisicao_id'])
        return context

class OrdemUpdateView(LoginRequiredMixin, UpdateView):
    model = Ordem
    form_class = OrdemForm
    template_name = 'ordens/ordem_form.html'

    def get_success_url(self):
        return reverse_lazy('projetos:ordem_detail', kwargs={'pk': self.object.pk})