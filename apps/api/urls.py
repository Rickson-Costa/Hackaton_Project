from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import ProjetoViewSet, ContratoViewSet

router = DefaultRouter()
router.register(r'projetos', ProjetoViewSet)
router.register(r'contratos', ContratoViewSet)

urlpatterns = [
    path('', include(router.urls)),
]