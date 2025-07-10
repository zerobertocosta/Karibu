from rest_framework import viewsets, permissions
from django.contrib.auth import get_user_model
from .models import Perfil, Estabelecimento
from .serializers import UserSerializer, PerfilSerializer, EstabelecimentoSerializer
# IMPORTAR A PERMISSÃO PERSONALIZADA AQUI:
from .permissions import IsSuperuserOrCreateUserInOwnEstablishment # <--- ADICIONADA/ATUALIZADA ESTA LINHA

User = get_user_model()

class UsuarioViewSet(viewsets.ModelViewSet):
    # REMOVIDO: queryset = User.objects.all()
    serializer_class = UserSerializer
    # ATUALIZADO: Usar a permissão personalizada
    permission_classes = [IsSuperuserOrCreateUserInOwnEstablishment]

    # NOVO: Implementar get_queryset para filtrar a lista de usuários
    def get_queryset(self):
        # Superusuários veem todos os usuários
        if self.request.user.is_superuser:
            return User.objects.all()
        
        # Gestores (autenticados, não superusuários) veem apenas usuários do seu estabelecimento
        elif hasattr(self.request.user, 'perfil') and self.request.user.perfil.estabelecimento:
            gestor_estabelecimento = self.request.user.perfil.estabelecimento
            # Filtra usuários cujo perfil está associado ao mesmo estabelecimento do gestor
            return User.objects.filter(perfil__estabelecimento=gestor_estabelecimento)
        
        # Para outros usuários (garçons, caixas, etc.) ou usuários sem perfil/estabelecimento, não mostre nada
        return User.objects.none()

class PerfilViewSet(viewsets.ModelViewSet):
    queryset = Perfil.objects.all()
    serializer_class = PerfilSerializer
    # Adapte as permissões para o PerfilViewSet. Gestores só devem poder ver/editar perfis do seu est.
    permission_classes = [IsSuperuserOrCreateUserInOwnEstablishment]

class EstabelecimentoViewSet(viewsets.ModelViewSet):
    queryset = Estabelecimento.objects.all()
    serializer_class = EstabelecimentoSerializer
    # Lista de estabelecimentos pode ser vista por qualquer usuário autenticado para seleção
    permission_classes = [permissions.IsAuthenticated]
    # Se quiser que NÃO LOGADOS possam ver, mude para: permissions.AllowAny