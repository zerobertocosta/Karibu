# backend/cliente/serializers.py

from rest_framework import serializers
from .models import Cliente
from configuracao.serializers import EstabelecimentoSerializer # Importa o Serializer de Estabelecimento

class ClienteSerializer(serializers.ModelSerializer):
    # O campo 'estabelecimento' será read-only, pois será definido/filtrado automaticamente pelo mixin.
    estabelecimento = EstabelecimentoSerializer(read_only=True)

    class Meta:
        model = Cliente
        fields = [
            'id', 'estabelecimento', 'nome_completo', 'email',
            'telefone', 'cpf', 'data_cadastro', 'data_atualizacao'
        ]
        read_only_fields = ['data_cadastro', 'data_atualizacao']
        # Adicionar validação de unicidade de CPF/Estabelecimento ou Nome/Estabelecimento
        # Já fizemos a validação no método clean() do modelo, que será chamado pelo serializer.