from django.views.generic import TemplateView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.http import HttpResponse

class RelatorioListView(LoginRequiredMixin, TemplateView):
    template_name = 'relatorios/relatorio_list.html'

class RelatorioProjetosView(LoginRequiredMixin, TemplateView):
    template_name = 'relatorios/relatorio_projetos.html'
    
    def get(self, request, *args, **kwargs):
        return HttpResponse("Relatório de projetos - Em desenvolvimento")
    
class RelatorioCustomView(LoginRequiredMixin, TemplateView):
    template_name = 'relatorios/relatorio_custom.html'