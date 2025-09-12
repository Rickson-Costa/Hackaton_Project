from django.urls import path
from .views import contrato_views

app_name = 'contratos'

urlpatterns = [
    # Contratos
    path('', contrato_views.ContratoListView.as_view(), name='contrato_list'),
    path('create/<int:ordem_id>/', contrato_views.ContratoCreateView.as_view(), name='contrato_create'),
    path('<str:pk>/', contrato_views.ContratoDetailView.as_view(), name='contrato_detail'),
    path('<str:pk>/edit/', contrato_views.ContratoUpdateView.as_view(), name='contrato_update'),
    # Remover temporariamente as linhas problemáticas:
    # path('<str:pk>/ativar/', contrato_views.ContratoAtivarView.as_view(), name='contrato_ativar'),
    # path('<str:pk>/finalizar/', contrato_views.ContratoFinalizarView.as_view(), name='contrato_finalizar'),
    # path('<str:contrato_id>/parcelas/', contrato_views.ParcelaListView.as_view(), name='parcela_list'),
    # path('parcelas/<str:contrato_id>/<int:lancamento_id>/pagar/', contrato_views.ParcelaPagarView.as_view(), name='parcela_pagar'),
    # path('parcelas/<str:contrato_id>/<int:lancamento_id>/liquidar/', contrato_views.ParcelaLiquidarView.as_view(), name='parcela_liquidar'),
    # path('prestadores/', contrato_views.PrestadorListView.as_view(), name='prestador_list'),
    # path('prestadores/create/', contrato_views.PrestadorCreateView.as_view(), name='prestador_create'),
    # path('prestadores/<int:pk>/', contrato_views.PrestadorDetailView.as_view(), name='prestador_detail'),
    # path('prestadores/<int:pk>/edit/', contrato_views.PrestadorUpdateView.as_view(), name='prestador_update'),
    # path('api/prestador-data/<str:cpf_cnpj>/', contrato_views.PrestadorDataAPIView.as_view(), name='api_prestador_data'),
    # path('api/calcular-impostos/', contrato_views.CalcularImpostosAPIView.as_view(), name='api_calcular_impostos'),
]