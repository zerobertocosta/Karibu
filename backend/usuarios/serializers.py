# backend/karibu/usuarios/serializers.py

from rest_framework import serializers
from django.contrib.auth import get_user_model
from .models import Perfil, Estabelecimento # Certifique-se de que Estabelecimento está correto, ou ajuste se estiver em outro app

User = get_user_model()

# Serializer para o modelo de Usuário (User)
class UsuarioSerializer(serializers.ModelSerializer):
    # Campo 'perfil' aninhado para incluir dados do perfil diretamente no usuário
    perfil = serializers.SerializerMethodField()

    class Meta:
        model = User
        # Inclua todos os campos que você deseja retornar/aceitar
        fields = ['id', 'username', 'email', 'first_name', 'last_name', 'is_active', 'is_staff', 'perfil']
        # Adicione 'password' apenas para criação/atualização se necessário, com write_only=True
        extra_kwargs = {'password': {'write_only': True, 'required': False}} # Password é opcional para update

    def get_perfil(self, obj):
        # Retorna o PerfilSerializer se o usuário tiver um perfil
        # Isso evita um erro se um usuário não tiver um perfil associado
        if hasattr(obj, 'perfil'):
            # self.context precisa ser passado para que PerfilSerializer possa acessar requests, etc.
            return PerfilSerializer(obj.perfil, context=self.context).data
        return None

    def create(self, validated_data):
        # Lida com a criação do usuário e seu perfil associado
        perfil_data = validated_data.pop('perfil', None)
        password = validated_data.pop('password', None)
        
        user = User.objects.create(**validated_data)
        if password:
            user.set_password(password)
            user.save()

        if perfil_data:
            # Garanta que o estabelecimento seja uma instância de Estabelecimento
            estabelecimento_id = perfil_data.get('estabelecimento')
            if isinstance(estabelecimento_id, Estabelecimento): # Já é uma instância
                estabelecimento_instance = estabelecimento_id
            else: # É um ID, busca a instância
                try:
                    estabelecimento_instance = Estabelecimento.objects.get(id=estabelecimento_id)
                except Estabelecimento.DoesNotExist:
                    raise serializers.ValidationError({"estabelecimento": "Estabelecimento não encontrado."})

            Perfil.objects.create(user=user, estabelecimento=estabelecimento_instance, papel=perfil_data.get('papel'))
        return user

    def update(self, instance, validated_data):
        # Lida com a atualização do usuário e seu perfil
        perfil_data = validated_data.pop('perfil', None)
        password = validated_data.pop('password', None)

        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        
        if password:
            instance.set_password(password)
        instance.save()

        if perfil_data:
            perfil_instance = getattr(instance, 'perfil', None)
            if perfil_instance:
                estabelecimento_id = perfil_data.get('estabelecimento')
                if isinstance(estabelecimento_id, Estabelecimento):
                    perfil_instance.estabelecimento = estabelecimento_id
                elif estabelecimento_id:
                    try:
                        perfil_instance.estabelecimento = Estabelecimento.objects.get(id=estabelecimento_id)
                    except Estabelecimento.DoesNotExist:
                        raise serializers.ValidationError({"estabelecimento": "Estabelecimento não encontrado."})
                
                perfil_instance.papel = perfil_data.get('papel', perfil_instance.papel)
                perfil_instance.save()
            else:
                # Cria um novo perfil se não existir e os dados forem fornecidos
                if perfil_data.get('estabelecimento') and perfil_data.get('papel'):
                    estabelecimento_id = perfil_data.get('estabelecimento')
                    if isinstance(estabelecimento_id, Estabelecimento):
                        estabelecimento_instance = estabelecimento_id
                    else:
                        try:
                            estabelecimento_instance = Estabelecimento.objects.get(id=estabelecimento_id)
                        except Estabelecimento.DoesNotExist:
                            raise serializers.ValidationError({"estabelecimento": "Estabelecimento não encontrado."})
                    Perfil.objects.create(user=instance, estabelecimento=estabelecimento_instance, papel=perfil_data.get('papel'))
        return instance

# Serializer para o modelo de Perfil
class PerfilSerializer(serializers.ModelSerializer):
    # Para mostrar o nome do estabelecimento em vez do ID
    estabelecimento_nome = serializers.CharField(source='estabelecimento.nome', read_only=True)
    # Para poder passar o ID do estabelecimento ao criar/atualizar
    estabelecimento = serializers.PrimaryKeyRelatedField(queryset=Estabelecimento.objects.all(), write_only=True)

    class Meta:
        model = Perfil
        fields = ['id', 'estabelecimento', 'estabelecimento_nome', 'papel', 'data_criacao', 'data_atualizacao']
        read_only_fields = ['id', 'data_criacao', 'data_atualizacao']

# Serializer para o modelo de Estabelecimento
class EstabelecimentoSerializer(serializers.ModelSerializer):
    class Meta:
        model = Estabelecimento
        fields = '__all__' # Inclua todos os campos do modelo Estabelecimento