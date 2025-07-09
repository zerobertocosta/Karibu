# backend/karibu/usuarios/permissions.py

from rest_framework import permissions

class EstablishmentPermission(permissions.BasePermission):
    """
    Permissão personalizada para permitir que apenas usuários relacionados
    ao mesmo estabelecimento possam visualizar/editar objetos.
    Superusuários têm acesso total.
    """

    def has_permission(self, request, view):
        # Permite acesso para superusuários em qualquer listagem ou criação
        if request.user.is_superuser:
            return True
        
        # Para operações de listagem (GET), permite se o usuário estiver autenticado
        # e tiver um perfil com estabelecimento.
        # A filtragem real será feita no get_queryset do ViewSet.
        if view.action == 'list':
            return request.user.is_authenticated and hasattr(request.user, 'perfil') and request.user.perfil.estabelecimento is not None
        
        # Para outras operações (retrieve, update, destroy, create), 
        # a verificação mais detalhada é feita em has_object_permission.
        return request.user.is_authenticated

    def has_object_permission(self, request, view, obj):
        # Permite acesso para superusuários em qualquer objeto
        if request.user.is_superuser:
            return True

        # Se o objeto tiver um campo 'estabelecimento' diretamente
        if hasattr(obj, 'estabelecimento'):
            return obj.estabelecimento == request.user.perfil.estabelecimento
        
        # Se o objeto for um 'User' e tiver um 'perfil' que tem 'estabelecimento'
        # Isso é crucial para o UsuarioViewSet
        if hasattr(obj, 'perfil') and hasattr(obj.perfil, 'estabelecimento'):
            return obj.perfil.estabelecimento == request.user.perfil.estabelecimento
            
        # Para o modelo Perfil, o próprio perfil já tem o campo 'estabelecimento'
        # então o primeiro 'if hasattr(obj, 'estabelecimento')' já lida com isso.

        # Negar por padrão se não houver lógica de correspondência
        return False