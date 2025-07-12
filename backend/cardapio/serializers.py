# backend/cardapio/serializers.py
from rest_framework import serializers
from .models import Categoria, ItemCardapio

class CategoriaSerializer(serializers.ModelSerializer):
    estabelecimento_nome = serializers.StringRelatedField(source='estabelecimento.nome', read_only=True)
    itens = serializers.PrimaryKeyRelatedField(many=True, read_only=True)

    class Meta:
        model = Categoria
        fields = [
            'id',
            'estabelecimento',
            'estabelecimento_nome',
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
    # Campo 'categoria' agora sempre lida com o ID da Primary Key,
    # tanto para escrita (write_only=True) quanto para leitura (se fosse read_only=False).
    # Removendo explicitamente categoria_id e usando apenas 'categoria' como PrimaryKeyRelatedField
    # Isso garante que ele retorne o UUID para leitura.
    categoria = serializers.PrimaryKeyRelatedField(
        queryset=Categoria.objects.all(),
        # Não precisa de 'source' se o nome do campo for o mesmo do modelo.
        # Caso queira que ele seja write_only para enviar, mas apareça o ID para leitura:
        # AQUI É A CHAVE: Se ele é um PrimaryKeyRelatedField, ele sempre retorna o ID para leitura.
    )
    
    categoria_nome = serializers.StringRelatedField(source='categoria.nome', read_only=True)
    estabelecimento_nome = serializers.StringRelatedField(source='estabelecimento.nome', read_only=True) 

    class Meta:
        model = ItemCardapio
        fields = [
            'id',
            'categoria', # Usamos 'categoria' diretamente para o PK do modelo
            'categoria_nome',
            'estabelecimento', 
            'estabelecimento_nome', 
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