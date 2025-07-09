# backend/core/permissions.py

from rest_framework import permissions
from rest_framework.exceptions import PermissionDenied

class IsAuthenticatedAndBelongsToEstablishment(permissions.BasePermission):
    """
    Permissão customizada que exige que o usuário esteja autenticado E
    que esteja vinculado a um Estabelecimento através do seu Perfil.
    Superusuários (admin) são sempre permitidos.
    """
    message = "Você não tem permissão para acessar este recurso, pois não está vinculado a um estabelecimento ou não tem um perfil válido."

    def has_permission(self, request, view):
        # Permite acesso para superusuários (administradores do sistema)
        if request.user and request.user.is_superuser:
            return True

        # Exige que o usuário esteja autenticado
        if not request.user or not request.user.is_authenticated:
            return False

        # Exige que o usuário tenha um perfil e que este perfil esteja vinculado a um estabelecimento
        # 'perfil' é o related_name da OneToOneField no modelo Perfil
        if hasattr(request.user, 'perfil') and request.user.perfil.estabelecimento:
            return True

        return False