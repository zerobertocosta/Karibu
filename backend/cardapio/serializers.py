# backend/cardapio/serializers.py

from rest_framework import serializers
from .models import Categoria, ItemCardapio
from configuracao.serializers import EstabelecimentoSerializer

# Serializer para ItemCardapio (para escrita e leitura básica)
class ItemCardapioSerializer(serializers.ModelSerializer):
    # 'estabelecimento' será read-only, pois o mixin irá definir/filtrar automaticamente.
    estabelecimento = EstabelecimentoSerializer(read_only=True)
    # 'categoria' será um campo de escrita (apenas o ID da categoria)
    # E será validado no ViewSet ou no modelo para garantir que pertença ao mesmo estabelecimento.
    categoria_id = serializers.PrimaryKeyRelatedField(
        queryset=Categoria.objects.all(), source='categoria', write_only=True
    )
    # Para leitura, podemos opcionalmente aninhar a categoria completa
    categoria = serializers.StringRelatedField(read_only=True) # Ou CategoriaSerializer(read_only=True) se quiser mais detalhes.

    class Meta:
        model = ItemCardapio
        fields = [
            'id', 'estabelecimento', 'categoria_id', 'categoria',
            'nome', 'descricao', 'preco', 'disponivel', 'imagem',
            'ordem', 'data_criacao', 'data_atualizacao'
        ]
        read_only_fields = ['data_criacao', 'data_atualizacao']
        # 'categoria' é read-only aqui porque 'categoria_id' é para escrita.
        # 'imagem' precisa ser tratado com cautela em DRF para uploads, o default é ok.


# Serializer para Categoria (agora também com itens aninhados para leitura)
class CategoriaSerializer(serializers.ModelSerializer):
    estabelecimento = EstabelecimentoSerializer(read_only=True)
    # Campo aninhado para listar itens dentro da categoria (somente leitura)
    itens = ItemCardapioSerializer(many=True, read_only=True)

    class Meta:
        model = Categoria
        fields = [
            'id', 'estabelecimento', 'nome', 'descricao',
            'ativa', 'ordem', 'data_criacao', 'data_atualizacao',
            'itens' # Incluir os itens aninhados aqui
        ]
        read_only_fields = ['data_criacao', 'data_atualizacao']