# backend/mesa/views.py

from rest_framework import viewsets
from .models import Mesa
from .serializers import MesaSerializer
from core.mixins import EstablishmentFilteredViewSet # Importa o mixin de multi-tenancy

class MesaViewSet(EstablishmentFilteredViewSet, viewsets.ModelViewSet):
    """
    ViewSet para a gestão de Mesas.
    Hereda de EstablishmentFilteredViewSet para garantir que cada mesa
    esteja vinculada e seja acessível apenas pelo seu respectivo estabelecimento.
    """
    queryset = Mesa.objects.all()
    serializer_class = MesaSerializer

    # A lógica de perform_create/update e get_queryset do mixin já cuida
    # automaticamente do preenchimento e filtragem do campo 'estabelecimento'.