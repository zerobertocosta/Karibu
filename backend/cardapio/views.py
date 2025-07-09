# backend/cardapio/views.py

from rest_framework import viewsets
from .models import Categoria
from .serializers import CategoriaSerializer
# Importar o mixin de filtragem por estabelecimento
from core.mixins import EstablishmentFilteredViewSet


class CategoriaViewSet(EstablishmentFilteredViewSet, viewsets.ModelViewSet):
    """
    ViewSet para Categoria do Cardápio.
    Hereda de EstablishmentFilteredViewSet para garantir que apenas categorias
    do estabelecimento do usuário logado sejam acessíveis.
    """
    queryset = Categoria.objects.all()
    serializer_class = CategoriaSerializer
    # A permissão 'IsAuthenticatedAndBelongsToEstablishment' já está definida globalmente
    # em settings.py, então não precisamos especificá-la aqui novamente,
    # mas se você precisasse de permissões adicionais, as adicionaria aqui.
    # permission_classes = [IsAuthenticatedOrReadOnly, OutraPermissaoCustomizada]

    # O método get_queryset já é sobrescrito pelo EstablishmentFilteredViewSet mixin.
    # O método perform_create também é sobrescrito para associar a categoria ao estabelecimento.