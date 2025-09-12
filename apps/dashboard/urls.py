from django.urls import path
from .views import main_dashboard, analytics_views

app_name = 'dashboard'

urlpatterns = [
    path('', main_dashboard.DashboardView.as_view(), name='index'),
    path('analytics/financeiro/', analytics_views.FinanceiroAnalyticsView.as_view(), name='analytics_financeiro'),
    path('analytics/projetos/', analytics_views.ProjetosAnalyticsView.as_view(), name='analytics_projetos'),
    path('analytics/contratos/', analytics_views.ContratosAnalyticsView.as_view(), name='analytics_contratos'),
]