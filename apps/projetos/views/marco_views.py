from django.shortcuts import get_object_or_404
from django.urls import reverse_lazy
from django.views.generic import CreateView, UpdateView
from ..models import Projeto, MarcoProjeto
from ..forms.marco_forms import MarcoProjetoForm

class MarcoProjetoCreateView(CreateView):
    model = MarcoProjeto
    form_class = MarcoProjetoForm
    template_name = 'projetos/marco_form.html'

    def form_valid(self, form):
        projeto = get_object_or_404(Projeto, pk=self.kwargs['projeto_pk'])
        form.instance.projeto = projeto
        return super().form_valid(form)

    def get_success_url(self):
        return reverse_lazy('projetos:projeto_detail', kwargs={'pk': self.kwargs['projeto_pk']})

class MarcoProjetoUpdateStatusView(UpdateView):
    model = MarcoProjeto
    fields = ['status']
    template_name = 'projetos/marco_update_status.html'

    def get_success_url(self):
        return reverse_lazy('projetos:projeto-detail', kwargs={'pk': self.object.projeto.pk})
