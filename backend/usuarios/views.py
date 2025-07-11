# backend/usuarios/views.py
from rest_framework import viewsets, permissions, status
from rest_framework.decorators import action
from rest_framework.response import Response

from django.contrib.auth import get_user_model
from .models import Perfil 
from configuracao.models import Estabelecimento 

from .serializers import UserSerializer, PerfilSerializer, EstabelecimentoSerializer 

from .permissions import IsManagerOrSuperuser, IsSelfOrManagerOrSuperuser, IsSuperuserOrCreateUserInOwnEstablishment 
from core.mixins import EstablishmentFilteredViewSet 

User = get_user_model() 

class UsuarioViewSet(EstablishmentFilteredViewSet, viewsets.ModelViewSet):
    """
    ViewSet para o modelo User (padrão do Django).
    - Superusuários veem e gerenciam todos os usuários.
    - Gerentes veem e gerenciam APENAS usuários do seu próprio estabelecimento.
    - Outros papéis (Garçons, Cozinheiros, Caixas) NÃO podem listar ou gerenciar outros usuários.
    - Qualquer usuário pode ver/editar seu próprio perfil via a ação 'me'.
    """
    serializer_class = UserSerializer

    def get_permissions(self):
        """ Instancia e retorna a lista de permissões que esta view requer. """
        if self.action in ['list', 'create']:
            self.permission_classes = [IsManagerOrSuperuser, IsSuperuserOrCreateUserInOwnEstablishment]
        elif self.action in ['retrieve', 'update', 'partial_update', 'destroy']:
            self.permission_classes = [IsSelfOrManagerOrSuperuser]
        elif self.action == 'me': 
            self.permission_classes = [permissions.IsAuthenticated]
        else: 
            self.permission_classes = [permissions.IsAuthenticated] 
        return [permission() for permission in self.permission_classes]

    def get_queryset(self):
        if self.request.user.is_superuser:
            return User.objects.all().select_related('perfil__estabelecimento') 
        
        if hasattr(self.request.user, 'perfil') and self.request.user.perfil.is_gestor:
            return User.objects.filter(perfil__estabelecimento=self.request.user.perfil.estabelecimento).select_related('perfil__estabelecimento')
        
        return User.objects.none()

    # O MÉTODO perform_create CUSTOMIZADO FOI REMOVIDO DAQUI!
    # O ModelViewSet padrão chamará o método create do seu UserSerializer,
    # que já lida corretamente com a criação do Perfil e a vinculação do Estabelecimento
    # a partir do UUID fornecido.

    @action(detail=False, methods=['get'], permission_classes=[permissions.IsAuthenticated])
    def me(self, request):
        """
        Retorna os detalhes do usuário autenticado e seu perfil.
        Endpoint: /api/usuarios/users/me/
        """
        if not request.user.is_authenticated:
            return Response({'detail': 'Não autenticado.'}, status=status.HTTP_401_UNAUTHORIZED)
        
        serializer = self.get_serializer(request.user)
        return Response(serializer.data)

class PerfilViewSet(EstablishmentFilteredViewSet, viewsets.ModelViewSet):
    """
    ViewSet para o modelo Perfil.
    """
    queryset = Perfil.objects.all().select_related('user', 'estabelecimento') 
    serializer_class = PerfilSerializer

    def get_permissions(self):
        """ Instancia e retorna a lista de permissões que esta view requer. """
        if self.action in ['list', 'create']:
            self.permission_classes = [IsManagerOrSuperuser]
        elif self.action in ['retrieve', 'update', 'partial_update', 'destroy']:
            self.permission_classes = [IsSelfOrManagerOrSuperuser]
        else:
            self.permission_classes = [permissions.IsAuthenticated]
        return [permission() for permission in self.permission_classes]

class EstabelecimentoViewSet(viewsets.ModelViewSet):
    """
    ViewSet para o modelo Estabelecimento.
    """
    serializer_class = EstabelecimentoSerializer
    queryset = Estabelecimento.objects.all() 

    def get_permissions(self):
        """ Define as permissões baseadas na ação. """
        if self.action in ['list', 'retrieve']: 
            self.permission_classes = [permissions.IsAuthenticated]
        elif self.action in ['create', 'update', 'partial_update', 'destroy']: 
            self.permission_classes = [permissions.IsAdminUser] 
        else:
            self.permission_classes = [permissions.IsAuthenticated]
        return [permission() for permission in self.permission_classes]

    def get_queryset(self):
        """ Filtra o queryset de estabelecimentos baseado no papel do usuário. """
        if self.request.user.is_superuser:
            return Estabelecimento.objects.all()
        
        if self.request.user.is_authenticated and \
           hasattr(self.request.user, 'perfil') and \
           self.request.user.perfil.estabelecimento:
            return Estabelecimento.objects.filter(id=self.request.user.perfil.estabelecimento.id)
        
        return Estabelecimento.objects.none()