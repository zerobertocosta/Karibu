# backend/karibu/usuarios/views.py

from django.contrib.auth import get_user_model
from rest_framework import viewsets, status
from rest_framework.permissions import IsAuthenticated, DjangoModelPermissions # Removido AllowAny se não for usado
from rest_framework.response import Response
from django_filters.rest_framework import DjangoFilterBackend

# Importe seus models e serializers do aplicativo 'usuarios'
# REMOVA 'Funcao' daqui!
from .models import Perfil, Estabelecimento 
from .serializers import (
    UsuarioSerializer, 
    PerfilSerializer, 
    EstabelecimentoSerializer, 
    # REMOVA FuncaoSerializer daqui!
)

# Importe sua permissão personalizada EstablishmentPermission
from .permissions import EstablishmentPermission 

User = get_user_model() 

# ViewSet para Gerenciamento de Usuários (sem mudanças neste)
class UsuarioViewSet(viewsets.ModelViewSet):
    queryset = User.objects.all().order_by('id')
    serializer_class = UsuarioSerializer
    permission_classes = [IsAuthenticated, DjangoModelPermissions, EstablishmentPermission] 
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ['id', 'username', 'email', 'perfil__estabelecimento', 'is_active'] 

    def get_queryset(self):
        user = self.request.user
        if user.is_superuser:
            return User.objects.all().order_by('id')
        if hasattr(user, 'perfil') and user.perfil.estabelecimento:
            return User.objects.filter(perfil__estabelecimento=user.perfil.estabelecimento).order_by('id')
        return User.objects.none()

# ViewSet para Gerenciamento de Perfis (sem mudanças neste)
class PerfilViewSet(viewsets.ModelViewSet):
    queryset = Perfil.objects.all()
    serializer_class = PerfilSerializer
    permission_classes = [IsAuthenticated, DjangoModelPermissions, EstablishmentPermission] 
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ['estabelecimento', 'funcao'] 

    def get_queryset(self):
        user = self.request.user
        if user.is_superuser:
            return Perfil.objects.all()
        if hasattr(user, 'perfil') and user.perfil.estabelecimento:
            return Perfil.objects.filter(estabelecimento=user.perfil.estabelecimento)
        return Perfil.objects.none()

# ViewSet para Gerenciamento de Estabelecimentos (sem mudanças neste)
class EstabelecimentoViewSet(viewsets.ModelViewSet):
    queryset = Estabelecimento.objects.all()
    serializer_class = EstabelecimentoSerializer
    permission_classes = [IsAuthenticated, DjangoModelPermissions]

# REMOVA O BLOCO INTEIRO DE FuncaoViewSet ABAIXO
# class FuncaoViewSet(viewsets.ModelViewSet):
#    queryset = Funcao.objects.all()
#    serializer_class = FuncaoSerializer
#    permission_classes = [IsAuthenticated]