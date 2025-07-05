# backend/pedido/models/pedido.py

from django.db import models
from django.db.models import Sum, F, Q
from django.core.exceptions import ValidationError

# Importa os modelos de outros apps se necessário
from mesa.models import Mesa
from cardapio.models import ItemCardapio
from configuracao.models import Estabelecimento # Importa Estabelecimento

class Pedido(models.Model):
    # Foreign Key para Estabelecimento
    estabelecimento = models.ForeignKey(
        Estabelecimento,
        on_delete=models.CASCADE,
        related_name='pedidos',
        verbose_name="Estabelecimento"
    )

    STATUS_CHOICES = [
        ('aberto', 'Aberto'),
        ('em_preparo', 'Em Preparo'),
        ('fechado', 'Fechado'),
        ('cancelado', 'Cancelado'),
    ]

    mesa = models.ForeignKey(Mesa, on_delete=models.SET_NULL, null=True, blank=True, related_name='pedidos', verbose_name="Mesa")
    data_hora_pedido = models.DateTimeField(auto_now_add=True, verbose_name="Data e Hora do Pedido")
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='aberto', verbose_name="Status do Pedido")
    
    # Campo para armazenar o valor total calculado
    valor_total = models.DecimalField(max_digits=10, decimal_places=2, default=0.00, verbose_name="Valor Total")

    # Campos: Gorjeta e Observações na Finalização (já existentes)
    gorjeta = models.DecimalField(max_digits=10, decimal_places=2, default=0.00, blank=True, null=True, verbose_name="Valor da Gorjeta")
    observacoes_finalizacao = models.TextField(blank=True, null=True, verbose_name="Observações do Cliente na Finalização")

    def __str__(self):
        return f"Pedido {self.id} - Mesa {self.mesa.numero if self.mesa else 'N/A'} ({self.estabelecimento.nome}) - Status: {self.get_status_display()}"

    def update_valor_total(self):
        # MENSAGEM DE DEBUG MUITO DETALHADA
        print(f"\n--- DEBUG: Pedido {self.id} - Início de update_valor_total ---")
        print(f"DEBUG: Valor total atual do pedido ANTES do cálculo: {self.valor_total}")
        
        # Obter todos os ItemPedido relacionados a este Pedido
        all_itens_pedido = self.itens_pedido.all()
        print(f"DEBUG: Todos os ItemPedido do Pedido {self.id}:")
        for item in all_itens_pedido:
            status_envio = item.envio_cozinha.status if item.envio_cozinha else "N/A (não enviado)"
            print(f"   - ItemPedido ID: {item.id}, Cardapio: {item.cardapio.nome}, Subtotal: {item.subtotal}, EnvioCozinha ID: {item.envio_cozinha.id if item.envio_cozinha else 'N/A'}, Status Envio: {status_envio}")

        # Construir o filtro para itens elegíveis:
        # 1. Itens que NÃO POSSUEM um envio_cozinha (ainda estão no "carrinho" do pedido)
        # 2. OU itens que POSSUEM um envio_cozinha cujo status NÃO É 'cancelado'
        eligible_items_filter = Q(envio_cozinha__isnull=True) | ~Q(envio_cozinha__status='cancelado')
        print(f"DEBUG: Filtro aplicado (Q object): {eligible_items_filter}")

        # Obter o queryset de itens elegíveis baseado no filtro
        eligible_items_queryset = self.itens_pedido.filter(eligible_items_filter)
        print(f"DEBUG: Itens **elegíveis** para a soma (queryset filtrado):")
        for item in eligible_items_queryset:
            status_envio = item.envio_cozinha.status if item.envio_cozinha else "N/A (não enviado)"
            print(f"   - ItemPedido ID: {item.id}, Cardapio: {item.cardapio.nome}, Subtotal: {item.subtotal}, EnvioCozinha ID: {item.envio_cozinha.id if item.envio_cozinha else 'N/A'}, Status Envio: {status_envio}")


        total_sum_result = eligible_items_queryset.aggregate(total_sum=Sum('subtotal')).get('total_sum')
        total = total_sum_result if total_sum_result is not None else 0
        
        # Adiciona a gorjeta ao valor total final, se houver
        if self.gorjeta is not None:
            total += self.gorjeta
            print(f"DEBUG: Gorjeta ({self.gorjeta}) adicionada ao total.")

        print(f"DEBUG: Soma CALCULADA para itens elegíveis (incluindo gorjeta, SEM couvert agora): {total}")

        if self.valor_total != total: 
            old_value = self.valor_total
            self.valor_total = total
            self.save(update_fields=['valor_total']) # Salva apenas o campo valor_total
            print(f"DEBUG: Pedido {self.id} SALVO. Valor total ATUALIZADO de {old_value} para {self.valor_total}")
        else:
            print(f"DEBUG: Pedido {self.id} NÃO SALVO. Valor total permaneceu: {self.valor_total}")
        print(f"--- DEBUG: Pedido {self.id} - Fim de update_valor_total ---\n")


    class Meta:
        verbose_name = "Pedido"
        verbose_name_plural = "Pedidos"
        ordering = ['-data_hora_pedido']


