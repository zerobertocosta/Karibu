# backend/pedido/views.py

from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from django.shortcuts import get_object_or_404
from django.db import transaction

from .models.pedido import Pedido, ItemPedido
from .models.envio_cozinha import EnvioCozinha
from .serializers import PedidoSerializer, ItemPedidoSerializer, EnvioCozinhaSerializer

# Importa o modelo Mesa e ItemCardapio, se necessário para outras views
from mesa.models import Mesa
from cardapio.models import ItemCardapio


class PedidoViewSet(viewsets.ModelViewSet):
    queryset = Pedido.objects.all().order_by('-data_hora_pedido')
    serializer_class = PedidoSerializer

    @action(detail=False, methods=['get'], url_path='aberto/mesa/(?P<mesa_id>\d+)')
    def get_or_create_open_order_for_table(self, request, mesa_id=None):
        try:
            mesa = get_object_or_404(Mesa, pk=mesa_id)
            # Tenta encontrar um pedido aberto para a mesa
            pedido = Pedido.objects.get(mesa=mesa, status='aberto')
            
            # Atualiza o valor total do pedido antes de serializar, caso haja alguma inconsistência.
            pedido.update_valor_total() 
            
            serializer = self.get_serializer(pedido)
            return Response(serializer.data)
        except Pedido.DoesNotExist:
            # Se não houver pedido aberto, cria um novo
            try:
                with transaction.atomic():
                    novo_pedido = Pedido.objects.create(mesa=mesa, status='aberto')
                    serializer = self.get_serializer(novo_pedido)
                    return Response(serializer.data, status=status.HTTP_201_CREATED)
            except Exception as e:
                return Response({'detail': f'Erro ao criar novo pedido: {str(e)}'}, status=status.HTTP_400_BAD_REQUEST)
        except Mesa.DoesNotExist:
            return Response({'detail': 'Mesa não encontrada.'}, status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            return Response({'detail': f'Ocorreu um erro inesperado: {str(e)}'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    @action(detail=True, methods=['post'])
    def adicionar_item(self, request, pk=None):
        pedido = self.get_object()
        cardapio_id = request.data.get('cardapio')
        quantidade = request.data.get('quantidade')

        if not cardapio_id or not quantidade:
            return Response({'detail': 'ID do item do cardápio e quantidade são obrigatórios.'}, status=status.HTTP_400_BAD_REQUEST)

        try:
            item_cardapio = get_object_or_404(ItemCardapio, pk=cardapio_id)
            quantidade = int(quantidade)
            if quantidade <= 0:
                return Response({'detail': 'Quantidade deve ser maior que zero.'}, status=status.HTTP_400_BAD_REQUEST)

            # Verifica se o item já existe no pedido para atualizar a quantidade
            item_pedido, created = ItemPedido.objects.get_or_create(
                pedido=pedido, 
                cardapio=item_cardapio,
                envio_cozinha__isnull=True # Apenas considere itens que ainda não foram enviados para a cozinha
            )
            
            if created:
                item_pedido.quantidade = quantidade
            else:
                item_pedido.quantidade += quantidade
            
            item_pedido.save() # O método save() do ItemPedido agora calcula o subtotal e atualiza o total do Pedido

            serializer = ItemPedidoSerializer(item_pedido)
            return Response(serializer.data, status=status.HTTP_200_OK)
        except ItemCardapio.DoesNotExist:
            return Response({'detail': 'Item do cardápio não encontrado.'}, status=status.HTTP_404_NOT_FOUND)
        except ValueError:
            return Response({'detail': 'Quantidade deve ser um número inteiro válido.'}, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            return Response({'detail': f'Erro ao adicionar item: {str(e)}'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    @action(detail=True, methods=['delete'], url_path='remover_item/(?P<item_pedido_id>\d+)')
    def remover_item(self, request, pk=None, item_pedido_id=None):
        pedido = self.get_object()
        
        try:
            item_pedido = get_object_or_404(ItemPedido, pk=item_pedido_id, pedido=pedido)
            
            # Impedir a remoção se o item já foi enviado para a cozinha
            if item_pedido.envio_cozinha:
                return Response({'detail': 'Não é possível remover um item que já foi enviado para a cozinha.'}, status=status.HTTP_400_BAD_REQUEST)
            
            item_pedido.delete()
            
            # CORREÇÃO: Atualiza o valor total do pedido após a remoção
            pedido.update_valor_total() 

            return Response(status=status.HTTP_204_NO_CONTENT)
        except ItemPedido.DoesNotExist:
            return Response({'detail': 'Item do pedido não encontrado.'}, status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            return Response({'detail': f'Erro ao remover item: {str(e)}'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    @action(detail=True, methods=['post'])
    def enviar_para_cozinha(self, request, pk=None):
        pedido = self.get_object()
        itens_ids = request.data.get('itens_ids', [])
        observacoes_envio = request.data.get('observacoes_envio', '')

        if not itens_ids:
            return Response({'detail': 'Pelo menos um item deve ser selecionado para envio.'}, status=status.HTTP_400_BAD_REQUEST)

        try:
            with transaction.atomic():
                # Garante que os itens pertencem a este pedido e ainda não foram enviados
                itens_a_enviar = ItemPedido.objects.filter(
                    pedido=pedido, 
                    id__in=itens_ids, 
                    envio_cozinha__isnull=True
                )

                if not itens_a_enviar.exists():
                    return Response({'detail': 'Nenhum item válido encontrado para envio ou já foram enviados.'}, status=status.HTTP_400_BAD_REQUEST)

                # Cria um novo EnvioCozinha
                envio = EnvioCozinha.objects.create(
                    pedido=pedido,
                    observacoes_envio=observacoes_envio
                )

                # Associa os itens ao EnvioCozinha
                for item in itens_a_enviar:
                    item.envio_cozinha = envio
                    item.save() # Isso já atualiza o subtotal e o total do pedido principal

                # O valor total do pedido principal já deve ser atualizado pelo item.save()
                # Mas para garantir a consistência, podemos chamar novamente, embora tecnicamente redundante
                pedido.update_valor_total() 

                serializer = EnvioCozinhaSerializer(envio)
                return Response(serializer.data, status=status.HTTP_201_CREATED)

        except Exception as e:
            return Response({'detail': f'Erro ao enviar itens para a cozinha: {str(e)}'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    @action(detail=True, methods=['post'])
    def finalizar_pedido(self, request, pk=None):
        pedido = self.get_object()

        if pedido.status == 'fechado' or pedido.status == 'cancelado':
            return Response({'detail': 'Pedido já está fechado ou cancelado.'}, status=status.HTTP_400_BAD_REQUEST)

        # NOVOS: Captura gorjeta e observações do corpo da requisição
        gorjeta = request.data.get('gorjeta')
        observacoes_finalizacao = request.data.get('observacoes_finalizacao', '')

        try:
            with transaction.atomic():
                pedido.status = 'fechado'
                
                # Atribui a gorjeta e observações ao pedido
                if gorjeta is not None:
                    try:
                        pedido.gorjeta = float(gorjeta) # Converte para float antes de atribuir
                    except (ValueError, TypeError):
                        return Response({'detail': 'Gorjeta deve ser um valor numérico válido.'}, status=status.HTTP_400_BAD_REQUEST)
                else:
                    pedido.gorjeta = None # Garante que seja null se não for fornecido

                if observacoes_finalizacao is not None:
                    pedido.observacoes_finalizacao = observacoes_finalizacao
                else:
                    pedido.observacoes_finalizacao = '' # Garante que seja string vazia se não for fornecido

                pedido.save() # Salva o status do pedido e os novos campos

                # Garante que o valor total esteja finalizado corretamente antes de fechar o pedido
                # O update_valor_total agora considera a gorjeta
                pedido.update_valor_total() 
                
                serializer = self.get_serializer(pedido)
                return Response(serializer.data, status=status.HTTP_200_OK)
        except Exception as e:
            return Response({'detail': f'Erro ao finalizar pedido: {str(e)}'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class EnvioCozinhaViewSet(viewsets.ModelViewSet):
    queryset = EnvioCozinha.objects.all()
    serializer_class = EnvioCozinhaSerializer

    @action(detail=True, methods=['patch'], url_path='status_envio')
    def update_status_envio(self, request, pk=None):
        envio = self.get_object()
        new_status = request.data.get('status')

        if not new_status or new_status not in [choice[0] for choice in EnvioCozinha.STATUS_CHOICES]:
            return Response({'detail': 'Status inválido.'}, status=status.HTTP_400_BAD_REQUEST)
        
        try:
            envio.status = new_status
            envio.save()

            # ************** AQUI ESTÁ A CORREÇÃO PRINCIPAL **************
            # Após salvar a alteração de status do envio,
            # precisamos garantir que o pedido principal seja recalculado.
            # Isso é crucial para que o valor total reflita os itens de envios cancelados/não cancelados.
            envio.pedido.update_valor_total()
            # *************************************************************
            
            serializer = self.get_serializer(envio)
            return Response(serializer.data, status=status.HTTP_200_OK)
        except Exception as e:
            return Response({'detail': f'Erro ao atualizar status do envio: {str(e)}'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
