# backend/cliente/views.py

from rest_framework import viewsets
from .models import Cliente
from .serializers import ClienteSerializer
from core.mixins import EstablishmentFilteredViewSet # Importa o mixin de multi-tenancy

class ClienteViewSet(EstablishmentFilteredViewSet, viewsets.ModelViewSet):
    """
    ViewSet para a gestão de Clientes.
    Hereda de EstablishmentFilteredViewSet para garantir que cada cliente
    esteja vinculado e seja acessível apenas pelo seu respectivo estabelecimento.
    """
    queryset = Cliente.objects.all()
    serializer_class = ClienteSerializer

    # A lógica de perform_create/update e get_queryset do mixin já cuida
    # automaticamente do preenchimento e filtragem do campo 'estabelecimento'.