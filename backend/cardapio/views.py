# backend/cardapio/views.py

from rest_framework import viewsets, status
from rest_framework.response import Response
from rest_framework.exceptions import ValidationError, PermissionDenied
from .models import Categoria, ItemCardapio
from .serializers import CategoriaSerializer, ItemCardapioSerializer
from core.mixins import EstablishmentFilteredViewSet # Mantenha esta importação
from .mixins import CardapioEstablishmentMixin # Importa o seu NOVO mixin


class CategoriaViewSet(CardapioEstablishmentMixin, EstablishmentFilteredViewSet, viewsets.ModelViewSet):
    """
    ViewSet para Categoria do Cardápio, usando o mixin customizado para Cardapio.
    A ordem da herança é crucial aqui.
    """
    queryset = Categoria.objects.all()
    serializer_class = CategoriaSerializer
    # Os métodos get_queryset, perform_create e perform_update
    # do CardapioEstablishmentMixin serão usados aqui, pois ele vem primeiro na MRO.


class ItemCardapioViewSet(CardapioEstablishmentMixin, EstablishmentFilteredViewSet, viewsets.ModelViewSet):
    """
    ViewSet para Item de Cardápio, usando o mixin customizado para Cardapio.
    A ordem da herança é crucial aqui.
    """
    queryset = ItemCardapio.objects.all()
    serializer_class = ItemCardapioSerializer

    def perform_create(self, serializer):
        # O CardapioEstablishmentMixin.perform_create já definiu o 'estabelecimento'.
        # Agora, validamos a categoria em relação a esse estabelecimento.
        
        estabelecimento_do_item = serializer.validated_data.get('estabelecimento') 
        categoria_obj = serializer.validated_data.get('categoria')

        if not categoria_obj:
            raise ValidationError({"categoria_id": "A categoria é obrigatória."})

        # Valida se a categoria pertence ao estabelecimento do item.
        if categoria_obj.estabelecimento != estabelecimento_do_item:
            raise ValidationError(
                {"categoria_id": "A categoria selecionada não pertence ao estabelecimento deste item."}
            )
        
        # Chama o perform_create do mixin pai (CardapioEstablishmentMixin)
        # que já contém a lógica para salvar com o estabelecimento correto.
        super().perform_create(serializer) # IMPORTANTE: CHAMA O super() AQUI!

    def perform_update(self, serializer):
        # O CardapioEstablishmentMixin.perform_update já tratou da segurança do 'estabelecimento'.
        # Agora, validamos a categoria em relação ao estabelecimento do item.
        
        instance = self.get_object() 
        nova_categoria_obj = serializer.validated_data.get('categoria')
        
        if nova_categoria_obj and nova_categoria_obj.estabelecimento != instance.estabelecimento:
            raise ValidationError(
                {"categoria_id": "A categoria selecionada não pertence ao estabelecimento atual do item."}
            )
        
        # Chama o perform_update do mixin pai (CardapioEstablishmentMixin)
        # que já contém a lógica para salvar.
        super().perform_update(serializer) # IMPORTANTE: CHAMA O super() AQUI!