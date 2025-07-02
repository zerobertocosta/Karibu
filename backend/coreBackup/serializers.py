# backend/core/serializers.py

from rest_framework import serializers
from .models import Cliente, Mesa, Produto, Pedido, PedidoItem

# Serializer para Cliente (simplificado para uso em PedidoSerializer)
class ClienteSerializer(serializers.ModelSerializer):
    class Meta:
        model = Cliente
        fields = ['id', 'nome'] # Incluindo o nome para display fácil

# Serializer para Mesa (simplificado para uso em PedidoSerializer)
class MesaSerializer(serializers.ModelSerializer):
    class Meta:
        model = Mesa
        fields = ['id', 'numero'] # Incluindo o numero para display fácil

# Serializer para Produto (simplificado para uso em PedidoItemSerializer)
class ProdutoSerializer(serializers.ModelSerializer):
    class Meta:
        model = Produto
        fields = ['id', 'nome', 'preco'] # Apenas campos essenciais para o item

# Serializer para PedidoItem (item individual dentro de um pedido)
class PedidoItemSerializer(serializers.ModelSerializer):
    produto = ProdutoSerializer(read_only=True) # Serializa os detalhes do produto
    produto_id = serializers.PrimaryKeyRelatedField(
        queryset=Produto.objects.all(), source='produto', write_only=True
    )

    class Meta:
        model = PedidoItem
        fields = ['id', 'produto', 'produto_id', 'quantidade', 'preco_unitario', 'subtotal']
        read_only_fields = ['preco_unitario', 'subtotal'] # Preço unitário e subtotal são calculados

# Serializer principal para Pedido
class PedidoSerializer(serializers.ModelSerializer):
    # Serializa os itens aninhados dentro do pedido
    # many=True indica que pode haver múltiplos itens
    # read_only=False e required=False para permitir criação/atualização com ou sem itens na mesma requisição
    itens = PedidoItemSerializer(many=True, required=False, read_only=False)
    
    # Serializa detalhes aninhados de Cliente e Mesa
    cliente = ClienteSerializer(read_only=True)
    mesa = MesaSerializer(read_only=True)

    # Campos para receber o ID do cliente e da mesa na criação/atualização
    cliente_id = serializers.PrimaryKeyRelatedField(
        queryset=Cliente.objects.all(), source='cliente', write_only=True
    )
    mesa_id = serializers.PrimaryKeyRelatedField(
        queryset=Mesa.objects.all(), source='mesa', write_only=True
    )

    class Meta:
        model = Pedido
        # Adicione 'itens', 'observacoes', 'cliente', 'mesa' aqui para que sejam incluídos na saída da API
        fields = ['id', 'cliente', 'cliente_id', 'mesa', 'mesa_id', 'status', 'data_hora_pedido', 'observacoes', 'valor_total', 'itens']
        read_only_fields = ['data_hora_pedido', 'valor_total'] # Estes são calculados ou definidos automaticamente

    def create(self, validated_data):
        itens_data = validated_data.pop('itens', [])
        pedido = Pedido.objects.create(**validated_data)
        
        for item_data in itens_data:
            produto = item_data.pop('produto') # Pega o objeto Produto já resolvido pelo produto_id
            PedidoItem.objects.create(pedido=pedido, produto=produto, **item_data)
        
        pedido.save() # Para garantir que valor_total seja calculado após a adição dos itens
        return pedido

    def update(self, instance, validated_data):
        # Lógica de atualização de itens, se necessário.
        # Por enquanto, focamos em atualizar campos do Pedido, como status e observacoes.
        # Se você precisar adicionar/remover itens via PATCH/PUT, esta lógica seria mais complexa.
        itens_data = validated_data.pop('itens', []) # Remove itens para processamento separado

        # Atualiza campos diretos do Pedido
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()
        
        # Opcional: Lógica para atualizar PedidoItems se 'itens_data' for fornecido no PATCH/PUT
        # Para um CRUD completo de itens via este endpoint, você precisaria de um controle mais sofisticado
        # (identificar itens a serem atualizados, criados ou excluídos).
        # Por simplicidade, para o propósito atual, focamos no status e observacoes
        # e a criação de itens só ocorre no 'create'.
        
        return instance