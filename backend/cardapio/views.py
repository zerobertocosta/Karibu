# backend/cardapio/views.py

from rest_framework import viewsets, status
from rest_framework.response import Response
from .models import Categoria, ItemCardapio
from .serializers import CategoriaSerializer, ItemCardapioSerializer
from core.mixins import EstablishmentFilteredViewSet


class CategoriaViewSet(EstablishmentFilteredViewSet, viewsets.ModelViewSet):
    """
    ViewSet para Categoria do Cardápio.
    Hereda de EstablishmentFilteredViewSet para garantir que apenas categorias
    do estabelecimento do usuário logado sejam acessíveis.
    """
    queryset = Categoria.objects.all()
    serializer_class = CategoriaSerializer

    # A lógica de perform_create/update do mixin já cuida do estabelecimento.


class ItemCardapioViewSet(EstablishmentFilteredViewSet, viewsets.ModelViewSet):
    """
    ViewSet para Item de Cardápio.
    Hereda de EstablishmentFilteredViewSet para garantir que apenas itens
    do estabelecimento do usuário logado sejam acessíveis e criados corretamente.
    Inclui validação para garantir que a categoria do item pertença ao mesmo estabelecimento.
    """
    queryset = ItemCardapio.objects.all()
    serializer_class = ItemCardapioSerializer

    def perform_create(self, serializer):
        # A lógica do EstablishmentFilteredViewSet já define o estabelecimento_id
        # Vamos usar essa informação para pré-filtrar as categorias disponíveis
        # e garantir que a categoria escolhida pertença ao mesmo estabelecimento.

        categoria_id = serializer.validated_data.get('categoria', None)
        if categoria_id:
            # Obtém o ID do estabelecimento que o mixin já determinou para o usuário logado
            estabelecimento_id_do_usuario = self.request.user.perfil.estabelecimento.id if hasattr(self.request.user, 'perfil') and self.request.user.perfil.estabelecimento else None

            if not estabelecimento_id_do_usuario and not self.request.user.is_superuser:
                return Response(
                    {"detail": "Usuário não vinculado a um estabelecimento."},
                    status=status.HTTP_400_BAD_REQUEST
                )

            try:
                # Se for superusuário, permite criar para qualquer categoria_id se o estabelecimento for fornecido
                # Caso contrário, filtra pela categoria do estabelecimento do usuário
                if self.request.user.is_superuser:
                    # superusers podem especificar o estabelecimento no payload
                    # se nao especificar ele vai tentar usar o do user logado se tiver
                    # ou falhar se nao tiver
                    estabelecimento_do_payload = serializer.validated_data.get('estabelecimento', None)
                    if estabelecimento_do_payload:
                        categoria_obj = Categoria.objects.get(
                            id=categoria_id.id, # categoria_id aqui é um objeto Categoria, não apenas o ID
                            estabelecimento=estabelecimento_do_payload
                        )
                    else:
                        # Se superuser e nao forneceu estabelecimento, e nao tem perfil,
                        # talvez esteja tentando criar globalmente, o que nao é o caso para ItemCardapio
                        raise ValueError("Superusuário deve especificar o estabelecimento ao criar ItemCardapio se não estiver vinculado a um.")
                else:
                    categoria_obj = Categoria.objects.get(
                        id=categoria_id.id, # categoria_id aqui é um objeto Categoria, não apenas o ID
                        estabelecimento=estabelecimento_id_do_usuario
                    )
            except Categoria.DoesNotExist:
                return Response(
                    {"categoria": "A categoria selecionada não existe ou não pertence ao seu estabelecimento."},
                    status=status.HTTP_400_BAD_REQUEST
                )
            # A validação no método clean() do modelo ItemCardapio também garantirá isso.
            # O save do serializer já passará a categoria_obj corretamente
            serializer.save(estabelecimento=categoria_obj.estabelecimento) # Garante que o estabelecimento do item é o da categoria
        else:
            # Caso a categoria não tenha sido fornecida (deveria ser obrigatória, mas fallback)
            super().perform_create(serializer) # Chama o perform_create do mixin


    def perform_update(self, serializer):
        # Similar ao create, mas para update.
        # Garante que a categoria (se alterada) pertença ao mesmo estabelecimento do item.
        categoria_id = serializer.validated_data.get('categoria', None)
        if categoria_id:
            instance = self.get_object() # Obtém a instância existente
            estabelecimento_id_do_usuario = self.request.user.perfil.estabelecimento.id if hasattr(self.request.user, 'perfil') and self.request.user.perfil.estabelecimento else None

            if not estabelecimento_id_do_usuario and not self.request.user.is_superuser:
                return Response(
                    {"detail": "Usuário não vinculado a um estabelecimento."},
                    status=status.HTTP_400_BAD_REQUEST
                )

            try:
                if self.request.user.is_superuser:
                    # Superusers podem mudar o estabelecimento do item e/ou categoria
                    # Se mudou categoria, verifica se nova categoria pertence ao novo/atual estabelecimento
                    nova_categoria_obj = Categoria.objects.get(id=categoria_id.id)
                    estabelecimento_target = serializer.validated_data.get('estabelecimento', instance.estabelecimento)
                    if nova_categoria_obj.estabelecimento != estabelecimento_target:
                        raise ValueError("A categoria deve pertencer ao estabelecimento alvo.")
                else:
                    # Para usuários normais, a categoria deve pertencer ao seu estabelecimento e
                    # o item deve permanecer no seu estabelecimento.
                    nova_categoria_obj = Categoria.objects.get(
                        id=categoria_id.id,
                        estabelecimento=estabelecimento_id_do_usuario
                    )
                    # Verifica se o estabelecimento do item não está sendo alterado para outro
                    if 'estabelecimento' in serializer.validated_data and \
                       serializer.validated_data['estabelecimento'].id != estabelecimento_id_do_usuario:
                        raise permissions.PermissionDenied("Você não pode alterar o estabelecimento de um item.")

            except (Categoria.DoesNotExist, ValueError) as e:
                return Response(
                    {"categoria": str(e) or "A categoria selecionada não existe ou não pertence ao seu estabelecimento."},
                    status=status.HTTP_400_BAD_REQUEST
                )
            # O save do serializer já passará a categoria_obj corretamente
            serializer.save(estabelecimento=nova_categoria_obj.estabelecimento) # Garante consistência
        else:
            super().perform_update(serializer) # Chama o perform_update do mixin