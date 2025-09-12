from django.urls import path
from .views import projeto_views, requisicao_views, ordem_views

app_name = 'projetos'

urlpatterns = [
    # Projetos
    path('', projeto_views.ProjetoListView.as_view(), name='projeto_list'),
    path('create/', projeto_views.ProjetoCreateView.as_view(), name='projeto_create'),
    path('<int:pk>/', projeto_views.ProjetoDetailView.as_view(), name='projeto_detail'),
    path('<int:pk>/edit/', projeto_views.ProjetoUpdateView.as_view(), name='projeto_update'),
    path('<int:pk>/delete/', projeto_views.ProjetoDeleteView.as_view(), name='projeto_delete'),
    # Remover temporariamente a linha problemática:
    # path('<int:pk>/change-status/', projeto_views.ProjetoChangeStatusView.as_view(), name='projeto_change_status'),

    # Requisições
    path('<int:projeto_id>/requisicoes/', requisicao_views.RequisicaoListView.as_view(), name='requisicao_list'),
    path('<int:projeto_id>/requisicoes/create/', requisicao_views.RequisicaoCreateView.as_view(), name='requisicao_create'),
    path('requisicoes/<int:pk>/', requisicao_views.RequisicaoDetailView.as_view(), name='requisicao_detail'),
    path('requisicoes/<int:pk>/edit/', requisicao_views.RequisicaoUpdateView.as_view(), name='requisicao_update'),

    # Ordens
    path('requisicoes/<int:requisicao_id>/ordens/', ordem_views.OrdemListView.as_view(), name='ordem_list'),
    path('requisicoes/<int:requisicao_id>/ordens/create/', ordem_views.OrdemCreateView.as_view(), name='ordem_create'),
    path('ordens/<int:pk>/', ordem_views.OrdemDetailView.as_view(), name='ordem_detail'),
    path('ordens/<int:pk>/edit/', ordem_views.OrdemUpdateView.as_view(), name='ordem_update'),
    # Remover temporariamente as linhas problemáticas:
    # path('ordens/<int:pk>/iniciar/', ordem_views.OrdemIniciarView.as_view(), name='ordem_iniciar'),
    # path('ordens/<int:pk>/concluir/', ordem_views.OrdemConcluirView.as_view(), name='ordem_concluir'),
]
