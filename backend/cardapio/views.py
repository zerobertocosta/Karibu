# backend/cardapio/views.py
from rest_framework import viewsets, status
from rest_framework.response import Response
from rest_framework.exceptions import ValidationError, PermissionDenied
from .models import Categoria, ItemCardapio
from .serializers import CategoriaSerializer, ItemCardapioSerializer
from core.mixins import EstablishmentFilteredViewSet 
from .mixins import CardapioEstablishmentMixin 


class CategoriaViewSet(CardapioEstablishmentMixin, EstablishmentFilteredViewSet, viewsets.ModelViewSet):
    queryset = Categoria.objects.all()
    serializer_class = CategoriaSerializer


class ItemCardapioViewSet(CardapioEstablishmentMixin, EstablishmentFilteredViewSet, viewsets.ModelViewSet):
    queryset = ItemCardapio.objects.all()
    serializer_class = ItemCardapioSerializer

    def perform_create(self, serializer):
        # O CardapioEstablishmentMixin já adiciona o 'estabelecimento' ao serializer.
        # Pegamos o estabelecimento que será salvo para o Item.
        estabelecimento_do_item = self.request.user.perfil.estabelecimento

        # Validamos se a categoria escolhida pertence ao estabelecimento do usuário.
        categoria_obj = serializer.validated_data.get('categoria')
        if not categoria_obj:
            raise ValidationError({"categoria_id": "A categoria é obrigatória."})

        if categoria_obj.estabelecimento != estabelecimento_do_item:
            raise ValidationError(
                {"categoria_id": "A categoria selecionada não pertence ao seu estabelecimento."}
            )
        
        serializer.save(estabelecimento=estabelecimento_do_item) # Garante que o estabelecimento está correto

    def perform_update(self, serializer):
        instance = self.get_object() 
        
        # O CardapioEstablishmentMixin já validou que o usuário só pode atualizar objetos
        # que pertencem ao seu estabelecimento.
        
        # Agora, validamos se a nova categoria (se alterada) pertence ao estabelecimento do item.
        nova_categoria_obj = serializer.validated_data.get('categoria')
        if nova_categoria_obj and nova_categoria_obj.estabelecimento != instance.estabelecimento:
            raise ValidationError(
                {"categoria_id": "A categoria selecionada não pertence ao estabelecimento atual do item."}
            )
        
        serializer.save() # Chama o save normal, o mixin já cuida do estabelecimento