class ItemPedido(models.Model):
    # Foreign Key para Estabelecimento - ItemPedido deve herdar do Pedido, ou ter sua própria FK
    # Para simplicidade e consistência, cada ItemPedido também apontará para um Estabelecimento.
    # Em um cenário real, você pode optar por derivar isso do Pedido, mas ter a FK direta evita JOINs complexos em algumas queries.
    estabelecimento = models.ForeignKey(
        Estabelecimento,
        on_delete=models.CASCADE,
        related_name='itens_pedido', # Nome diferente do Pedido para evitar conflito
        verbose_name="Estabelecimento"
    )

    pedido = models.ForeignKey(Pedido, on_delete=models.CASCADE, related_name='itens_pedido', verbose_name="Pedido")
    cardapio = models.ForeignKey(ItemCardapio, on_delete=models.CASCADE, verbose_name="Item do Cardápio")
    quantidade = models.PositiveIntegerField(default=1, verbose_name="Quantidade")
    
    subtotal = models.DecimalField(max_digits=10, decimal_places=2, default=0.00, verbose_name="Subtotal")
    
    envio_cozinha = models.ForeignKey('EnvioCozinha', on_delete=models.SET_NULL, null=True, blank=True, related_name='itens_enviados', verbose_name="Envio para Cozinha")

    def __str__(self):
        return f"{self.quantidade}x {self.cardapio.nome} (Pedido {self.pedido.id} - {self.estabelecimento.nome})"

    def save(self, *args, **kwargs):
        print(f"DEBUG: ItemPedido.save() - Item {self.id if self.id else 'NOVO'} antes do cálculo do subtotal. Cardapio ID: {self.cardapio.id if self.cardapio else 'N/A'}, Quantidade: {self.quantidade}")

        if self.cardapio and self.quantidade is not None:
            preco_decimal = models.DecimalField(max_digits=10, decimal_places=2).to_python(self.cardapio.preco)
            self.subtotal = preco_decimal * self.quantidade
            print(f"DEBUG: ItemPedido.save() - Subtotal calculado: {self.subtotal}")
        else:
            self.subtotal = 0.00
            print(f"DEBUG: ItemPedido.save() - Subtotal definido para 0.00 (faltando cardapio ou quantidade)")
            
        super().save(*args, **kwargs)
        print(f"DEBUG: ItemPedido.save() - Item {self.id} salvo. Subtotal final: {self.subtotal}")

        if self.pedido and hasattr(self.pedido, 'update_valor_total'):
            print(f"DEBUG: ItemPedido.save() - Chamando update_valor_total para Pedido {self.pedido.id}")
            self.pedido.update_valor_total()
        else:
            print(f"DEBUG: ItemPedido.save() - Não chamou update_valor_total (pedido não existe ou método ausente)")

    class Meta:
        verbose_name = "Item do Pedido"
        verbose_name_plural = "Itens do Pedido"