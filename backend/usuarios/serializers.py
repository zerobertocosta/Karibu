# backend/usuarios/serializers.py
from rest_framework import serializers
from django.contrib.auth import get_user_model
from .models import Perfil, Estabelecimento

User = get_user_model()

class EstabelecimentoSerializer(serializers.ModelSerializer):
    class Meta:
        model = Estabelecimento
        fields = '__all__'

class PerfilSerializer(serializers.ModelSerializer):
    # Campo 'estabelecimento' para escrita (receber UUID).
    # O PrimaryKeyRelatedField já lida com a conversão do UUID para o objeto Estabelecimento
    # durante a validação para operações de escrita (create/update).
    # Para leitura, ele retorna o UUID por padrão.
    estabelecimento = serializers.PrimaryKeyRelatedField(
        queryset=Estabelecimento.objects.all(),
        pk_field=serializers.UUIDField(format='hex_verbose'),
        required=False,
        allow_null=True
    )
    # Campo 'estabelecimento_obj' para leitura (retornar o objeto completo do estabelecimento)
    # Isso garante que na resposta da API, o frontend receba os detalhes do estabelecimento.
    estabelecimento_obj = EstabelecimentoSerializer(source='estabelecimento', read_only=True)

    class Meta:
        model = Perfil
        fields = ['id', 'estabelecimento', 'estabelecimento_obj', 'estabelecimento_nome', 'papel']
        read_only_fields = ['estabelecimento_nome'] # 'estabelecimento_obj' já é read_only

    def get_estabelecimento_nome(self, obj):
        return obj.estabelecimento.nome if obj.estabelecimento else None

    # O SerializerMethodField é usado para campos calculados ou que precisam de lógica customizada.
    # Ele chama o método 'get_estabelecimento_nome' automaticamente.
    estabelecimento_nome = serializers.SerializerMethodField('get_estabelecimento_nome')

class UserSerializer(serializers.ModelSerializer):
    # O PerfilSerializer aninhado cuidará da validação e serialização do perfil
    perfil = PerfilSerializer()

    class Meta:
        model = User
        fields = ['id', 'username', 'email', 'password', 'is_superuser', 'perfil']
        extra_kwargs = {
            'password': {'write_only': True, 'required': False}, # Senha é apenas para escrita e não obrigatória em updates
            'is_superuser': {'read_only': True} # Superusuário é apenas para leitura (não pode ser alterado via API por padrão)
        }

    def create(self, validated_data):
        # Popa os dados do perfil e da senha antes de criar o usuário
        perfil_data = validated_data.pop('perfil')
        password = validated_data.pop('password', None)
        user = User.objects.create(**validated_data) # Cria o objeto User
        if password:
            user.set_password(password) # Define a senha com hash
        user.save() # Salva o User no banco de dados
        Perfil.objects.create(user=user, **perfil_data) # Cria o perfil associado ao usuário
        return user

    def update(self, instance, validated_data):
        # --- INÍCIO DEBUG ---
        print("\n--- DEBUG UserSerializer.update ---")
        print(f"Instance ID: {instance.id}, Username (antes): {instance.username}, Email (antes): {instance.email}")
        print(f"Validated Data (dados recebidos para validação): {validated_data}")
        # --- FIM DEBUG ---

        # Popa os dados do perfil e da senha. O .pop garante que eles não fiquem em validated_data para o User
        perfil_data = validated_data.pop('perfil', {})
        password = validated_data.pop('password', None)

        # --- INÍCIO DEBUG ---
        print(f"Perfil Data (depois do pop): {perfil_data}")
        print(f"Password (depois do pop): {'<present>' if password else '<not present>'}")
        print(f"Validated Data (após pops de perfil/password): {validated_data}")
        # --- FIM DEBUG ---

        # Atualiza campos do modelo User (username e email)
        instance.username = validated_data.get('username', instance.username)
        instance.email = validated_data.get('email', instance.email)

        # --- INÍCIO DEBUG ---
        print(f"User fields (para salvar): username={instance.username}, email={instance.email}")
        # --- FIM DEBUG ---

        if password:
            instance.set_password(password) # Define a nova senha
            # --- INÍCIO DEBUG ---
            print("Senha foi atualizada.")
            # --- FIM DEBUG ---
        instance.save() # Salva as alterações no modelo User
        # --- INÍCIO DEBUG ---
        print("Instância do User salva.")
        # --- FIM DEBUG ---

        # Atualiza campos do modelo Perfil associado ao usuário
        perfil_instance = instance.perfil
        # --- INÍCIO DEBUG ---
        print(f"Perfil atual (antes da atualização): Estabelecimento ID={perfil_instance.estabelecimento.id if perfil_instance.estabelecimento else 'None'}, Papel={perfil_instance.papel}")
        # --- FIM DEBUG ---

        # Pega os novos valores para estabelecimento e papel do perfil_data.
        # O PrimaryKeyRelatedField já converteu o UUID em um objeto Estabelecimento aqui.
        new_estabelecimento = perfil_data.get('estabelecimento', perfil_instance.estabelecimento)
        new_papel = perfil_data.get('papel', perfil_instance.papel)

        # --- INÍCIO DEBUG ---
        if new_estabelecimento:
            print(f"Novo Estabelecimento (ID): {new_estabelecimento.id if hasattr(new_estabelecimento, 'id') else new_estabelecimento}")
        else:
            print("Novo Estabelecimento: None")
        print(f"Novo Papel: {new_papel}")
        # --- FIM DEBUG ---

        perfil_instance.estabelecimento = new_estabelecimento
        perfil_instance.papel = new_papel
        perfil_instance.save() # Salva as alterações no modelo Perfil
        # --- INÍCIO DEBUG ---
        print("Instância do Perfil salva.")
        print("--- FIM DEBUG UserSerializer.update ---\n")
        # --- FIM DEBUG ---

        return instance # Retorna a instância User atualizada