from rest_framework import serializers
from .models import Estabelecimento

class EstabelecimentoSerializer(serializers.ModelSerializer):
    class Meta:
        model = Estabelecimento
        fields = '__all__' # Inclui todos os campos do modelo
        # Ou especifique os campos que deseja: fields = ['id', 'nome', 'endereco', 'email', 'telefone', 'cnpj', 'ativo']