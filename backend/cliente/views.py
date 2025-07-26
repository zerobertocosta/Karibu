# backend/cliente/views.py
from rest_framework import viewsets, status
from rest_framework.response import Response
from .models import Cliente
from .serializers import ClienteSerializer
from .permissions import IsOwnerOrManager
from rest_framework.permissions import IsAuthenticated
from django.db import transaction # Import para garantir atomicidade
from django.contrib.auth import get_user_model # Importa o modelo de usuário ativo

User = get_user_model() # Obtém o modelo de usuário customizado ou padrão

class ClienteViewSet(viewsets.ModelViewSet):
    queryset = Cliente.objects.all()
    serializer_class = ClienteSerializer
    permission_classes = [IsAuthenticated, IsOwnerOrManager]
    lookup_field = 'celular' # Define o celular como campo de lookup

    def get_queryset(self):
        # Filtrar clientes com base na permissão IsOwnerOrManager
        user = self.request.user
        if user.is_authenticated:
            # Verifica se o usuário tem um perfil e se é gestor
            if hasattr(user, 'perfil') and user.perfil.is_gestor:
                # Gestor vê clientes do seu estabelecimento
                return Cliente.objects.filter(estabelecimento=user.perfil.estabelecimento)
            else:
                # Cliente normal só vê o próprio perfil
                return Cliente.objects.filter(celular=user.username)
        return Cliente.objects.none() # Não autenticado não vê nada

    # NOVO MÉTODO OU MÉTODO ATUALIZADO PARA LIDAR COM A EXCLUSÃO
    def perform_destroy(self, instance):
        """
        Sobrescreve perform_destroy para deletar o Cliente e o User associado.
        """
        user_celular = instance.celular # Pega o celular do cliente antes de deletá-lo

        with transaction.atomic():
            # 1. Deleta o Cliente
            instance.delete()
            
            # 2. Tenta deletar o User associado (que tem o celular como username)
            try:
                user_to_delete = User.objects.get(username=user_celular)
                user_to_delete.delete()
                # O Perfil será deletado em cascata se o OneToOneField em Perfil tiver on_delete=CASCADE
                # Se não tiver, precisaria deletar Perfil.objects.filter(user=user_to_delete).delete()
            except User.DoesNotExist:
                # Logar um aviso se o User não for encontrado, mas não impedir a deleção do Cliente
                print(f"Aviso: Usuário associado para o celular {user_celular} não encontrado ao deletar Cliente.")
            except Exception as e:
                # Logar qualquer outro erro inesperado
                print(f"Erro ao deletar usuário associado {user_celular}: {e}")