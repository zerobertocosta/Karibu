# backend/cliente/permissions.py
from rest_framework import permissions

class IsOwnerOrManager(permissions.BasePermission):
    """
    Permissão customizada para permitir que apenas o proprietário do perfil (cliente)
    ou um gestor/superusuário possa ver/editar/excluir o perfil.
    """

    def has_object_permission(self, request, view, obj):
        # Permissões de leitura são permitidas para qualquer solicitação GET, HEAD ou OPTIONS.
        if request.method in permissions.SAFE_METHODS:
            # Se a requisição for de leitura, um cliente só pode ver o seu próprio perfil.
            # Um gestor/superusuário pode ver qualquer perfil.
            if hasattr(request.user, 'perfil') and request.user.perfil.is_gestor:
                return True # Gestores podem ver todos
            return obj.celular == request.user.username # Assumindo que o username do usuário é o celular

        # Permissões de escrita (PUT, PATCH, DELETE) são permitidas apenas para o proprietário do objeto
        # ou para gestores/superusuários.
        if request.user.is_superuser:
            return True # Superusuários têm acesso total

        # Verifica se o usuário logado tem um perfil e se ele é um gestor
        if hasattr(request.user, 'perfil') and request.user.perfil.is_gestor:
            return True # Gestores podem editar/deletar clientes

        # Se não for gestor nem superusuário, o usuário deve ser o próprio cliente do objeto
        # e o celular do objeto deve ser igual ao username do usuário autenticado (que é o celular).
        # Para PUT/PATCH, permite se for o próprio cliente e o método não for DELETE
        if request.method in ['PUT', 'PATCH']:
            return obj.celular == request.user.username
        
        # Para DELETE, o cliente não pode se deletar
        if request.method == 'DELETE':
            return False # Clientes não podem deletar seus próprios perfis via API (somente gestores/superusuários)

        return False # Nega todas as outras requisições por padrão