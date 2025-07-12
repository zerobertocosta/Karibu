# backend/cardapio/mixins.py

from rest_framework.exceptions import PermissionDenied, ValidationError
from configuracao.models import Estabelecimento 
from core.mixins import EstablishmentFilteredViewSet 


class CardapioEstablishmentMixin:
    """
    Mixin customizado para os ViewSets de Categoria e ItemCardapio.
    Ele vai ser usado JUNTO com o EstablishmentFilteredViewSet e ModelViewSet.
    A lógica de atribuição de estabelecimento agora é mais simples, focando no perfil do usuário.
    """

    def get_queryset(self):
        # Lógica para superusuários e usuários comuns.
        if not self.request.user.is_authenticated:
            raise PermissionDenied("Usuário não autenticado.")

        if self.request.user.is_superuser:
            # Superusuários veem todos os objetos do modelo deste ViewSet.
            # Eles podem usar o Django Admin para gerenciar estabelecimentos.
            return super(EstablishmentFilteredViewSet, self).get_queryset()
        
        # Usuários regulares (gerentes)
        if not hasattr(self.request.user, 'perfil') or not self.request.user.perfil.estabelecimento:
            raise PermissionDenied("Seu perfil de usuário não está vinculado a um estabelecimento.")
        
        # Usuário regular (gestor) vê apenas os objetos do seu estabelecimento.
        return super(EstablishmentFilteredViewSet, self).get_queryset().filter(estabelecimento=self.request.user.perfil.estabelecimento)

    def perform_create(self, serializer):
        # O estabelecimento será SEMPRE o do perfil do usuário logado,
        # simplificando a lógica de criação.
        if not self.request.user.is_authenticated:
            raise PermissionDenied("Usuário não autenticado para criar.")

        if not hasattr(self.request.user, 'perfil') or not self.request.user.perfil.estabelecimento:
            raise ValidationError({"detail": "Seu perfil de usuário não está vinculado a um estabelecimento."})
            
        final_establishment = self.request.user.perfil.estabelecimento
        
        serializer.save(estabelecimento=final_establishment)

    def perform_update(self, serializer):
        # A atualização garante que o objeto pertence ao estabelecimento do usuário logado.
        instance = self.get_object() 

        if not self.request.user.is_superuser:
            # Usuários comuns NÃO podem alterar o campo 'estabelecimento' do objeto.
            # Essa validação já foi reforçada no perform_update anterior.
            if 'estabelecimento' in serializer.validated_data and \
               serializer.validated_data['estabelecimento'] != instance.estabelecimento:
                raise PermissionDenied("Você não tem permissão para alterar o estabelecimento de um objeto.")
            
            # E garantimos que o objeto que está sendo atualizado pertence ao estabelecimento do usuário.
            if instance.estabelecimento != self.request.user.perfil.estabelecimento:
                raise PermissionDenied("Você não tem permissão para atualizar um objeto que não pertence ao seu estabelecimento.")
        
        # Se for superusuário, ele pode alterar o campo estabelecimento,
        # mas como definimos que ele não usará essa funcionalidade pelo frontend,
        # a lógica se torna mais simples.
        serializer.save()