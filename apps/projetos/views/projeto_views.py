# apps/projetos/views/projeto_views.py
from django.urls import reverse_lazy
from django.contrib.auth.mixins import LoginRequiredMixin, PermissionRequiredMixin
from django.contrib import messages
from django.contrib.messages.views import SuccessMessageMixin
from django.views.generic import ListView, DetailView, CreateView, UpdateView, DeleteView
from ..models.projeto import Projeto
from ..forms.projeto_forms import ProjetoForm

class ProjetoListView(LoginRequiredMixin, ListView):
    """
    View para listar todos os projetos.
    """
    model = Projeto
    template_name = 'projetos/projeto_list.html'
    context_object_name = 'projetos'
    paginate_by = 10

class ProjetoDetailView(LoginRequiredMixin, DetailView):
    """
    View para ver os detalhes de um projeto específico.
    """
    model = Projeto
    template_name = 'projetos/projeto_detail.html'
    context_object_name = 'projeto'

class ProjetoCreateView(LoginRequiredMixin, SuccessMessageMixin, CreateView):
    """
    View para criar um novo projeto.
    """
    model = Projeto
    form_class = ProjetoForm
    template_name = 'projetos/projeto_form.html'
    success_message = "Projeto criado com sucesso!"

    def get_success_url(self):
        return reverse_lazy('projetos:projeto_detail', kwargs={'pk': self.object.pk})

    def form_valid(self, form):
        # Remove created_by pois não existe no modelo
        return super().form_valid(form)

    def form_invalid(self, form):
        messages.error(self.request, "Erro ao criar o projeto. Verifique os campos abaixo.")
        return super().form_invalid(form)

class ProjetoUpdateView(LoginRequiredMixin, PermissionRequiredMixin, SuccessMessageMixin, UpdateView):
    """
    View para editar um projeto existente.
    """
    model = Projeto
    form_class = ProjetoForm
    template_name = 'projetos/projeto_form.html'
    success_message = "Projeto atualizado com sucesso!"
    permission_required = 'projetos.change_projeto'

    def get_success_url(self):
        return reverse_lazy('projetos:projeto_detail', kwargs={'pk': self.object.pk})

    def form_valid(self, form):
        # Remove updated_by pois não existe no modelo
        return super().form_valid(form)

    def form_invalid(self, form):
        messages.error(self.request, "Erro ao atualizar o projeto. Verifique os campos abaixo.")
        return super().form_invalid(form)

class ProjetoDeleteView(LoginRequiredMixin, PermissionRequiredMixin, SuccessMessageMixin, DeleteView):
    """
    View para deletar um projeto.
    """
    model = Projeto
    template_name = 'projetos/projeto_confirm_delete.html'
    success_url = reverse_lazy('projetos:projeto_list')
    success_message = "Projeto deletado com sucesso!"
    permission_required = 'projetos.delete_projeto'

# As outras views (ChangeStatus, etc.) podem ser adicionadas aqui depois.
