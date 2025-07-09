# backend/configuracao/serializers.py

from rest_framework import serializers
from .models import Estabelecimento

class EstabelecimentoSerializer(serializers.ModelSerializer):
    class Meta:
        model = Estabelecimento
        fields = '__all__' # Incluir todos os campos do modelo Estabelecimento
        read_only_fields = ['data_criacao', 'data_atualizacao'] # Campos que não podem ser alterados diretamente