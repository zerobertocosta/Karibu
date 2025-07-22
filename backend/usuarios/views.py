# backend/usuarios/views.py

from rest_framework import viewsets, permissions, status
from rest_framework.decorators import action
from rest_framework.response import Response
from django.contrib.auth import get_user_model
from .models import Perfil # Importe Perfil
from configuracao.models import Estabelecimento, AssinaturaEstabelecimento # Importe AssinaturaEstabelecimento
from .serializers import UserSerializer, PerfilSerializer, EstabelecimentoSerializer # Importe todos os serializers
from .permissions import IsManagerOrSuperuser, IsSelfOrManagerOrSuperuser, IsSuperuserOrCreateUserInOwnEstablishment
from core.mixins import EstablishmentFilteredViewSet
# Importações para o TokenObtainPairView customizado
from rest_framework_simplejwt.views import TokenObtainPairView
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from datetime import date # Importar datetime.date para comparar datas

# >>> ESTA É A LINHA QUE PRECISA SER ADICIONADA <<<
from rest_framework import serializers 
# >>> FIM DA ADIÇÃO <<<

User = get_user_model()

class MyTokenObtainPairSerializer(TokenObtainPairSerializer):
    """
    Serializer customizado para o login, adicionando informações do perfil
    e fazendo a validação da assinatura do estabelecimento.
    """
    @classmethod
    def get_token(cls, user):
        token = super().get_token(user)

        if hasattr(user, 'perfil'):
            token['role'] = user.perfil.papel
            if user.perfil.estabelecimento:
                token['establishment_id'] = str(user.perfil.estabelecimento.id) # UUID precisa ser string
                token['establishment_name'] = user.perfil.estabelecimento.nome
        
        token['is_superuser'] = user.is_superuser

        return token

    def validate(self, attrs):
        data = super().validate(attrs)

        user = self.user

        if hasattr(user, 'perfil') and user.perfil.estabelecimento:
            estabelecimento = user.perfil.estabelecimento
            
            assinatura = AssinaturaEstabelecimento.objects.filter(
                estabelecimento=estabelecimento
            ).exclude(
                estado='FINALIZADA'
            ).order_by('-data_ativacao').first()

            if not assinatura:
                raise serializers.ValidationError(
                    {"detail": "Nenhuma assinatura ativa encontrada para este estabelecimento. Contate o suporte."}
                )

            if assinatura.estado == 'CANCELADA' or assinatura.estado == 'SUSPENSA':
                raise serializers.ValidationError(
                    {"detail": f"A assinatura do estabelecimento '{estabelecimento.nome}' está {assinatura.get_estado_display().lower()}. Acesso negado. Contate o suporte."}
                )
            
            if assinatura.data_desativacao and assinatura.data_desativacao < date.today():
                raise serializers.ValidationError(
                    {"detail": f"A assinatura do estabelecimento '{estabelecimento.nome}' expirou em {assinatura.data_desativacao.strftime('%d/%m/%Y')}. Acesso negado. Contate o suporte."}
                )
            
            data['subscription_status'] = assinatura.estado
            data['establishment_id'] = str(estabelecimento.id)
            data['is_superuser'] = user.is_superuser
            data['user_role'] = user.perfil.papel

        else:
            if not user.is_superuser:
                 raise serializers.ValidationError(
                    {"detail": "Seu usuário não está vinculado a um estabelecimento. Contate o administrador."}
                )
            data['is_superuser'] = user.is_superuser
            data['user_role'] = 'admin'
            data['establishment_id'] = None

        return data

class MyTokenObtainPairView(TokenObtainPairView):
    serializer_class = MyTokenObtainPairSerializer

class UsuarioViewSet(EstablishmentFilteredViewSet, viewsets.ModelViewSet):
    """ ViewSet para o modelo User (padrão do Django). ... """
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

    def update(self, request, *args, **kwargs):
        print("\n--- DEBUG UsuarioViewSet.update: Método update da ViewSet chamado! ---")
        print(f"Request data (dados recebidos na ViewSet): {request.data}")
        print(f"User making request: {request.user.username} (ID: {request.user.id})")
        partial = kwargs.pop('partial', False)
        instance = self.get_object()
        serializer = self.get_serializer(instance, data=request.data, partial=partial)
        print(f"--- DEBUG UsuarioViewSet.update: Chamando serializer.is_valid() ---")
        if serializer.is_valid(raise_exception=True):
            print(f"--- DEBUG UsuarioViewSet.update: serializer.is_valid() retornou TRUE. Validated data: {serializer.validated_data}")
            self.perform_update(serializer)
            print(f"--- DEBUG UsuarioViewSet.update: perform_update concluído. ---")
            response = Response(serializer.data)
        else:
            print(f"--- DEBUG UsuarioViewSet.update: serializer.is_valid() retornou FALSE. Erros: {serializer.errors}")
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        print(f"--- DEBUG UsuarioViewSet.update: Response status: {response.status_code} ---")
        print(f"Response data (após atualização): {response.data}")
        print("--- FIM DEBUG UsuarioViewSet.update ---\n")
        return response

    def perform_update(self, serializer):
        print("\n--- DEBUG UsuarioViewSet.perform_update: Método perform_update da ViewSet chamado! ---")
        print(f"Serializer instance: {serializer.instance.username} (ID: {serializer.instance.id})")
        print(f"Serializer validated_data: {serializer.validated_data}")
        serializer.save()
        print("--- DEBUG UsuarioViewSet.perform_update: serializer.save() invocado! ---")
        print(f"Serializer instance APÓS SAVE: {serializer.instance.username} (ID: {serializer.instance.id})")
        print(f"Perfil do usuário APÓS SAVE: Estabelecimento ID={serializer.instance.perfil.estabelecimento.id if serializer.instance.perfil.estabelecimento else 'None'}, Papel={serializer.instance.perfil.papel}")
        print("--- FIM DEBUG UsuarioViewSet.perform_update ---\n")

    @action(detail=False, methods=['get'], permission_classes=[permissions.IsAuthenticated])
    def me(self, request):
        """ Retorna os detalhes do usuário autenticado e seu perfil. Endpoint: /api/usuarios/users/me/ """
        if not request.user.is_authenticated:
            return Response({'detail': 'Não autenticado.'}, status=status.HTTP_401_UNAUTHORIZED)
        serializer = self.get_serializer(request.user)
        return Response(serializer.data)

class PerfilViewSet(EstablishmentFilteredViewSet, viewsets.ModelViewSet):
    """ ViewSet para o modelo Perfil. """
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
    """ ViewSet para o modelo Estabelecimento. """
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