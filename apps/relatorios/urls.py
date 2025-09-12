from django.urls import path
from .views import report_views

app_name = 'relatorios'

urlpatterns = [
    path('', report_views.RelatorioListView.as_view(), name='relatorio_list'),
    path('projetos/', report_views.RelatorioProjetosView.as_view(), name='relatorio_projetos'),
    # Comentar temporariamente as URLs problemáticas:
    # path('projetos/pdf/', report_views.RelatorioProjetosPDFView.as_view(), name='relatorio_projetos_pdf'),
    # path('projetos/excel/', report_views.RelatorioProjetosExcelView.as_view(), name='relatorio_projetos_excel'),
    # path('contratos/', report_views.RelatorioContratosView.as_view(), name='relatorio_contratos'),
    # path('contratos/pdf/', report_views.RelatorioContratosPDFView.as_view(), name='relatorio_contratos_pdf'),
    # path('contratos/inadimplencia/', report_views.RelatorioInadimplenciaView.as_view(), name='relatorio_inadimplencia'),
    # path('financeiro/', report_views.RelatorioFinanceiroView.as_view(), name='relatorio_financeiro'),
    # path('financeiro/pdf/', report_views.RelatorioFinanceiroPDFView.as_view(), name='relatorio_financeiro_pdf'),
    # path('custom/', report_views.RelatorioCustomView.as_view(), name='relatorio_custom'),
    # path('custom/generate/', report_views.RelatorioCustomGenerateView.as_view(), name='relatorio_custom_generate'),
]
