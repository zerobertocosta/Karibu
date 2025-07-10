# backend/usuarios/permissions.py

from rest_framework import permissions

class IsManagerOrSuperuser(permissions.BasePermission):
    """
    Permissão customizada que permite acesso apenas a superusuários
    ou a usuários que são gerentes (is_gestor=True) e pertencem
    ao mesmo estabelecimento. Utilizada para ações de LISTAR e CRIAR usuários.
    """
    message = "Você não tem permissão para realizar esta ação."

    def has_permission(self, request, view):
        # Superusuários sempre têm permissão
        if request.user and request.user.is_superuser:
            return True

        # Gerentes (is_gestor) têm permissão (a filtragem do queryset é responsabilidade do ViewSet)
        if request.user and hasattr(request.user, 'perfil') and request.user.perfil.is_gestor: # Corrigido para is_gestor
            return True
        
        # Negar para outros tipos de usuários (garçom, cozinheiro, caixa)
        return False

class IsSelfOrManagerOrSuperuser(permissions.BasePermission):
    """
    Permissão customizada para permitir que:
    1. Superusuário edite/delete qualquer usuário.
    2. Gerente edite/delete usuários do SEU estabelecimento (já filtrado pelo ViewSet).
    3. Usuário edite/delete seu próprio perfil.
    Utilizada para ações de DETALHE, ATUALIZAÇÃO e EXCLUSÃO de usuários.
    """
    message = "Você não tem permissão para realizar esta ação neste usuário."

    def has_object_permission(self, request, view, obj):
        # Superusuários podem fazer qualquer coisa
        if request.user and request.user.is_superuser:
            return True

        # Gerentes (is_gestor) podem editar usuários do seu próprio estabelecimento e a si mesmos
        if request.user and hasattr(request.user, 'perfil') and request.user.perfil.is_gestor: # Corrigido para is_gestor
            # O objeto 'obj' aqui é o usuário que está sendo acessado.
            # Se o usuário acessado (obj) tem um perfil e pertence ao mesmo estabelecimento do gerente
            if hasattr(obj, 'perfil') and obj.perfil and obj.perfil.estabelecimento == request.user.perfil.estabelecimento:
                return True
            # Ou se o gerente está tentando acessar seu próprio perfil
            if obj == request.user:
                return True
        
        # Usuário pode editar/ver seu próprio perfil
        if obj == request.user:
            return True
            
        return False

class IsSuperuserOrCreateUserInOwnEstablishment(permissions.BasePermission):
    """
    Permite superusuários fazerem qualquer coisa.
    Permite gestores (autenticados, não superusuários) fazerem o seguinte:
    - Ver (listar, detalhar) usuários do seu próprio estabelecimento.
    - Criar usuários associados ao seu próprio estabelecimento.
    - Editar usuários associados ao seu próprio estabelecimento.

    NOTA: Para "listar" usuários, esta permissão deve ser usada em conjunto
    com `IsManagerOrSuperuser` ou `get_queryset` para restringir quem pode
    ver a lista em primeiro lugar. Esta permissão é mais focada em `create`
    e `has_object_permission`.
    """
    def has_permission(self, request, view):
        # 1. Superusuários sempre têm permissão total
        if request.user.is_superuser:
            return True
        
        # 2. Usuários não autenticados não têm permissão para nada (exceto login)
        if not request.user.is_authenticated:
            return False
        
        # 3. Para usuários autenticados (que não são superusuários):
        if not hasattr(request.user, 'perfil') or not request.user.perfil or not request.user.perfil.estabelecimento:
            # Se não tem perfil ou estabelecimento, não pode gerenciar usuários relacionados a estabelecimento
            return False
        
        # Adição de verificação se o usuário é gestor para usar esta permissão
        if not request.user.perfil.is_gestor: # Apenas gestores (além de superusers) podem usar esta permissão
            return False

        gestor_establishment_id = str(request.user.perfil.estabelecimento.id)

        # Permissão para ações de LEITURA (GET, HEAD, OPTIONS)
        # ESTE BLOCO AGORA SERÁ MAIS RESTRITO PELO get_permissions NO VIEWS.PY
        # Aqui, mantemos para 'retrieve' se for o caso de um gerente ver um usuário específico
        if request.method in permissions.SAFE_METHODS:
            return True # A permissão de listagem será gerenciada pelo IsManagerOrSuperuser

        # Permissão para ações de ESCRITA (POST, PUT, PATCH, DELETE)
        # Ações de CRIAR (POST)
        if view.action == 'create':
            requested_establishment_id = None
            if 'perfil' in request.data and 'estabelecimento' in request.data['perfil']:
                requested_establishment_id = request.data['perfil']['estabelecimento']
            elif 'estabelecimento' in request.data: # Se o campo for direto no UserSerializer
                 requested_establishment_id = request.data['estabelecimento']

            if not requested_establishment_id:
                # Permite que o EstablishmentFilteredViewSet insira o estabelecimento para gestores
                return True 

            # Garante que o gestor só pode criar usuários para SEU PRÓPRIO estabelecimento
            if str(requested_establishment_id) == gestor_establishment_id:
                return True
            return False 
        
        return True

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
        
        # Adição de verificação se o usuário é gestor para usar esta permissão
        if not request.user.perfil.is_gestor: # Apenas gestores (além de superusers) podem usar esta permissão
            # No caso de has_object_permission, o próprio usuário pode ter acesso a si mesmo,
            # então esta negação direta precisa ser feita com cuidado.
            # A lógica IsSelfOrManagerOrSuperuser já cuida disso.
            # Esta permissão é mais para gerenciar OUTROS usuários.
            pass # Deixa IsSelfOrManagerOrSuperuser cuidar de quem pode ver o próprio perfil
        
        gestor_establishment_id = str(request.user.perfil.estabelecimento.id)

        # O objeto (obj) é a instância do User que está sendo acessada/modificada.
        # Verifica se o usuário (obj) tem um perfil e se esse perfil tem um estabelecimento
        if hasattr(obj, 'perfil') and obj.perfil and obj.perfil.estabelecimento:
            # Permite o acesso se o estabelecimento do objeto for o mesmo do gestor logado
            return str(obj.perfil.estabelecimento.id) == gestor_establishment_id
        
        return False