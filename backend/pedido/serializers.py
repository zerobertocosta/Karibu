# backend/pedido/serializers.py

from rest_framework import serializers
from .models.pedido import Pedido, ItemPedido
from .models.envio_cozinha import EnvioCozinha
from cardapio.serializers import ItemCardapioSerializer # Certifique-se de que este import está correto
from django.db.models import Sum # Importar Sum para a agregação

class ItemPedidoSerializer(serializers.ModelSerializer):
    # Usar SerializerMethodField para exibir o nome do item do cardápio
    cardapio_nome = serializers.CharField(source='cardapio.nome', read_only=True)
    cardapio = ItemCardapioSerializer(read_only=True) # Inclui todos os detalhes do item do cardápio
    
    class Meta:
        model = ItemPedido
        fields = ['id', 'cardapio', 'cardapio_nome', 'quantidade', 'subtotal', 'envio_cozinha'] # Adicionar 'envio_cozinha'

class EnvioCozinhaSerializer(serializers.ModelSerializer):
    itens_enviados = ItemPedidoSerializer(many=True, read_only=True)
    status_display = serializers.CharField(source='get_status_display', read_only=True)
    
    # Campo para o valor total deste envio
    valor_total_envio = serializers.SerializerMethodField()

    class Meta:
        model = EnvioCozinha
        fields = '__all__' 

    # Método para calcular o valor total de um envio específico
    def get_valor_total_envio(self, obj):
        total = obj.itens_enviados.aggregate(total_sum=Sum('subtotal')).get('total_sum')
        return total if total is not None else 0.00


class PedidoSerializer(serializers.ModelSerializer):
    itens_no_carrinho = serializers.SerializerMethodField()
    envios_cozinha = EnvioCozinhaSerializer(many=True, read_only=True) # Para listar os envios
    status_display = serializers.CharField(source='get_status_display', read_only=True) # Para exibir o nome amigável do status

    # Campos de gorjeta e observações na finalização (já existentes)
    gorjeta = serializers.DecimalField(max_digits=10, decimal_places=2, required=False, allow_null=True)
    observacoes_finalizacao = serializers.CharField(required=False, allow_null=True, allow_blank=True)

    # O campo 'couvert_artistico' FOI REMOVIDO DAQUI


    class Meta:
        model = Pedido
        fields = [
            'id', 'mesa', 'data_hora_pedido', 'status', 'status_display', 
            'valor_total', 'itens_no_carrinho', 'envios_cozinha',
            'gorjeta', 'observacoes_finalizacao' # O campo 'couvert_artistico' foi removido
        ]
        read_only_fields = ['data_hora_pedido', 'valor_total'] # Valor total é calculado

    def get_itens_no_carrinho(self, obj):
        # Filtra itens que AINDA NÃO FORAM ENVIADOS para a cozinha
        itens = obj.itens_pedido.filter(envio_cozinha__isnull=True).order_by('id')
        return ItemPedidoSerializer(itens, many=True).data
