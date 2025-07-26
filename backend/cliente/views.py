# backend/cliente/views.py
from rest_framework import viewsets, status
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from .models import Cliente
from .serializers import ClienteSerializer
from .permissions import IsOwnerOrManager # Importa a permissão customizada

class ClienteViewSet(viewsets.ModelViewSet):
    """
    ViewSet para gerenciar clientes.
    Permite operações CRUD (Criar, Ler, Atualizar, Deletar) para o modelo Cliente.
    """
    queryset = Cliente.objects.all()
    serializer_class = ClienteSerializer
    permission_classes = [IsAuthenticated, IsOwnerOrManager] # Aplica autenticação e permissão customizada

    def get_queryset(self):
        """
        Garante que usuários não superusuários ou gestores vejam apenas
        os clientes de seu próprio estabelecimento, ou seu próprio perfil.
        Superusuários e gestores veem todos ou os do seu estabelecimento.
        """
        user = self.request.user
        
        # Superusuários veem todos os clientes
        if user.is_superuser:
            return Cliente.objects.all()
        
        # Gestores veem os clientes do seu estabelecimento
        if hasattr(user, 'perfil') and user.perfil.is_gestor:
            if user.perfil.estabelecimento:
                return Cliente.objects.filter(estabelecimento=user.perfil.estabelecimento)
            return Cliente.objects.none() # Se for gestor mas não tiver estabelecimento, não vê nada
        
        # Clientes normais só podem ver seu próprio perfil
        # A permissão 'IsOwnerOrManager' já lida com a visibilidade de objeto.
        # Aqui, estamos filtrando a lista inicial.
        # Assumindo que o 'username' do cliente é o 'celular'
        return Cliente.objects.filter(celular=user.username)


    def perform_create(self, serializer):
        """
        Define o estabelecimento para o cliente na criação, se o usuário não for superusuário
        e tiver um estabelecimento associado.
        """
        user = self.request.user
        if not user.is_superuser and hasattr(user, 'perfil') and user.perfil.estabelecimento:
            # Garante que o cliente seja associado ao estabelecimento do usuário logado
            serializer.save(estabelecimento=user.perfil.estabelecimento)
        else:
            # Para superusuários, ou se o estabelecimento for passado explicitamente (e permitido por validação)
            serializer.save()

    def get_object(self):
        """
        Garante que um cliente normal só possa acessar seu próprio perfil pelo celular (PK).
        Gestores/Superusuários acessam normalmente.
        """
        obj = super().get_object()
        # Se o usuário não for superusuário nem gestor, e o celular do objeto não for o do usuário,
        # levantar um erro de permissão.
        # A permissão IsOwnerOrManager já faz grande parte disso, mas é bom ter uma redundância aqui
        # para a obtenção do objeto.
        user = self.request.user
        if not user.is_superuser and not (hasattr(user, 'perfil') and user.perfil.is_gestor):
            if str(obj.celular) != str(user.username): # Converte para string para comparação segura
                self.permission_denied(
                    self.request,
                    message="Você não tem permissão para acessar o perfil de outros clientes."
                )
        return obj