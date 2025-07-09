# backend/usuarios/views.py

from rest_framework import viewsets, permissions
from django.contrib.auth.models import User
from .models import Perfil
from .serializers import UserSerializer, PerfilSerializer, PerfilWriteSerializer
from core.mixins import EstablishmentFilteredViewSet # Importar o mixin

# ViewSet para o modelo User (do Django)
class UserViewSet(viewsets.ModelViewSet):
    """
    ViewSet para gerenciar usuários.
    Por padrão, apenas superusuários podem gerenciar todos os usuários.
    A lógica para gerenciar usuários dentro de um estabelecimento específico
    por um gerente de estabelecimento (não superuser) precisaria ser implementada
    com uma permissão/filtro mais granular aqui.
    """
    queryset = User.objects.all().select_related('perfil__estabelecimento') # Otimiza o carregamento do perfil
    serializer_class = UserSerializer
    # Por enquanto, apenas superusuários podem listar/criar/editar/deletar usuários.
    # A gestão de usuários por gerentes de estabelecimento é uma funcionalidade a ser refinada.
    permission_classes = [permissions.IsAdminUser]

    # Sobrescreve get_queryset para superusuários verem todos os detalhes e
    # talvez um dia para não-superusuários verem apenas alguns dados de user.
    # Por agora, IsAdminUser já restringe bem.

# ViewSet para o modelo Perfil, usando o mixin de multi-tenancy
class PerfilViewSet(EstablishmentFilteredViewSet, viewsets.ModelViewSet):
    """
    ViewSet para gerenciar Perfis de Usuário.
    Hereda de EstablishmentFilteredViewSet para garantir que apenas perfis
    do estabelecimento do usuário logado sejam acessíveis e criados corretamente.
    """
    queryset = Perfil.objects.all().select_related('estabelecimento', 'user')
    serializer_class = PerfilSerializer

    def get_serializer_class(self):
        # Usa PerfilWriteSerializer para escrita (POST/PUT/PATCH) para permitir user/estabelecimento
        # e PerfilSerializer para leitura (GET) para aninhar Estabelecimento.
        if self.action in ['create', 'update', 'partial_update']:
            return PerfilWriteSerializer
        return PerfilSerializer

    def perform_create(self, serializer):
        # O EstablishmentFilteredViewSet.perform_create já deve cuidar do 'estabelecimento'.
        # Aqui precisamos garantir que o 'user' seja passado.
        # Geralmente, a criação de Perfil é atrelada à criação de User.
        # Este ViewSet seria mais para editar perfis existentes ou criar perfis
        # para usuários já existentes onde o perfil é opcional/separado.
        # Se for criar um perfil para um usuário, o 'user' deve vir no request.
        # Para um gerenciamento mais robusto, um fluxo de criação de usuário/perfil
        # combinado seria ideal (ex: usando um Nested Serializer writeable).

        # Para superusuários criando um perfil, 'user' e 'estabelecimento' devem ser fornecidos.
        # Para usuários normais, 'user' deve ser o próprio request.user e 'estabelecimento'
        # será automaticamente definido pelo mixin.

        if self.request.user.is_superuser:
            # Superusuários devem fornecer user_id e estabelecimento_id
            serializer.save()
        else:
            # Usuários não super podem criar/atualizar seu próprio perfil,
            # ou um gerente pode criar para um usuário do seu estabelecimento.
            # O mixin já cuida do 'estabelecimento'. Precisamos garantir que o 'user'
            # seja o correto para o perfil.
            if 'user' not in serializer.validated_data:
                # Se 'user' não foi fornecido, associa ao usuário logado.
                # Isso pode ser perigoso se um gerente puder alterar o perfil de qualquer um.
                # Um fluxo mais seguro seria vincular o Perfil à criação de um User.
                serializer.save(user=self.request.user, estabelecimento=self.request.user.perfil.estabelecimento)
            else:
                 # Se 'user' for fornecido (ex: por gerente), valida se o user pertence ao estabelecimento
                 # Ou se o user é o próprio request.user.
                 target_user = serializer.validated_data['user']
                 if not self.request.user.is_superuser and \
                    (not hasattr(target_user, 'perfil') or \
                     target_user.perfil.estabelecimento != self.request.user.perfil.estabelecimento):
                     raise permissions.PermissionDenied("Você não pode criar/editar o perfil de um usuário fora do seu estabelecimento.")
                 serializer.save(estabelecimento=self.request.user.perfil.estabelecimento)