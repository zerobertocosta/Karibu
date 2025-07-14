# backend/mesas/mixins.py (CÓDIGO COMPLETO - GARANTA QUE ESTÁ ASSIM)

from rest_framework.exceptions import PermissionDenied

class MesaEstablishmentMixin:
    """
    Mixin específico para o ViewSet de Mesa.
    Garante que as operações de listagem de Mesa sejam vinculadas ao estabelecimento do usuário autenticado.
    """
    def get_queryset(self):
        if not self.request.user.is_authenticated:
            raise PermissionDenied("Usuário não autenticado.")

        if self.request.user.is_superuser:
            return super().get_queryset()

        if not hasattr(self.request.user, 'perfil') or not self.request.user.perfil.estabelecimento:
            raise PermissionDenied("Seu perfil de usuário não está vinculado a um estabelecimento.")

        # Filtra as mesas para mostrar apenas as do estabelecimento do usuário logado.
        return super().get_queryset().filter(estabelecimento=self.request.user.perfil.estabelecimento)

    # REMOVA qualquer perform_create, perform_update, perform_destroy que estava aqui.
    # Essas lógicas agora estarão na classe de permissão ou no perform_create do ViewSet.