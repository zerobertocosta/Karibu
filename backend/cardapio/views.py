# backend/cardapio/views.py

from rest_framework import viewsets
from rest_framework.decorators import action
from rest_framework.response import Response
from .models import Categoria, ItemCardapio
from .serializers import CategoriaSerializer, ItemCardapioSerializer

# A linha que causava a importação circular foi removida daqui.
# Se você tinha algo como:
# from cardapio.views import ItemCardapioViewSet, CategoriaCardapioViewSet
# OU
# from .views import ItemCardapioViewSet, CategoriaCardapioViewSet
# Essas linhas NÃO DEVEM ESTAR AQUI.

class CategoriaViewSet(viewsets.ModelViewSet):
    queryset = Categoria.objects.all().order_by('nome')
    serializer_class = CategoriaSerializer

    @action(detail=False, methods=['get'], url_path='com_itens')
    def com_itens(self, request):
        """
        Retorna todas as categorias com seus respectivos itens de cardápio aninhados.
        """
        queryset = self.get_queryset()
        serializer = CategoriaSerializer(queryset, many=True)
        return Response(serializer.data)


class ItemCardapioViewSet(viewsets.ModelViewSet):
    queryset = ItemCardapio.objects.all().order_by('nome') 
    serializer_class = ItemCardapioSerializer
