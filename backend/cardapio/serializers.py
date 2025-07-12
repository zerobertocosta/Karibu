# backend/cardapio/serializers.py
from rest_framework import serializers
from .models import Categoria, ItemCardapio

class CategoriaSerializer(serializers.ModelSerializer):
    # Campo para exibir o NOME do estabelecimento na listagem/detalhes
    estabelecimento_nome = serializers.StringRelatedField(source='estabelecimento.nome', read_only=True)
    itens = serializers.PrimaryKeyRelatedField(many=True, read_only=True)

    class Meta:
        model = Categoria
        fields = [
            'id',
            'estabelecimento',
            'estabelecimento_nome', # NOVO: Para exibir o nome
            'nome',
            'descricao',
            'ativa',
            'ordem',
            'data_criacao',
            'data_atualizacao',
            'itens'
        ]
        read_only_fields = ['data_criacao', 'data_atualizacao', 'estabelecimento']


class ItemCardapioSerializer(serializers.ModelSerializer):
    categoria_id = serializers.PrimaryKeyRelatedField(
        queryset=Categoria.objects.all(),
        source='categoria',
        write_only=True,
        help_text="ID da categoria a que este item pertence."
    )
    
    categoria_nome = serializers.StringRelatedField(source='categoria.nome', read_only=True)
    # Campo para exibir o NOME do estabelecimento na listagem/detalhes
    estabelecimento_nome = serializers.StringRelatedField(source='estabelecimento.nome', read_only=True) # NOVO: Para exibir o nome


    class Meta:
        model = ItemCardapio
        fields = [
            'id',
            'categoria_id',
            'categoria_nome',
            'estabelecimento', 
            'estabelecimento_nome', # NOVO: Para exibir o nome
            'nome',
            'descricao',
            'preco',
            'disponivel',
            'imagem',
            'ordem',
            'data_criacao',
            'data_atualizacao'
        ]
        read_only_fields = ['data_criacao', 'data_atualizacao', 'estabelecimento']