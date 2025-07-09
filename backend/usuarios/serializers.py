# backend/usuarios/serializers.py

from rest_framework import serializers
from django.contrib.auth.models import User
from .models import Perfil
from configuracao.serializers import EstabelecimentoSerializer # Importar para nested serializer

# Serializer para o modelo Perfil
class PerfilSerializer(serializers.ModelSerializer):
    # Para exibição, queremos os detalhes do estabelecimento.
    # Para criação/atualização por usuários de estabelecimento, o mixin irá definir.
    estabelecimento = EstabelecimentoSerializer(read_only=True)
    papel_display = serializers.CharField(source='get_papel_display', read_only=True)

    class Meta:
        model = Perfil
        fields = [
            'id', 'estabelecimento', 'papel', 'papel_display',
            'data_criacao', 'data_atualizacao'
        ]
        read_only_fields = ['data_criacao', 'data_atualizacao']


# Serializer para o modelo User (do Django), com o Perfil aninhado
class UserSerializer(serializers.ModelSerializer):
    # Aninha o Perfil para que ele seja incluído nas operações do User
    perfil = PerfilSerializer(read_only=True) # Apenas leitura no UserSerializer principal

    class Meta:
        model = User
        fields = [
            'id', 'username', 'email', 'first_name', 'last_name',
            'is_staff', 'is_active', 'is_superuser', 'last_login',
            'date_joined', 'perfil' # Incluir o perfil aninhado
        ]
        read_only_fields = [
            'is_staff', 'is_active', 'is_superuser', 'last_login',
            'date_joined', 'perfil' # Estes campos são geralmente gerenciados pelo admin ou sistema
        ]
        extra_kwargs = {
            'password': {'write_only': True, 'required': False} # Permite mudar senha, mas não lê
        }

    # Sobrescrever create e update para lidar com a senha de forma segura
    def create(self, validated_data):
        password = validated_data.pop('password', None)
        user = User.objects.create(**validated_data)
        if password:
            user.set_password(password)
            user.save()
        return user

    def update(self, instance, validated_data):
        password = validated_data.pop('password', None)
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        if password:
            instance.set_password(password)
        instance.save()
        return instance

# Este serializer pode ser usado para operações de escrita de Perfil,
# especialmente quando você precisa definir 'estabelecimento' manualmente
# (e.g., por um superusuário via API ou em um fluxo específico).
class PerfilWriteSerializer(serializers.ModelSerializer):
    class Meta:
        model = Perfil
        fields = [
            'id', 'user', 'estabelecimento', 'papel',
            'data_criacao', 'data_atualizacao'
        ]
        read_only_fields = ['data_criacao', 'data_atualizacao']
        # 'user' deve ser definido ao criar, 'estabelecimento' também.