# backend/cliente/serializers.py

from rest_framework import serializers
from django.contrib.auth import get_user_model
from django.db import transaction
from django.utils.translation import gettext_lazy as _

# Importações ABSOLUTAS corrigidas:
from usuarios.models import Perfil
from configuracao.models import Estabelecimento # Certifique-se de que este caminho está correto para seu modelo Estabelecimento
from .models import Cliente

User = get_user_model()

class ClienteSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True)
    # Garante que o UUID recebido é convertido para um objeto Estabelecimento
    estabelecimento = serializers.PrimaryKeyRelatedField(queryset=Estabelecimento.objects.all())

    class Meta:
        model = Cliente
        fields = [
            'celular', 'password', 'nome_completo', 'data_nascimento',
            'logradouro', 'numero', 'bairro', 'cidade', 'estado', 'cep',
            'foto_cliente', 'estabelecimento'
        ]
        # Adicione campos somente leitura ou outros extras se necessário
        extra_kwargs = {
            'celular': {'validators': []} # Remove o validador padrão de unicidade aqui se for controlado em clean()
        }

    def create(self, validated_data):
        password = validated_data.pop('password')
        # Extrair o objeto Estabelecimento validado ANTES de criar o Cliente/Perfil
        estabelecimento_obj = validated_data.pop('estabelecimento')

        with transaction.atomic():
            # 1. Criação do Django User
            user = User.objects.create_user(
                username=validated_data['celular'], # O celular será o username
                password=password,
                is_active=True # Cliente deve ser ativo por padrão
            )

            # 2. Criação do Perfil associado ao User e Estabelecimento
            # REMOVEMOS is_gestor=False e is_garcom=False daqui, pois são propriedades
            # ou seus valores são definidos por lógica interna do modelo Perfil,
            # ou por outros campos que você pode ter no Perfil.
            Perfil.objects.create(
                user=user,
                estabelecimento=estabelecimento_obj # PASSA O OBJETO ESTABELECIMENTO AQUI
            )

            # 3. Criação do Cliente
            # O campo 'estabelecimento' é uma ForeignKey no modelo Cliente.
            # Ele precisa do objeto Estabelecimento, não do ID.
            # Os demais dados de validated_data são passados diretamente.
            cliente = Cliente.objects.create(
                estabelecimento=estabelecimento_obj, # PASSA O OBJETO ESTABELECIMENTO AQUI
                **validated_data # Passa os campos restantes (celular, nome_completo, etc.)
            )

            return cliente

    def update(self, instance, validated_data):
        # Se a senha for enviada, atualiza a senha do User associado
        password = validated_data.pop('password', None)
        if password:
            # Assumimos que o Cliente tem uma relação reversa para o User (cliente.user)
            # ou que você pode acessar o user através do perfil (cliente.perfil.user)
            # A forma mais robusta é buscar o User pelo username (celular do cliente)
            try:
                user_to_update = User.objects.get(username=instance.celular)
                user_to_update.set_password(password)
                user_to_update.save()
            except User.DoesNotExist:
                # Se o User não for encontrado, podemos logar um erro ou levantar uma exceção
                raise serializers.ValidationError({"detail": "Usuário associado não encontrado."})


        # Lida com a atualização do campo 'estabelecimento' se for permitido.
        # Para clientes, geralmente o estabelecimento não é alterado via PATCH.
        if 'estabelecimento' in validated_data:
            instance.estabelecimento = validated_data.pop('estabelecimento')

        # Atualiza os campos restantes do cliente
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save() # Salva a instância do Cliente
        
        return instance