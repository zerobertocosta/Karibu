# backend/chamada/views.py

from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from django.shortcuts import get_object_or_404 # Para buscar objetos, se necessário

from .models import ChamadaGarcom
from .serializers import ChamadaGarcomSerializer
from mesa.models import Mesa # Importa o modelo Mesa para validação

class ChamadaGarcomViewSet(viewsets.ModelViewSet):
    # Queryset padrão: todas as chamadas, ordenadas da mais recente para a mais antiga
    queryset = ChamadaGarcom.objects.all().order_by('-data_hora_chamada')
    serializer_class = ChamadaGarcomSerializer

    def get_queryset(self):
        # Permite filtrar as chamadas. Por padrão, exibe apenas as chamadas não atendidas.
        # Se 'all=true' for passado como parâmetro na URL (ex: /api/chamadas-garcom/?all=true),
        # todas as chamadas (atendidas e não atendidas) serão retornadas.
        if self.request.query_params.get('all') == 'true':
            return ChamadaGarcom.objects.all().order_by('-data_hora_chamada')
        # Retorna apenas as chamadas pendentes (não atendidas)
        return ChamadaGarcom.objects.filter(atendida=False).order_by('-data_hora_chamada')

    @action(detail=False, methods=['post'], url_path='criar-chamada')
    def criar_chamada(self, request):
        """
        Endpoint para criar uma nova chamada de garçom.
        Recebe 'mesa_id' no corpo da requisição.
        """
        mesa_id = request.data.get('mesa_id') # O cliente enviará o ID da mesa como 'mesa_id'
        if not mesa_id:
            return Response({'detail': 'ID da mesa é obrigatório.'}, status=status.HTTP_400_BAD_REQUEST)
        
        try:
            mesa = get_object_or_404(Mesa, pk=mesa_id)
        except Mesa.DoesNotExist:
            return Response({'detail': 'Mesa não encontrada.'}, status=status.HTTP_404_NOT_FOUND)

        # Verifica se já existe uma chamada não atendida para esta mesa
        if ChamadaGarcom.objects.filter(mesa=mesa, atendida=False).exists():
            return Response({'detail': f'Já existe uma chamada pendente para a Mesa {mesa.numero}.'}, status=status.HTTP_409_CONFLICT)


        # Cria a instância de ChamadaGarcom.
        # Note que passamos 'mesa=mesa.id' porque o serializer espera o ID da PK da mesa no campo 'mesa'.
        serializer = self.get_serializer(data={'mesa': mesa.id}) 
        serializer.is_valid(raise_exception=True) # Valida os dados da requisição
        self.perform_create(serializer) # Salva a nova chamada no banco de dados
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    @action(detail=True, methods=['patch'], url_path='marcar-atendida')
    def marcar_atendida(self, request, pk=None):
        """
        Endpoint para marcar uma chamada de garçom como atendida.
        """
        chamada = self.get_object() # Obtém o objeto ChamadaGarcom pelo PK (ID) da URL
        if chamada.atendida:
            return Response({'detail': 'Esta chamada já foi marcada como atendida.'}, status=status.HTTP_400_BAD_REQUEST)
        
        chamada.atendida = True # Altera o status para atendida
        chamada.save() # Salva a alteração no banco de dados
        serializer = self.get_serializer(chamada) # Serializa o objeto atualizado
        return Response(serializer.data, status=status.HTTP_200_OK)

