from django.urls import path
from .views import (
    ClienteListView,
    ClienteDetailView,
    ClienteCreateView,
    ClienteUpdateView,
    ClienteDeleteView,
)

app_name = 'clientes'

urlpatterns = [
    path('', ClienteListView.as_view(), name='cliente-list'),
    path('<int:pk>/', ClienteDetailView.as_view(), name='cliente-detail'),
    path('adicionar/', ClienteCreateView.as_view(), name='cliente-create'),
    path('<int:pk>/editar/', ClienteUpdateView.as_view(), name='cliente-update'),
    path('<int:pk>/deletar/', ClienteDeleteView.as_view(), name='cliente-delete'),
]