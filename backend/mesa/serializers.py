# backend/mesa/serializers.py

from rest_framework import serializers
from .models import Mesa
from configuracao.serializers import EstabelecimentoSerializer # Importa o Serializer de Estabelecimento

class MesaSerializer(serializers.ModelSerializer):
    # O campo 'estabelecimento' será read-only, pois será definido/filtrado automaticamente pelo mixin.
    estabelecimento = EstabelecimentoSerializer(read_only=True)

    class Meta:
        model = Mesa
        fields = [
            'id', 'estabelecimento', 'numero', 'capacidade',
            'status', 'descricao', 'data_criacao', 'data_atualizacao'
        ]
        read_only_fields = ['data_criacao', 'data_atualizacao']
        # A validação de unicidade de 'numero' por 'estabelecimento' já é tratada no modelo via unique_together e clean().