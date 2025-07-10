from rest_framework import serializers
from django.contrib.auth import get_user_model
from .models import Perfil, Estabelecimento

User = get_user_model()

class EstabelecimentoSerializer(serializers.ModelSerializer):
    class Meta:
        model = Estabelecimento
        fields = '__all__'

class PerfilSerializer(serializers.ModelSerializer):
    estabelecimento = serializers.PrimaryKeyRelatedField(
        queryset=Estabelecimento.objects.all(),
        pk_field=serializers.UUIDField(format='hex_verbose'), # CORREÇÃO AQUI: Removido 'binary=False'
        required=False,
        allow_null=True
    )

    class Meta:
        model = Perfil
        fields = ['id', 'estabelecimento', 'estabelecimento_nome', 'papel']
        read_only_fields = ['estabelecimento_nome']

    def get_estabelecimento_nome(self, obj):
        return obj.estabelecimento.nome if obj.estabelecimento else None

    estabelecimento_nome = serializers.SerializerMethodField('get_estabelecimento_nome')


class UserSerializer(serializers.ModelSerializer):
    perfil = PerfilSerializer()

    class Meta:
        model = User
        fields = ['id', 'username', 'email', 'password', 'is_superuser', 'perfil']
        extra_kwargs = {
            'password': {'write_only': True, 'required': False},
            'is_superuser': {'read_only': True}
        }

    def create(self, validated_data):
        perfil_data = validated_data.pop('perfil')
        password = validated_data.pop('password', None)

        user = User.objects.create(**validated_data)
        if password:
            user.set_password(password)
            user.save()

        Perfil.objects.create(user=user, **perfil_data)
        return user

    def update(self, instance, validated_data):
        perfil_data = validated_data.pop('perfil', {})
        password = validated_data.pop('password', None)

        instance.username = validated_data.get('username', instance.username)
        instance.email = validated_data.get('email', instance.email)
        if password:
            instance.set_password(password)
        instance.save()

        perfil_instance = instance.perfil
        perfil_instance.estabelecimento = perfil_data.get('estabelecimento', perfil_instance.estabelecimento)
        perfil_instance.papel = perfil_data.get('papel', perfil_instance.papel)
        perfil_instance.save()

        return instance