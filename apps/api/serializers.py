from rest_framework import serializers
from apps.projetos.models import Projeto
from apps.contratos.models import Contrato

class ProjetoSerializer(serializers.ModelSerializer):
    class Meta:
        model = Projeto
        fields = ['cod_projeto', 'nome', 'situacao', 'data_inicio', 'data_encerramento', 'custo_previsto', 'custo_realizado']

class ContratoSerializer(serializers.ModelSerializer):
    projeto = serializers.StringRelatedField(source='cod_ordem.cod_requisicao.cod_projeto')

    class Meta:
        model = Contrato
        fields = ['num_contrato', 'projeto', 'contratado', 'valor', 'situacao']
