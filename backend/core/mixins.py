from rest_framework import status
from rest_framework.response import Response
from rest_framework.exceptions import PermissionDenied, ValidationError

class EstablishmentFilteredViewSet:
    """
    Mixin para ViewSets que filtra automaticamente o queryset com base no estabelecimento do usuário logado.
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
            raise PermissionDenied("Seu perfil de usuário não está vinculado a um estabelecimento.")

        # Assume que o modelo tem um campo 'estabelecimento' ForeignKey
        # para o modelo Estabelecimento (através do Perfil).
        queryset = super().get_queryset().filter(
            perfil__estabelecimento=self.request.user.perfil.estabelecimento
        )
        return queryset

    def perform_create(self, serializer):
        """
        Ao criar um objeto, garante que ele seja vinculado ao estabelecimento do usuário logado.
        """
        if not self.request.user.is_authenticated:
            raise PermissionDenied("Usuário não autenticado para criar.")

        if not self.request.user.is_superuser:
            if not hasattr(self.request.user, 'perfil') or not self.request.user.perfil.estabelecimento:
                raise ValidationError({"detail": "Seu perfil de usuário não está vinculado a um estabelecimento."})
            
            user_establishment = self.request.user.perfil.estabelecimento

            # Para o UserSerializer, precisamos injetar o estabelecimento DENTRO do perfil_data.
            # É crucial passar a INSTÂNCIA do objeto Estabelecimento, não apenas o ID.
            if 'perfil' not in serializer.validated_data:
                serializer.validated_data['perfil'] = {}
            
            # Garante que o estabelecimento no perfil do novo usuário seja o mesmo do gerente
            # Passa a instância completa do objeto Estabelecimento
            serializer.validated_data['perfil']['estabelecimento'] = user_establishment
            
        # Para superusuários, o serializer.save() será chamado sem argumentos adicionais,
        # e o campo 'estabelecimento' (se aplicável) deve vir diretamente do request.data
        # ou ser tratado com defaults no serializer.
        # Para usuários comuns (gerentes), as modificações em validated_data já foram feitas acima.
        serializer.save()

    def perform_update(self, serializer):
        """
        Ao atualizar um objeto, garante que o usuário não mude o estabelecimento e que o objeto pertence ao seu estabelecimento (já garantido por get_queryset).
        """
        # A lógica de get_queryset já impede que o usuário acesse objetos de outros estabelecimentos.
        # Aqui, podemos adicionar uma validação extra se o campo 'estabelecimento' for alterável
        # no serializer e não quisermos que ele seja alterado após a criação por usuários comuns.
        
        # A validação precisa comparar a instância do Estabelecimento.
        if not self.request.user.is_superuser and \
           'perfil' in serializer.validated_data and \
           'estabelecimento' in serializer.validated_data['perfil']:
            
            # Pega o estabelecimento validado (que pode ser uma instância ou um ID dependendo do SerializerField)
            validated_establishment = serializer.validated_data['perfil']['estabelecimento']
            
            # Se for um PrimaryKeyRelatedField, validated_establishment já será a instância do objeto.
            # Se for um UUIDField e o serializer permitir