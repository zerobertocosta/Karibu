# backend/chamada/serializers.py

from rest_framework import serializers
from .models import ChamadaGarcom
from mesa.models import Mesa # Importa o modelo Mesa para o queryset do campo ForeignKey

class ChamadaGarcomSerializer(serializers.ModelSerializer):
    # Campo para exibir o número da mesa, apenas para leitura
    mesa_numero = serializers.IntegerField(source='mesa.numero', read_only=True)
    
    # Campo para exibir o status amigável (ex: "Pendente", "Resolvida")
    status_display = serializers.CharField(source='get_status_display', read_only=True)

    # Campo para receber o ID da mesa na criação/atualização.
    # 'queryset=Mesa.objects.all()' garante que o ID fornecido seja de uma Mesa existente.
    # 'write_only=True' significa que este campo é usado apenas para entrada de dados.
    mesa = serializers.PrimaryKeyRelatedField(queryset=Mesa.objects.all(), write_only=True)

    class Meta:
        model = ChamadaGarcom
        # Campos que serão incluídos na representação JSON
        # ATENÇÃO: 'atendida' FOI REMOVIDO E 'status' E 'status_display' FORAM ADICIONADOS AQUI
        fields = ['id', 'mesa', 'mesa_numero', 'data_hora_chamada', 'status', 'status_display']
        
        # Campos que são apenas para leitura (não podem ser alterados via API na criação/update)
        # ATENÇÃO: 'atendida' FOI REMOVIDO E 'status' NÃO É MAIS read_only AQUI
        read_only_fields = ['data_hora_chamada', 'mesa_numero', 'status_display']