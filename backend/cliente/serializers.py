from rest_framework import serializers
from .models import Cliente

class ClienteSerializer(serializers.ModelSerializer):
    class Meta:
        model = Cliente
        fields = '__all__' # Inclui todos os campos do modelo
        # Ou especifique os campos que deseja: fields = ['id', 'nome', 'sobrenome', 'email', 'telefone', 'cpf', 'ativo']