# backend/cardapio/serializers.py (MANTENHA ESTE)

from rest_framework import serializers
from .models import Categoria, ItemCardapio

class ItemCardapioSerializer(serializers.ModelSerializer):
    categoria_id = serializers.PrimaryKeyRelatedField(
        queryset=Categoria.objects.all(),
        source='categoria',
        write_only=True,
        help_text="ID da categoria a que este item pertence."
    )
    categoria_nome = serializers.StringRelatedField(source='categoria.nome', read_only=True)

    class Meta:
        model = ItemCardapio
        fields = [
            'id', 'categoria_id', 'categoria_nome', 'nome', 'descricao', 'preco',
            'disponivel', 'imagem', 'ordem', 'data_criacao', 'data_atualizacao'
        ]
        read_only_fields = ['data_criacao', 'data_atualizacao', 'estabelecimento']

class CategoriaSerializer(serializers.ModelSerializer):
    estabelecimento = serializers.StringRelatedField(read_only=True)
    itens = ItemCardapioSerializer(many=True, read_only=True)

    class Meta:
        model = Categoria
        fields = [
            'id', 'estabelecimento', 'nome', 'descricao', 'ativa', 'ordem',
            'data_criacao', 'data_atualizacao', 'itens'
        ]
        read_only_fields = ['data_criacao', 'data_atualizacao', 'estabelecimento']