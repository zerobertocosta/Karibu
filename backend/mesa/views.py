# backend/mesas/views.py (CÓDIGO COMPLETO ATUALIZADO)

from rest_framework import viewsets
from .models import Mesa
from .serializers import MesaSerializer
from .mixins import MesaEstablishmentMixin # Importa o NOVO mixin específico para Mesa

class MesaViewSet(MesaEstablishmentMixin, viewsets.ModelViewSet):
    """
    ViewSet para a gestão de Mesas.
    Hereda de MesaEstablishmentMixin para garantir que cada mesa esteja vinculada e seja acessível apenas pelo seu respectivo estabelecimento.
    """
    queryset = Mesa.objects.all()
    serializer_class = MesaSerializer