# backend/usuarios/views.py
from rest_framework import viewsets, permissions
from django.contrib.auth import get_user_model
from .models import Perfil
from configuracao.models import Estabelecimento # Para o superuser criar user em estabelecimento específico
from .serializers import UserSerializer, PerfilSerializer, EstabelecimentoSerializer 
# Importe as novas permissões
from .permissions import IsManagerOrSuperuser, IsSelfOrManagerOrSuperuser, IsSuperuserOrCreateUserInOwnEstablishment 
from core.mixins import EstablishmentFilteredViewSet # Importe o mixin

User = get_user_model()

class UsuarioViewSet(EstablishmentFilteredViewSet, viewsets.ModelViewSet):
    """
    ViewSet para o modelo Usuario.
    - Superusuários veem todos os usuários e podem criar/gerenciar qualquer um.
    - Gerentes veem e gerenciam APENAS usuários do seu próprio estabelecimento.
    - Garçons, Cozinheiros, Caixas NÃO podem listar ou gerenciar outros usuários.
    - Qualquer usuário pode ver/editar seu próprio perfil.
    """
    serializer_class = UserSerializer

    def get_permissions(self):
        """
        Instancia e retorna a lista de permissões que esta view requer.
        """
        if self.action in ['list', 'create']:
            # Listar e criar usuários: apenas superusuários e gerentes
            # IsManagerOrSuperuser nega acesso para garçons/cozinheiros/caixas na listagem.
            # IsSuperuserOrCreateUserInOwnEstablishment lida com a lógica de criação e object-level para gerentes.
            self.permission_classes = [IsManagerOrSuperuser, IsSuperuserOrCreateUserInOwnEstablishment]
        elif self.action in ['retrieve', 'update', 'partial_update', 'destroy']:
            # Detalhe, atualização, exclusão: superusuário, gerente, ou o próprio usuário
            self.permission_classes = [IsSelfOrManagerOrSuperuser]
        else:
            # Permissão padrão para outras ações (se houver, ex: custom actions)
            self.permission_classes = [permissions.IsAuthenticated] # Garante que pelo menos autenticado
        return [permission() for permission in self.permission_classes]

    def get_queryset(self):
        # Esta lógica de filtragem é fundamental para o multi-tenancy e para o controle
        # de quem vê o quê.
        
        if self.request.user.is_superuser:
            return User.objects.all()
        
        # Se for gerente, retorna apenas os usuários do seu estabelecimento
        if hasattr(self.request.user, 'perfil') and self.request.user.perfil.is_gestor:
            return User.objects.filter(perfil__estabelecimento=self.request.user.perfil.estabelecimento)
        
        # Para garçons, cozinheiros, caixas, etc., o queryset para 'list' deve ser vazio
        # para evitar que vejam outros usuários. A permissão `IsManagerOrSuperuser` já deveria
        # ter barrado na camada de permissão, mas isso reforça.
        # O 'retrieve' do próprio usuário ainda funcionará pela IsSelfOrManagerOrSuperuser,
        # pois o get_queryset não é chamado para `retrieve` por padrão em ModelViewSets se a instância
        # é recuperada via `get_object()`.
        return User.objects.none()

    def perform_create(self, serializer):
        # A lógica de vinculação ao estabelecimento já está no EstablishmentFilteredViewSet.
        # No caso de superusuários, eles precisariam passar o estabelecimento_id.
        # Para gerentes, o sistema vincula automaticamente ao seu estabelecimento.

        if self.request.user.is_superuser:
            estabelecimento_id = serializer.validated_data.get('perfil', {}).get('estabelecimento')
            if estabelecimento_id:
                try:
                    estabelecimento_instance = Estabelecimento.objects.get(id=estabelecimento_id)
                    user = serializer.save()
                    if hasattr(user, 'perfil'):
                        user.perfil.estabelecimento = estabelecimento_instance
                        if 'perfil' in serializer.validated_data and 'papel' in serializer.validated_data['perfil']:
                             user.perfil.papel = serializer.validated_data['perfil']['papel']
                        user.perfil.save()
                    else: 
                        papel = serializer.validated_data.get('perfil', {}).get('papel', Perfil.GARCOM) 
                        Perfil.objects.create(usuario=user, estabelecimento=estabelecimento_instance, papel=papel)

                except Estabelecimento.DoesNotExist:
                    raise ValueError(f"Estabelecimento com ID '{estabelecimento_id}' não encontrado.")
            else:
                super().perform_create(serializer)
        else:
            super().perform_create(serializer) 
            
            
class PerfilViewSet(EstablishmentFilteredViewSet, viewsets.ModelViewSet):
    """
    ViewSet para o modelo Perfil.
    - Utiliza EstablishmentFilteredViewSet para garantir isolamento por estabelecimento.
    - Permissões: Superusuários e gerentes podem gerenciar perfis de seu estabelecimento.
      Usuários podem ver/editar seu próprio perfil.
    """
    queryset = Perfil.objects.all() # O queryset real será filtrado pelo mixin
    serializer_class = PerfilSerializer
    
    def get_permissions(self):
        """
        Instancia e retorna a lista de permissões que esta view requer.
        """
        if self.action in ['list', 'create']:
            # Listar e criar perfis: apenas superusuários e gerentes
            self.permission_classes = [IsManagerOrSuperuser]
        elif self.action in ['retrieve', 'update', 'partial_update', 'destroy']:
            # Detalhe, atualização, exclusão: superusuário, gerente, ou o próprio usuário
            self.permission_classes = [IsSelfOrManagerOrSuperuser]
        else:
            self.permission_classes = [permissions.IsAuthenticated]
        return [permission() for permission in self.permission_classes]


class EstabelecimentoViewSet(viewsets.ModelViewSet):
    """
    ViewSet para o modelo Estabelecimento.
    Superusuários podem gerenciar todos os estabelecimentos.
    Usuários autenticados (como gerentes) só podem visualizar o(s) seu(s) próprio(s) estabelecimento(s).
    """
    serializer_class = EstabelecimentoSerializer
    queryset = Estabelecimento.objects.all() # Queryset base, será filtrado pelo get_queryset

    def get_permissions(self):
        """
        Define as permissões baseadas na ação.
        """
        if self.action in ['list', 'retrieve']:
            # Para listar e detalhar, permite superusuário ver tudo, e autenticados verem o seu.
            self.permission_classes = [permissions.IsAuthenticated] 
        elif self.action in ['create', 'update', 'partial_update', 'destroy']:
            # Para criar, atualizar e deletar, apenas superusuários.
            self.permission_classes = [permissions.IsAdminUser]
        else:
            # Permissão padrão para outras ações, se houver.
            self.permission_classes = [permissions.IsAuthenticated]
        return [permission() for permission in self.permission_classes]

    def get_queryset(self):
        """
        Filtra o queryset de estabelecimentos baseado no papel do usuário.
        """
        if self.request.user.is_superuser:
            return Estabelecimento.objects.all()
        
        # Se o usuário está autenticado e tem um perfil com estabelecimento
        if self.request.user.is_authenticated and \
           hasattr(self.request.user, 'perfil') and \
           self.request.user.perfil.estabelecimento:
            # Retorna apenas o estabelecimento ao qual o perfil do usuário está vinculado
            return Estabelecimento.objects.filter(id=self.request.user.perfil.estabelecimento.id)
        
        # Para qualquer outro caso (usuário sem perfil/estabelecimento, ou não autenticado)
        return Estabelecimento.objects.none()