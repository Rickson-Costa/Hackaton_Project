from rest_framework import viewsets
from .serializers import ProjetoSerializer, ContratoSerializer
from apps.projetos.models import Projeto
from apps.contratos.models import Contrato

class ProjetoViewSet(viewsets.ReadOnlyModelViewSet):
    """
    API endpoint que permite que projetos sejam visualizados.
    """
    queryset = Projeto.objects.all()
    serializer_class = ProjetoSerializer

class ContratoViewSet(viewsets.ReadOnlyModelViewSet):
    """
    API endpoint que permite que contratos sejam visualizados.
    """
    queryset = Contrato.objects.all()
    serializer_class = ContratoSerializer