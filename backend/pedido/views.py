# pedidos/views.py
from rest_framework import viewsets, status
from rest_framework.decorators import action, api_view # Adicione esta importação
from rest_framework.response import Response
from django.shortcuts import get_object_or_404
from django.db import transaction
from django.utils import timezone
from asgiref.sync import async_to_sync
from channels.layers import get_channel_layer

from .models import Mesa, ItemCardapio, Pedido, ItemPedido, EnvioCozinha
from mesa.serializers import MesaSerializer
from cardapio.serializers import ItemCardapioSerializer
from .serializers import ItemCardapioSerializer, PedidoSerializer, ItemPedidoSerializer # Mantenha PedidoSerializer

class MesaViewSet(viewsets.ModelViewSet):
    queryset = Mesa.objects.all()
    serializer_class = MesaSerializer

class ItemCardapioViewSet(viewsets.ModelViewSet):
    queryset = ItemCardapio.objects.all()
    serializer_class = ItemCardapioSerializer

class PedidoViewSet(viewsets.ModelViewSet):
    queryset = Pedido.objects.all()
    serializer_class = PedidoSerializer

    # >>> ADICIONE ESTE BLOCO AQUI DENTRO DE PedidoViewSet <<<
    @action(detail=False, methods=['get'], url_path='aberto/mesa/(?P<mesa_numero>[0-9]+)')
    def aberto_por_mesa(self, request, mesa_numero=None):
        """
        Retorna o pedido aberto para uma mesa específica.
        """
        if not mesa_numero:
            return Response({'detail': 'Número da mesa é obrigatório.'}, status=status.HTTP_400_BAD_REQUEST)

        try:
            pedido = Pedido.objects.get(mesa__numero=mesa_numero, status='aberto')
            serializer = self.get_serializer(pedido)
            return Response(serializer.data)
        except Pedido.DoesNotExist:
            return Response({'detail': 'Nenhum pedido aberto encontrado para esta mesa.'},
                            status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            return Response({'detail': f'Ocorreu um erro interno: {e}'},
                            status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    # >>> FIM DO BLOCO ADICIONADO <<<

class ItemPedidoViewSet(viewsets.ModelViewSet):
    queryset = ItemPedido.objects.all()
    serializer_class = ItemPedidoSerializer

# >>> REMOVA A FUNÇÃO @api_view abaixo, pois ela foi substituída pela action <<<
# @api_view(['GET'])
# def pedido_aberto_mesa(request, mesa_id):
#    try:
#        mesa = Mesa.objects.get(pk=mesa_id)
#        pedido = Pedido.objects.get(mesa=mesa, status='aberto')
#        serializer = PedidoSerializer(pedido)
#        return Response(serializer.data)
#    except Mesa.DoesNotExist:
#        return Response({"error": "Mesa não encontrada."}, status=status.HTTP_404_NOT_FOUND)
#    except Pedido.DoesNotExist:
#        return Response({"error": "Nenhum pedido aberto encontrado para esta mesa."}, status=status.HTTP_404_NOT_FOUND)
# >>> FIM DA REMOÇÃO <<<

@api_view(['POST'])
def criar_novo_pedido(request):
    mesa_id = request.data.get('mesa_id')
    if not mesa_id:
        return Response({"error": "ID da mesa é obrigatório."}, status=status.HTTP_400_BAD_REQUEST)

    try:
        mesa = Mesa.objects.get(pk=mesa_id)
    except Mesa.DoesNotExist:
        return Response({"error": "Mesa não encontrada."}, status=status.HTTP_404_NOT_FOUND)

    if Pedido.objects.filter(mesa=mesa, status='aberto').exists():
        return Response({"error": "Já existe um pedido aberto para esta mesa."}, status=status.HTTP_409_CONFLICT)

    with transaction.atomic():
        pedido = Pedido.objects.create(mesa=mesa, status='aberto', valor_total=0.0)
        mesa.status = 'Ocupada'
        mesa.save()
        serializer = PedidoSerializer(pedido)
        return Response(serializer.data, status=status.HTTP_201_CREATED)


@api_view(['POST'])
def adicionar_itens_ao_pedido(request):
    pedido_id = request.data.get('pedido_id')
    itens_carrinho = request.data.get('itens') # Lista de {item_cardapio_id, quantidade, observacoes}

    if not pedido_id or not itens_carrinho:
        return Response({"error": "ID do pedido e itens são obrigatórios."}, status=status.HTTP_400_BAD_REQUEST)

    pedido = get_object_or_404(Pedido, pk=pedido_id)

    with transaction.atomic():
        total_recalculado = pedido.valor_total
        for item_carrinho in itens_carrinho:
            item_cardapio_id = item_carrinho.get('item_cardapio_id')
            quantidade = item_carrinho.get('quantidade')
            observacoes = item_carrinho.get('observacoes', '')

            if not item_cardapio_id or not quantidade:
                return Response({"error": "Cada item deve ter item_cardapio_id e quantidade."}, status=status.HTTP_400_BAD_REQUEST)

            item_cardapio = get_object_or_404(ItemCardapio, pk=item_cardapio_id)

            item_pedido, created = ItemPedido.objects.get_or_create(
                pedido=pedido,
                item_cardapio=item_cardapio,
                defaults={'quantidade': quantidade, 'observacoes': observacoes, 'enviado_para_cozinha': False}
            )

            if not created:
                quantidade_antiga = item_pedido.quantidade
                item_pedido.quantidade += quantidade
                item_pedido.observacoes = observacoes
                item_pedido.save()
                total_recalculado += (quantidade * item_cardapio.preco)
            else:
                total_recalculado += (quantidade * item_cardapio.preco)
            
        pedido.valor_total = total_recalculado
        pedido.save()

    serializer = PedidoSerializer(pedido)
    return Response(serializer.data, status=status.HTTP_200_OK)


@api_view(['POST'])
def enviar_para_cozinha(request, pedido_id):
    pedido = get_object_or_404(Pedido, pk=pedido_id)
    itens_para_enviar_ids = request.data.get('itens_ids', []) # Lista de IDs de ItemPedido a serem enviados

    if not itens_para_enviar_ids:
        return Response({"error": "Nenhum item especificado para envio."}, status=status.HTTP_400_BAD_REQUEST)

    with transaction.atomic():
        envio = EnvioCozinha.objects.create(
            pedido=pedido,
            data_envio=timezone.now(),
            status='Pendente'
        )
        itens_enviados_data = []

        for item_pedido_id in itens_para_enviar_ids:
            try:
                item_pedido = ItemPedido.objects.get(pk=item_pedido_id, pedido=pedido, enviado_para_cozinha=False)
                item_pedido.enviado_para_cozinha = True
                item_pedido.envio_cozinha = envio # Associa ao envio específico
                item_pedido.save()
                
                itens_enviados_data.append({
                    'item_cardapio_nome': item_pedido.item_cardapio.nome,
                    'quantidade': item_pedido.quantidade,
                    'observacoes': item_pedido.observacoes,
                    'pedido_id': pedido.id,
                    'mesa_numero': pedido.mesa.numero
                })

            except ItemPedido.DoesNotExist:
                continue
        
        if not itens_enviados_data:
            return Response({"error": "Nenhum item válido encontrado para envio."}, status=status.HTTP_400_BAD_REQUEST)

        channel_layer = get_channel_layer()
        async_to_sync(channel_layer.group_send)(
            'kitchen_updates', # Nome do grupo definido no consumer
            {
                'type': 'send_kitchen_update', # Nome do método no consumer (sem o 'async def')
                'message': {
                    'type': 'nova_ordem',
                    'envio_id': envio.id,
                    'pedido_id': pedido.id,
                    'mesa_numero': pedido.mesa.numero,
                    'itens': itens_enviados_data,
                    'data_envio': envio.data_envio.isoformat()
                }
            }
        )

    serializer = PedidoSerializer(pedido)
    return Response(serializer.data, status=status.HTTP_200_OK)