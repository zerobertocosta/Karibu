# backend/core/views.py

from rest_framework import viewsets, mixins
from rest_framework.permissions import AllowAny
from .models import Cliente, Mesa, Produto, Pedido, PedidoItem
from .serializers import (
    ClienteSerializer, MesaSerializer, ProdutoSerializer,
    PedidoSerializer, PedidoItemSerializer
)

# ViewSet para Produto (pode ser consultado por clientes)
class ProdutoViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Produto.objects.all()
    serializer_class = ProdutoSerializer
    permission_classes = [AllowAny] # Permite acesso sem autenticação

# ViewSet para Cliente (permite criar novos clientes se necessário, ou apenas leitura)
class ClienteViewSet(viewsets.ModelViewSet):
    queryset = Cliente.objects.all()
    serializer_class = ClienteSerializer
    permission_classes = [AllowAny]

# ViewSet para Mesa (apenas leitura, geralmente mesas são pré-cadastradas)
class MesaViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Mesa.objects.all()
    serializer_class = MesaSerializer
    permission_classes = [AllowAny]

# ViewSet para PedidoItem (geralmente não acessado diretamente pela API, mas pode ser útil)
# Incluímos ReadOnlyModelViewSet pois os itens são geralmente manipulados via Pedido
class PedidoItemViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = PedidoItem.objects.all()
    serializer_class = PedidoItemSerializer
    permission_classes = [AllowAny]

# ViewSet para Pedido
class PedidoViewSet(viewsets.ModelViewSet):
    queryset = Pedido.objects.all().order_by('-data_hora_pedido') # Ordena os pedidos pelo mais recente
    serializer_class = PedidoSerializer
    permission_classes = [AllowAny] # Permite acesso sem autenticação

    # Sobrescreve get_queryset para otimizar a busca dos detalhes aninhados
    # `select_related` para campos ForeignKey e `prefetch_related` para campos ManyToMany ou Reverse ForeignKey
    def get_queryset(self):
        return Pedido.objects.all().order_by('-data_hora_pedido').select_related(
            'cliente', 'mesa'
        ).prefetch_related(
            'itens__produto' # Isso busca os itens do pedido e seus produtos relacionados
        )