# backend/configuracao/views.py

from rest_framework import viewsets, permissions
from .models import Estabelecimento
from .serializers import EstabelecimentoSerializer

class EstabelecimentoViewSet(viewsets.ModelViewSet):
    """
    ViewSet para o modelo Estabelecimento.
    Apenas superusuários (IsAdminUser) podem listar, criar, atualizar ou deletar estabelecimentos.
    Este ViewSet NÃO usa EstablishmentFilteredViewSet, pois gerencia os próprios tenants.
    """
    queryset = Estabelecimento.objects.all()
    serializer_class = EstabelecimentoSerializer
    # Permissão para garantir que apenas superusuários possam gerenciar estabelecimentos.
    permission_classes = [permissions.IsAdminUser]