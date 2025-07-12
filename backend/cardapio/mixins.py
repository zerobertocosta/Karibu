# backend/cardapio/mixins.py

from rest_framework.exceptions import PermissionDenied, ValidationError
from configuracao.models import Estabelecimento # Importe Estabelecimento para uso
from core.mixins import EstablishmentFilteredViewSet # <--- ADICIONE ESTA LINHA DE VOLTA!


class CardapioEstablishmentMixin: # ATENÇÃO: Mantém como antes, não herda diretamente aqui.
    """
    Mixin customizado para os ViewSets de Categoria e ItemCardapio.
    Ele vai ser usado JUNTO com o EstablishmentFilteredViewSet e ModelViewSet.
    """

    def get_queryset(self):
        # Lógica para superusuários e usuários comuns.
        if not self.request.user.is_authenticated:
            raise PermissionDenied("Usuário não autenticado.")

        # Superusuários veem todos os objetos do modelo deste ViewSet.
        if self.request.user.is_superuser:
            # Chama o get_queryset do ModelViewSet (ou da próxima classe na MRO),
            # não o do EstablishmentFilteredViewSet.
            return super(EstablishmentFilteredViewSet, self).get_queryset()
        
        # Usuários regulares (gerentes)
        if not hasattr(self.request.user, 'perfil') or not self.request.user.perfil.estabelecimento:
            raise PermissionDenied("Seu perfil de usuário não está vinculado a um estabelecimento.")
        
        # Usuário regular (gestor) vê apenas os objetos do seu estabelecimento.
        # Assume que o modelo tem um campo 'estabelecimento' Foreign Key diretamente.
        # Novamente, chama o get_queryset do ModelViewSet e filtra.
        return super(EstablishmentFilteredViewSet, self).get_queryset().filter(estabelecimento=self.request.user.perfil.estabelecimento)

    def perform_create(self, serializer):
        # Lógica para atribuir o estabelecimento na criação, adaptada para Cardapio.
        if not self.request.user.is_authenticated:
            raise PermissionDenied("Usuário não autenticado para criar.")

        final_establishment = None
        if self.request.user.is_superuser:
            # Superusuário: pode fornecer um 'estabelecimento' no payload (UUID).
            provided_establishment_id = self.request.data.get('estabelecimento')
            if provided_establishment_id:
                try:
                    final_establishment = Estabelecimento.objects.get(id=provided_establishment_id)
                except Estabelecimento.DoesNotExist:
                    raise ValidationError({"estabelecimento": "Estabelecimento fornecido não encontrado."})
            elif hasattr(self.request.user, 'perfil') and self.request.user.perfil.estabelecimento:
                final_establishment = self.request.user.perfil.estabelecimento
            else:
                raise ValidationError({"detail": "Superusuário deve fornecer o ID do estabelecimento ou estar vinculado a um."})
        else:
            # Usuário comum: usa o estabelecimento do seu perfil.
            if not hasattr(self.request.user, 'perfil') or not self.request.user.perfil.estabelecimento:
                raise ValidationError({"detail": "Seu perfil de usuário não está vinculado a um estabelecimento."})
            final_establishment = self.request.user.perfil.estabelecimento
        
        # Salva o objeto injetando o estabelecimento.
        serializer.save(estabelecimento=final_establishment)

    def perform_update(self, serializer):
        # Lógica para garantir que o estabelecimento não seja alterado por não-superusuários.
        instance = self.get_object() # A instância original.

        if not self.request.user.is_superuser:
            # Usuários comuns não podem alterar o campo 'estabelecimento'.
            # A validação abaixo espera a instância do Estabelecimento no payload.
            if 'estabelecimento' in serializer.validated_data and \
               serializer.validated_data['estabelecimento'] != instance.estabelecimento:
                raise PermissionDenied("Você não tem permissão para alterar o estabelecimento de um objeto.")
            
            # Garante que o objeto que está sendo atualizado pertence ao estabelecimento do usuário logado.
            # Embora get_queryset já filtre, é uma camada extra de segurança.
            if instance.estabelecimento != self.request.user.perfil.estabelecimento:
                raise PermissionDenied("Você não tem permissão para atualizar um objeto que não pertence ao seu estabelecimento.")
        
        serializer.save()