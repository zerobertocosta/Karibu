# backend/mesas/views.py (CÓDIGO COMPLETO - ATUALIZADO)

from rest_framework import viewsets
from rest_framework.exceptions import PermissionDenied, ValidationError
from .models import Mesa
from .serializers import MesaSerializer
from .mixins import MesaEstablishmentMixin # Importa o mixin de filtragem
from .permissions import IsGestorForMesaOperations # Importa a NOVA permissão específica

class MesaViewSet(MesaEstablishmentMixin, viewsets.ModelViewSet):
    """
    ViewSet para a gestão de Mesas.
    Hereda de MesaEstablishmentMixin para filtrar as mesas por estabelecimento (GET).
    Usa IsGestorForMesaOperations para controlar as permissões de acesso (visualização e escrita).
    """
    queryset = Mesa.objects.all()
    serializer_class = MesaSerializer
    permission_classes = [IsGestorForMesaOperations] # <-- Use a nova permissão aqui!

    # Sobrescreve perform_create para garantir que o estabelecimento seja definido corretamente.
    # A verificação de permissão (se o usuário é Gestor) já foi feita por IsGestorForMesaOperations.
    def perform_create(self, serializer):
        if not self.request.user.is_authenticated:
            raise PermissionDenied("Usuário não autenticado para criar.")
        
        # A permissão IsGestorForMesaOperations já garantiu que o perfil e estabelecimento existem.
        # Caso por algum motivo interno ainda falhe, esta validação extra ajuda.
        if not hasattr(self.request.user, 'perfil') or not self.request.user.perfil.estabelecimento:
            raise ValidationError({"detail": "Seu perfil de usuário não está vinculado a um estabelecimento."})
        
        # O modelo Mesa tem o campo 'estabelecimento' diretamente.
        serializer.save(estabelecimento=self.request.user.perfil.estabelecimento)

    # Não é necessário sobrescrever perform_update e perform_destroy a menos que haja
    # lógica adicional complexa. A permissão IsGestorForMesaOperations e o get_queryset
    # já lidam com a autorização e o filtro de objeto.