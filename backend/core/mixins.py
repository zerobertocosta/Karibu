# backend/core/mixins.py

from rest_framework import status
from rest_framework.response import Response
from rest_framework.exceptions import PermissionDenied, ValidationError

class EstablishmentFilteredViewSet:
    """
    Mixin para ViewSets que filtra automaticamente o queryset com base
    no estabelecimento do usuário logado.
    Permite que superusuários vejam todos os dados.
    """
    def get_queryset(self):
        # Garante que o usuário está autenticado e tem um perfil.
        if not self.request.user.is_authenticated:
            raise PermissionDenied("Usuário não autenticado.")

        # Superusuários (admins) podem ver todos os dados de todos os estabelecimentos.
        if self.request.user.is_superuser:
            return super().get_queryset()

        # Usuários regulares só podem ver dados do seu próprio estabelecimento.
        if not hasattr(self.request.user, 'perfil') or not self.request.user.perfil.estabelecimento:
            # Isso não deveria acontecer se a permissão IsAuthenticatedAndBelongsToEstablishment estiver funcionando,
            # mas é uma boa verificação de segurança.
            raise PermissionDenied("Seu perfil de usuário não está vinculado a um estabelecimento.")

        # Assume que o modelo tem um campo 'estabelecimento' ForeignKey
        # para o modelo Estabelecimento.
        queryset = super().get_queryset().filter(
            estabelecimento=self.request.user.perfil.estabelecimento
        )
        return queryset

    def perform_create(self, serializer):
        """
        Ao criar um objeto, garante que ele seja vinculado ao estabelecimento
        do usuário logado.
        """
        if not self.request.user.is_authenticated:
            raise PermissionDenied("Usuário não autenticado para criar.")

        if not self.request.user.is_superuser:
            if not hasattr(self.request.user, 'perfil') or not self.request.user.perfil.estabelecimento:
                raise ValidationError({"detail": "Seu perfil de usuário não está vinculado a um estabelecimento."})
            # Define o campo 'estabelecimento' no objeto antes de salvar
            serializer.save(estabelecimento=self.request.user.perfil.estabelecimento)
        else:
            # Para superusuários, o campo 'estabelecimento' deve ser fornecido explicitamente no request
            # ou o serializer.create() deve lidar com isso.
            # Aqui, para manter a simplicidade, assumimos que o superusuário pode criar sem especificar
            # e o serializer pode ter um default ou ele pode ser passado.
            # Em cenários reais, superusuários criando dados multi-tenant precisariam especificar o estabelecimento.
            # Por enquanto, deixamos o serializer salvar como vier ou o super().perform_create lidar.
            super().perform_create(serializer)


    def perform_update(self, serializer):
        """
        Ao atualizar um objeto, garante que o usuário não mude o estabelecimento
        e que o objeto pertence ao seu estabelecimento (já garantido por get_queryset).
        """
        # A lógica de get_queryset já impede que o usuário acesse objetos de outros estabelecimentos.
        # Aqui, podemos adicionar uma validação extra se o campo 'estabelecimento' for alterável
        # no serializer e não quisermos que ele seja alterado após a criação por usuários comuns.
        if not self.request.user.is_superuser and 'estabelecimento' in serializer.validated_data:
            # Impede que usuários não-super alterem o campo de estabelecimento.
            # O campo 'estabelecimento' geralmente não deve ser editável após a criação.
            if serializer.validated_data['estabelecimento'] != self.request.user.perfil.estabelecimento:
                 raise ValidationError({"detail": "Você não tem permissão para alterar o estabelecimento deste item."})
        super().perform_update(serializer)

    def perform_destroy(self, instance):
        """
        Ao deletar um objeto, garante que o objeto pertence ao estabelecimento
        do usuário (já garantido por get_queryset).
        """
        # A lógica de get_queryset já impede acesso a objetos de outros estabelecimentos.
        # Nenhuma validação extra é estritamente necessária aqui, mas pode ser adicionada
        # para regras de negócio específicas (ex: não permitir deletar se houver pedidos ativos).
        super().perform_destroy(instance)