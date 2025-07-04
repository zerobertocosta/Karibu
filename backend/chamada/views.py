# backend/chamada/views.py

from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from django.shortcuts import get_object_or_404 

from .models import ChamadaGarcom
from .serializers import ChamadaGarcomSerializer
from mesa.models import Mesa

class ChamadaGarcomViewSet(viewsets.ModelViewSet):
    # O queryset padrão pode ser simplesmente o que está no Meta.ordering do modelo
    # Se você quiser uma ordenação diferente ou filtros iniciais, pode colocar aqui.
    # Removi o .order_by() daqui para confiar no Meta.ordering do modelo,
    # que já definimos como ['status', '-data_hora_chamada']
    queryset = ChamadaGarcom.objects.all().select_related('mesa') 
    serializer_class = ChamadaGarcomSerializer

    def get_queryset(self):
        # Permite filtrar as chamadas. Por padrão, exibe apenas as chamadas pendentes.
        # ATENÇÃO: Substituído 'atendida' por 'status'
        if self.request.query_params.get('all') == 'true':
            # Se 'all=true', retorna todas as chamadas, ordenadas pelo status e data.
            return ChamadaGarcom.objects.all().order_by('status', '-data_hora_chamada')
        
        # Retorna apenas as chamadas pendentes (status='pendente')
        # ATENÇÃO: Substituído 'atendida=False' por 'status="pendente"'
        return ChamadaGarcom.objects.filter(status='pendente').order_by('-data_hora_chamada')

    @action(detail=False, methods=['post'], url_path='criar-chamada')
    def criar_chamada(self, request):
        mesa_id = request.data.get('mesa_id')
        if not mesa_id:
            return Response({'detail': 'ID da mesa é obrigatório.'}, status=status.HTTP_400_BAD_REQUEST)
        
        try:
            mesa = get_object_or_404(Mesa, pk=mesa_id)
        except Mesa.DoesNotExist:
            return Response({'detail': 'Mesa não encontrada.'}, status=status.HTTP_404_NOT_FOUND)

        # Verifica se já existe uma chamada pendente para esta mesa
        # ATENÇÃO: Substituído 'atendida=False' por 'status="pendente"'
        if ChamadaGarcom.objects.filter(mesa=mesa, status='pendente').exists():
            return Response({'detail': f'Já existe uma chamada pendente para a Mesa {mesa.numero}.'}, status=status.HTTP_409_CONFLICT)

        # O serializer agora precisa que o campo 'status' seja inicializado como 'pendente'
        # ou, como ele já tem um default no modelo, basta passar o ID da mesa.
        # O campo 'mesa' no serializer é 'write_only=True' e espera o ID.
        serializer = self.get_serializer(data={'mesa': mesa.id, 'status': 'pendente'}) # Explicitamente definindo status

        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    # ATENÇÃO: Mudei o nome da action para ser mais condizente com o novo campo 'status'
    # e para seguir a lógica de "resolver" em vez de "marcar atendida"
    @action(detail=True, methods=['patch'], url_path='resolver-chamada')
    def resolver_chamada(self, request, pk=None):
        """
        Endpoint para marcar uma chamada de garçom como resolvida.
        """
        chamada = self.get_object()

        # ATENÇÃO: Substituído 'chamada.atendida' por 'chamada.status'
        if chamada.status == 'resolvida':
            return Response({'detail': 'Esta chamada já foi marcada como resolvida.'}, status=status.HTTP_400_BAD_REQUEST)
        
        # ATENÇÃO: Altera o status para 'resolvida'
        chamada.status = 'resolvida'
        chamada.save()
        serializer = self.get_serializer(chamada)
        return Response(serializer.data, status=status.HTTP_200_OK)