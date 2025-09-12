# apps/projetos/views/projeto_views.py
from django.urls import reverse_lazy
from django.contrib.auth.mixins import LoginRequiredMixin, PermissionRequiredMixin
from django.views.generic import ListView, DetailView, CreateView, UpdateView, DeleteView
from ..models.projeto import Projeto
from ..forms.projeto_forms import ProjetoForm

class ProjetoListView(LoginRequiredMixin, ListView):
    """
    View para listar todos os projetos.
    """
    model = Projeto
    template_name = 'projetos/projeto_list.html' # <-- Precisaremos criar este template
    context_object_name = 'projetos'
    paginate_by = 10

class ProjetoDetailView(LoginRequiredMixin, DetailView):
    """
    View para ver os detalhes de um projeto específico.
    """
    model = Projeto
    template_name = 'projetos/projeto_detail.html' # <-- Precisaremos criar este template
    context_object_name = 'projeto'

class ProjetoCreateView(LoginRequiredMixin, PermissionRequiredMixin, CreateView):
    """
    View para criar um novo projeto.
    """
    model = Projeto
    form_class = ProjetoForm
    template_name = 'projetos/projeto_form.html' # <-- Precisaremos criar este template
    success_url = reverse_lazy('projetos:projeto_list')
    permission_required = 'projetos.add_projeto'

    def form_valid(self, form):
        form.instance.created_by = self.request.user
        return super().form_valid(form)

class ProjetoUpdateView(LoginRequiredMixin, PermissionRequiredMixin, UpdateView):
    """
    View para editar um projeto existente.
    """
    model = Projeto
    form_class = ProjetoForm
    template_name = 'projetos/projeto_form.html' # Reutiliza o mesmo template do Create
    success_url = reverse_lazy('projetos:projeto_list')
    permission_required = 'projetos.change_projeto'

    def form_valid(self, form):
        form.instance.updated_by = self.request.user
        return super().form_valid(form)

class ProjetoDeleteView(LoginRequiredMixin, PermissionRequiredMixin, DeleteView):
    """
    View para deletar um projeto.
    """
    model = Projeto
    template_name = 'projetos/projeto_confirm_delete.html' # <-- Precisaremos criar este template
    success_url = reverse_lazy('projetos:projeto_list')
    permission_required = 'projetos.delete_projeto'

# As outras views (ChangeStatus, etc.) podem ser adicionadas aqui depois.