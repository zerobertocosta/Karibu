# backend/usuarios/permissions.py

from rest_framework import permissions

class IsSuperuserOrCreateUserInOwnEstablishment(permissions.BasePermission):
    """
    Permite superusuários fazerem qualquer coisa.
    Permite gestores (autenticados, não superusuários) fazerem o seguinte:
    - Ver (listar, detalhar) usuários do seu próprio estabelecimento.
    - Criar usuários associados ao seu próprio estabelecimento.
    - Editar usuários associados ao seu próprio estabelecimento.
    """

    def has_permission(self, request, view):
        # 1. Superusuários sempre têm permissão total
        if request.user.is_superuser:
            return True
        
        # 2. Usuários não autenticados não têm permissão para nada (exceto login)
        if not request.user.is_authenticated:
            return False

        # 3. Para usuários autenticados (que não são superusuários):

        # Verifica se o usuário tem um perfil e se esse perfil tem um estabelecimento associado
        if not hasattr(request.user, 'perfil') or not request.user.perfil or not request.user.perfil.estabelecimento:
            # Se não tem perfil ou estabelecimento, não pode gerenciar usuários relacionados a estabelecimento
            return False
        
        gestor_establishment_id = str(request.user.perfil.estabelecimento.id)

        # Permissão para ações de LEITURA (GET, HEAD, OPTIONS)
        if request.method in permissions.SAFE_METHODS:
            return True # Permite que gestores vejam listas e detalhes (o queryset vai filtrar o que eles veem)

        # Permissão para ações de ESCRITA (POST, PUT, PATCH, DELETE)
        
        # Ações de CRIAR (POST)
        if view.action == 'create':
            # Obtém o ID do estabelecimento que está sendo enviado no corpo da requisição
            requested_establishment_id = request.data.get('perfil', {}).get('estabelecimento')
            
            # Se o estabelecimento for nulo ou vazio na requisição, um gestor NÃO pode criar
            if not requested_establishment_id:
                return False
            
            # Garante que o gestor só pode criar usuários para SEU PRÓPRIO estabelecimento
            # Converte para string para garantir a comparação de UUIDs
            if str(requested_establishment_id) == gestor_establishment_id:
                return True
            return False # Se tentar criar para outro estabelecimento
        
        # Para ações de ATUALIZAR (PUT, PATCH) e DELETAR (DELETE),
        # a permissão a nível de objeto (has_object_permission) é mais adequada.
        # has_permission retorna True aqui para permitir que has_object_permission seja chamado.
        return True # Permite que a validação continue para has_object_permission


    def has_object_permission(self, request, view, obj):
        # 1. Superusuários sempre têm permissão total sobre qualquer objeto
        if request.user.is_superuser:
            return True

        # 2. Usuários não autenticados não têm permissão para objetos
        if not request.user.is_authenticated:
            return False

        # 3. Para usuários autenticados (que não são superusuários):
        if not hasattr(request.user, 'perfil') or not request.user.perfil or not request.user.perfil.estabelecimento:
            return False

        gestor_establishment_id = str(request.user.perfil.estabelecimento.id)

        # O objeto (obj) é a instância do User que está sendo acessada/modificada.
        # Verifica se o usuário (obj) tem um perfil e se esse perfil tem um estabelecimento
        if hasattr(obj, 'perfil') and obj.perfil and obj.perfil.estabelecimento:
            # Permite o acesso se o estabelecimento do objeto for o mesmo do gestor logado
            return str(obj.perfil.estabelecimento.id) == gestor_establishment_id
        
        # Se o objeto não tem perfil ou estabelecimento, um gestor não tem permissão para ele.
        return False