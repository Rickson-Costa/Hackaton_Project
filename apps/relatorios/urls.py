from django.urls import path
from .views import report_views

app_name = 'relatorios'

urlpatterns = [
    path('', report_views.RelatorioListView.as_view(), name='relatorio_list'),
    
    # Relatórios de Projetos
    path('projetos/', report_views.RelatorioProjetosView.as_view(), name='relatorio_projetos'),
    path('projetos/generate/', report_views.RelatorioProjetosGenerateView.as_view(), name='relatorio_projetos_generate'),
    
    # Relatórios de Contratos
    path('contratos/', report_views.RelatorioContratosView.as_view(), name='relatorio_contratos'),
    path('contratos/generate/', report_views.RelatorioContratosGenerateView.as_view(), name='relatorio_contratos_generate'),
    
    # Relatórios Financeiros
    path('financeiro/', report_views.RelatorioFinanceiroView.as_view(), name='relatorio_financeiro'),
    path('financeiro/generate/', report_views.RelatorioFinanceiroGenerateView.as_view(), name='relatorio_financeiro_generate'),
    
    # Relatórios Personalizados
    path('custom/', report_views.RelatorioCustomView.as_view(), name='relatorio_custom'),
    path('custom/generate/', report_views.RelatorioCustomGenerateView.as_view(), name='relatorio_custom_generate'),
]
