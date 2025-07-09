# backend/cardapio/serializers.py

from rest_framework import serializers
from .models import Categoria
# Importar EstabelecimentoSerializer do app configuracao
from configuracao.serializers import EstabelecimentoSerializer


class CategoriaSerializer(serializers.ModelSerializer):
    # Campo 'estabelecimento' será apenas de leitura, pois será automaticamente
    # definido ou filtrado pelo EstablishmentFilteredViewSet.
    # Para visualização, queremos ver os detalhes do estabelecimento.
    estabelecimento = EstabelecimentoSerializer(read_only=True)

    class Meta:
        model = Categoria
        fields = [
            'id', 'estabelecimento', 'nome', 'descricao',
            'ativa', 'ordem', 'data_criacao', 'data_atualizacao'
        ]
        read_only_fields = ['data_criacao', 'data_atualizacao']

    # Método create e update não precisam lidar com 'estabelecimento' aqui,
    # pois o perform_create/perform_update do mixin já cuida disso.
    # Se um superusuário precisar definir explicitamente o estabelecimento,
    # uma implementação mais avançada seria necessária (ex: campo writable para superuser).