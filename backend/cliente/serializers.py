# backend/cliente/serializers.py
from rest_framework import serializers
from .models import Cliente
# Importa o Serializer de Estabelecimento
from configuracao.serializers import EstabelecimentoSerializer

class ClienteSerializer(serializers.ModelSerializer):
    # O campo 'estabelecimento' será read-only, pois será definido/filtrado automaticamente pelo mixin.
    # No entanto, para criar um novo cliente via API, talvez você queira que 'estabelecimento'
    # seja writable para superusuários ou para um fluxo de criação específico.
    # Por ora, mantemos como read_only, mas pense nesse detalhe para o fluxo de criação.
    estabelecimento = EstabelecimentoSerializer(read_only=True)

    # Adicione um campo de escrita para a senha, mas que não retorne a senha hasheada
    password = serializers.CharField(write_only=True, required=True, min_length=6)

    class Meta:
        model = Cliente
        fields = [
            'celular',           # O novo PK
            'password',          # Campo para a senha
            'estabelecimento',
            'nome_completo',
            'foto_cliente',      # Novo campo
            'data_nascimento',   # Novo campo
            # Campos de endereço
            'logradouro',
            'numero',
            'complemento',
            'bairro',
            'cidade',
            'estado',
            'cep',
            'data_cadastro',
            'data_atualizacao'
        ]
        # 'celular' agora é a PK, então não precisa de 'id'.
        # 'password' é write_only, então não aparece na leitura.
        read_only_fields = [
            'data_cadastro',
            'data_atualizacao',
            # 'estabelecimento' está como read_only acima, se quiser.
            # Se você quer permitir que o estabelecimento seja definido na criação,
            # remova 'read_only=True' do campo 'estabelecimento' acima e adicione:
            # extra_kwargs = {
            #     'estabelecimento': {'write_only': True} # Para ser writable na criação, mas não retornado na leitura
            # }
        ]

    # Sobrescreve o método create para usar a função save do modelo que já hasheia a senha
    def create(self, validated_data):
        password = validated_data.pop('password')
        cliente = Cliente.objects.create(**validated_data)
        cliente.set_password(password) # Usar set_password ou definir diretamente para aproveitar make_password
        cliente.save() # O save() já chama make_password() se não estiver hasheada
        return cliente

    # Sobrescreve o método update para permitir atualização da senha
    def update(self, instance, validated_data):
        # A senha é um campo 'write_only', então ela só virá em 'validated_data' se for atualizada.
        if 'password' in validated_data:
            password = validated_data.pop('password')
            # Você pode usar instance.set_password(password) aqui ou
            # deixar que o método save do modelo cuide do hash se a password for diretamente atribuída.
            instance.password = password # O save() do modelo fará o hash
        
        # Atualiza os outros campos
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        
        instance.save()
        return instance