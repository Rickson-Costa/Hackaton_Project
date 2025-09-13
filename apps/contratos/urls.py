from django.urls import path
from .views import contrato_views, pagamento_views

app_name = 'contratos'

# apps/contratos/urls.py
from django.urls import path
from .views import contrato_views, pagamento_views

app_name = 'contratos'

urlpatterns = [
    # URLs de Contrato
    path('', contrato_views.ContratoListView.as_view(), name='contrato_list'),
    path('create/<int:ordem_id>/', contrato_views.ContratoCreateView.as_view(), name='contrato_create'),
    path('<str:pk>/', contrato_views.ContratoDetailView.as_view(), name='contrato_detail'),
    path('<str:pk>/edit/', contrato_views.ContratoUpdateView.as_view(), name='contrato_update'),
    #path('<str:pk>/delete/', contrato_views.ContratoDeleteView.as_view(), name='contrato_delete'),
    #path('<str:pk>/ativar/', contrato_views.ContratoAtivarView.as_view(), name='contrato_ativar'),
    #path('<str:pk>/finalizar/', contrato_views.ContratoFinalizarView.as_view(), name='contrato_finalizar'),
    
    # URLs de Parcelas/Itens de Contrato
    path('parcelas/', pagamento_views.ParcelaListView.as_view(), name='parcela_list'),
    path('<str:contrato_pk>/parcelas/adicionar/', pagamento_views.ItemContratoCreateView.as_view(), name='itemcontrato-create'),
    path('parcelas/<int:parcela_pk>/registrar-pagamento/', pagamento_views.RegistrarPagamentoView.as_view(), name='registrar-pagamento'),
    
    # APIs e ações em lote
    path('api/parcela/<int:parcela_id>/', pagamento_views.ParcelaDetailAPIView.as_view(), name='api_parcela_detail'),
    path('parcelas/lote/pagar/', pagamento_views.PagamentoLoteView.as_view(), name='pagamento_lote'),
    path('parcelas/lote/adiar/', pagamento_views.AdiarParcelasView.as_view(), name='adiar_lote'),
    
    # Relatórios
    path('relatorio/inadimplencia/', pagamento_views.RelatorioInadimplenciaView.as_view(), name='relatorio_inadimplencia'),
    #path('export/', contrato_views.ContratoExportView.as_view(), name='contrato_export'),
    
    # Pagamento rápido
    #path('quick-pay/', contrato_views.QuickPayView.as_view(), name='quick_pay'),
]