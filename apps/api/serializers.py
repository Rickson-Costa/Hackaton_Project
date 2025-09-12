from rest_framework import serializers
from apps.projetos.models import Projeto
from apps.contratos.models import Contrato

class ProjetoSerializer(serializers.ModelSerializer):
    class Meta:
        model = Projeto
        fields = ['id', 'nome', 'status', 'data_inicio', 'data_fim', 'custo_previsto', 'custo_realizado']

class ContratoSerializer(serializers.ModelSerializer):
    class Meta:
        model = Contrato
        fields = ['id', 'numero_contrato', 'projeto', 'prestador', 'valor_total', 'status']