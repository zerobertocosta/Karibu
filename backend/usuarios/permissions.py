# backend/usuarios/permissions.py (CORRIGIDO)

from rest_framework import permissions

class IsManagerOrSuperuser(permissions.BasePermission):
    """
    Permissão customizada que permite acesso apenas a superusuários ou a usuários que são gerentes (is_gestor=True).
    Utilizada para ações de LISTAR e CRIAR usuários.
    """
    message = "Você não tem permissão para realizar esta ação."

    def has_permission(self, request, view):
        if request.user and request.user.is_superuser:
            return True
        if request.user and hasattr(request.user, 'perfil') and request.user.perfil.is_gestor:
            return True
        return False

class IsSelfOrManagerOrSuperuser(permissions.BasePermission):
    """
    Permissão customizada para permitir que:
    1. Superusuário edite/delete qualquer usuário.
    2. Gerente edite/delete usuários do SEU estabelecimento.
    3. Usuário edite/delete seu próprio perfil.
    Utilizada para ações de DETALHE, ATUALIZAÇÃO e EXCLUSÃO de usuários.
    """
    message = "Você não tem permissão para realizar esta ação neste usuário."

    def has_object_permission(self, request, view, obj):
        if request.user and request.user.is_superuser:
            return True
        
        # Usuário pode editar/ver seu próprio perfil
        if obj == request.user:
            return True

        # Gerentes (is_gestor) podem editar usuários do seu próprio estabelecimento
        if request.user and hasattr(request.user, 'perfil') and request.user.perfil.is_gestor:
            # Se o usuário acessado (obj) tem um perfil e pertence ao mesmo estabelecimento do gerente
            if hasattr(obj, 'perfil') and obj.perfil and obj.perfil.estabelecimento == request.user.perfil.estabelecimento:
                return True
        
        return False

class IsSuperuserOrCreateUserInOwnEstablishment(permissions.BasePermission):
    """
    Permite superusuários fazerem qualquer coisa.
    Permite gestores (autenticados, não superusuários) fazerem o seguinte:
    - Criar usuários associados ao seu próprio estabelecimento (o EstablishmentFilteredViewSet injetará o ID).
    - Editar usuários associados ao seu próprio estabelecimento.
    """
    message = "Você não tem permissão para realizar esta ação."

    def has_permission(self, request, view):
        # 1. Superusuários sempre têm permissão total
        if request.user.is_superuser:
            return True

        # 2. Usuários não autenticados não têm permissão para nada
        if not request.user.is_authenticated:
            return False

        # 3. Gerentes (is_gestor) autenticados (que não são superusuários)
        if hasattr(request.user, 'perfil') and request.user.perfil and request.user.perfil.is_gestor:
            # Para ações de criação (POST):
            # Apenas verifica se o gerente tem um estabelecimento. O ViewSet se encarregará
            # de vincular o usuário ao estabelecimento CORRETO do gerente.
            if view.action == 'create':
                return request.user.perfil.estabelecimento is not None
            
            # Para ações de leitura ou atualização (PUT/PATCH) será tratado em has_object_permission
            return True # Permite que has_object_permission seja chamado
        
        return False # Nega para outros papéis ou usuários sem perfil/estabelecimento

    def has_object_permission(self, request, view, obj):
        # 1. Superusuários sempre têm permissão total sobre qualquer objeto
        if request.user.is_superuser:
            return True

        # 2. Usuários não autenticados não têm permissão para objetos
        if not request.user.is_authenticated:
            return False

        # 3. Gerentes (is_gestor) autenticados (que não são superusuários):
        if hasattr(request.user, 'perfil') and request.user.perfil and request.user.perfil.estabelecimento:
            gestor_establishment_id = request.user.perfil.estabelecimento.id if request.user.perfil.estabelecimento else None
            
            # Permite o acesso se o objeto (usuário) for o próprio gestor
            if obj == request.user:
                return True
            
            # Permite o acesso se o objeto (usuário) pertence ao mesmo estabelecimento do gestor
            if hasattr(obj, 'perfil') and obj.perfil and obj.perfil.estabelecimento:
                return obj.perfil.estabelecimento.id == gestor_establishment_id
        
        return False # Nega para outros casos