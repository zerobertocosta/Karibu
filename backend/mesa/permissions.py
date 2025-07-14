# backend/mesas/permissions.py (CÓDIGO COMPLETO - ATUALIZADO PARA BLOQUEAR VISUALIZAÇÃO)
from rest_framework import permissions
from core.permissions import IsAuthenticatedAndBelongsToEstablishment

class IsGestorForMesaOperations(IsAuthenticatedAndBelongsToEstablishment):
    """
    Permissão específica para operações em Mesas.
    Hereda de IsAuthenticatedAndBelongsToEstablishment para garantir autenticação e vínculo com estabelecimento.
    Exige que o usuário seja um 'Gestor' para TODAS as operações (visualização e escrita).
    """
    message = "Você não tem permissão para realizar esta ação (apenas Gestores ou Superusuários podem gerenciar mesas)."

    def has_permission(self, request, view):
        # Primeiro, executa a verificação da permissão base (IsAuthenticatedAndBelongsToEstablishment)
        # para garantir que o usuário está autenticado e tem um perfil/estabelecimento.
        if not super().has_permission(request, view):
            return False

        # Superusuários (admins) sempre têm permissão total.
        if request.user.is_superuser:
            return True

        # Para todas as operações (leitura e escrita), exige que seja um Gestor.
        # REMOVIDA a condição 'if request.method in permissions.SAFE_METHODS:'
        # Agora, qualquer método exige ser gestor ou superusuário.
        if hasattr(request.user, 'perfil') and request.user.perfil and request.user.perfil.is_gestor:
            return True

        # Nega se não for superusuário e não for gestor.
        return False

    def has_object_permission(self, request, view, obj):
        # Permissões baseadas no objeto (para PUT, PATCH, DELETE em uma mesa específica)
        # Primeiro, executa a verificação da permissão base (autenticado e com estabelecimento).
        if not super().has_object_permission(request, view, obj):
            return False

        # Superusuários sempre têm permissão total sobre qualquer objeto.
        if request.user.is_superuser:
            return True

        # Para todas as operações (leitura e escrita) no objeto específico,
        # exige que o usuário seja um Gestor E que o objeto (mesa) pertença
        # ao mesmo estabelecimento do Gestor logado.
        # REMOVIDA a condição 'if request.method in permissions.SAFE_METHODS:'
        if hasattr(request.user, 'perfil') and request.user.perfil and request.user.perfil.is_gestor:
            if obj.estabelecimento == request.user.perfil.estabelecimento:
                return True

        # Nega se não atender às condições acima.
        return False