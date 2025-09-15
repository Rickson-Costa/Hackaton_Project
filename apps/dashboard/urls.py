from django.urls import path
from .views import main_dashboard, analytics_views

app_name = 'dashboard'

urlpatterns = [
    path('', main_dashboard.DashboardView.as_view(), name='index'),
     path('analytics/financeiro/', analytics_views.FinanceiroAnalyticsView.as_view(), name='analytics_financeiro'),
    # Comentar temporariamente as URLs problemáticas:
    path('analytics/projetos/', analytics_views.ProjetosAnalyticsView.as_view(), name='analytics_projetos'),
    path('analytics/contratos/', analytics_views.ContratosAnalyticsView.as_view(), name='analytics_contratos'),
    # path('analytics/financeiro/', analytics_views.FinanceiroAnalyticsView.as_view(), name='analytics_financeiro'),
    # path('api/chart-data/projetos/', analytics_views.ProjetosChartDataView.as_view(), name='chart_data_projetos'),
    # path('api/chart-data/contratos/', analytics_views.ContratosChartDataView.as_view(), name='chart_data_contratos'),
    # path('api/chart-data/financeiro/', analytics_views.FinanceiroChartDataView.as_view(), name='chart_data_financeiro'),
    # path('widget/projeto-status/<int:projeto_id>/', main_dashboard.ProjetoStatusWidget.as_view(), name='widget_projeto_status'),
    # path('widget/alertas/', main_dashboard.AlertasWidget.as_view(), name='widget_alertas'),
]
