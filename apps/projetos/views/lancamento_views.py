from django.shortcuts import get_object_or_404
from django.urls import reverse_lazy
from django.views.generic import CreateView, DeleteView
from ..models import Projeto, LancamentoCusto
from ..forms.lancamento_forms import LancamentoCustoForm

class LancamentoCustoCreateView(CreateView):
    model = LancamentoCusto
    form_class = LancamentoCustoForm
    template_name = 'projetos/lancamento_form.html'

    def form_valid(self, form):
        projeto = get_object_or_404(Projeto, pk=self.kwargs['projeto_pk'])
        form.instance.projeto = projeto
        return super().form_valid(form)

    def get_success_url(self):
        return reverse_lazy('projetos:projeto_detail', kwargs={'pk': self.kwargs['projeto_pk']})

class LancamentoCustoDeleteView(DeleteView):
    model = LancamentoCusto
    template_name = 'projetos/lancamento_confirm_delete.html'
    
    def get_success_url(self):
        return reverse_lazy('projetos:projeto_detail', kwargs={'pk': self.object.projeto.pk})
