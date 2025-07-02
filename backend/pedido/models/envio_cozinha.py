# backend/pedido/models/envio_cozinha.py

from django.db import models
from django.db.models import Sum

# Importa o modelo Pedido e ItemPedido
from .pedido import Pedido, ItemPedido

class EnvioCozinha(models.Model):
    STATUS_CHOICES = [
        ('aguardando_envio', 'Aguardando Envio'),
        ('em_preparo_cozinha', 'Em Preparo'),
        ('pronto_para_entrega', 'Pronto para Entrega'),
        ('entregue', 'Entregue'),
        ('cancelado', 'Cancelado'),
    ]

    pedido = models.ForeignKey(Pedido, on_delete=models.CASCADE, related_name='envios_cozinha', verbose_name="Pedido Principal")
    data_hora_envio = models.DateTimeField(auto_now_add=True, verbose_name="Data e Hora do Envio")
    status = models.CharField(max_length=30, choices=STATUS_CHOICES, default='aguardando_envio', verbose_name="Status do Envio")
    observacoes_envio = models.TextField(blank=True, null=True, verbose_name="Observações para Cozinha")

    def __str__(self):
        return f"Envio {self.id} do Pedido {self.pedido.id} - Status: {self.get_status_display()}"

    @property
    def valor_total_envio(self):
        # CORREÇÃO: Acessa a soma pelo alias 'total' e usa 'or 0' para garantir 0 se for None
        total_sum_result = self.itens_enviados.aggregate(total=Sum('subtotal')).get('total')
        return total_sum_result if total_sum_result is not None else 0

    class Meta:
        verbose_name = "Envio para Cozinha"
        verbose_name_plural = "Envios para Cozinha"
        ordering = ['-data_hora_envio']
