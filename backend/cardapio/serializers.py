# backend/cardapio/serializers.py

from rest_framework import serializers
from .models import Categoria, ItemCardapio

class ItemCardapioSerializer(serializers.ModelSerializer):
    class Meta:
        model = ItemCardapio
        fields = ['id', 'nome', 'descricao', 'preco', 'disponivel', 'imagem']
        # Adicione 'categoria' se precisar mostrar a categoria do item individualmente
        # Mas para aninhamento dentro da categoria, não é estritamente necessário aqui

class CategoriaSerializer(serializers.ModelSerializer):
    # Este campo 'itens' vai carregar todos os ItemCardapio relacionados à categoria
    itens = ItemCardapioSerializer(many=True, read_only=True)

    class Meta:
        model = Categoria
        fields = ['id', 'nome', 'descricao', 'itens'] # Incluímos 'itens' aqui