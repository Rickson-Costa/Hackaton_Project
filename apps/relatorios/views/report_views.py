from django.views.generic import TemplateView
from django.views import View
from django.contrib.auth.mixins import LoginRequiredMixin
from django.http import HttpResponse
from django.http import HttpResponse
from django.template.loader import get_template
from xhtml2pdf import pisa
import io

from apps.projetos.models.projeto import Projeto
from apps.contratos.models.contrato import Contrato
from django.db import models

class RelatorioProjetosPDFView(LoginRequiredMixin, View):
    def get(self, request):
        # Buscar dados
        projetos = Projeto.objects.all()
        
        # Renderizar template
        template = get_template('relatorios/projetos_pdf.html')
        html = template.render({'projetos': projetos})
        
        # Gerar PDF
        result = io.BytesIO()
        pdf = pisa.pisaDocument(io.BytesIO(html.encode("UTF-8")), result)
        
        if not pdf.err:
            response = HttpResponse(result.getvalue(), content_type='application/pdf')
            response['Content-Disposition'] = 'attachment; filename="projetos.pdf"'
            return response
        return HttpResponse('Erro ao gerar PDF')

class RelatorioContratosView(LoginRequiredMixin, TemplateView):
    template_name = 'relatorios/contratos.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['contratos'] = Contrato.objects.all()
        context['total_contratos'] = Contrato.objects.count()
        context['valor_total'] = Contrato.objects.aggregate(
            total=models.Sum('valor')
        )['total'] or 0
        return context
    
class RelatorioListView(LoginRequiredMixin, TemplateView):
    template_name = 'relatorios/relatorio_list.html'

class RelatorioProjetosView(LoginRequiredMixin, TemplateView):
    template_name = 'relatorios/relatorio_projetos.html'
    
    def get(self, request, *args, **kwargs):
        return HttpResponse("Relatório de projetos - Em desenvolvimento")
    
class RelatorioCustomView(LoginRequiredMixin, TemplateView):
    template_name = 'relatorios/relatorio_custom.html'