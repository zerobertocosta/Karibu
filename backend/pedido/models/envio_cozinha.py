# backend/pedido/models/envio_cozinha.py
from django.db import models
from django.db.models import Sum 
from .pedido import Pedido, ItemPedido # Importa o modelo Pedido e ItemPedido
from configuracao.models import Estabelecimento # Importa Estabelecimento

class EnvioCozinha(models.Model):
    # Foreign Key para Estabelecimento.
    # Será sempre obrigatório. Removido null=True, blank=True.
    estabelecimento = models.ForeignKey(
        Estabelecimento,
        on_delete=models.CASCADE,
        related_name='envios_cozinha',
        verbose_name="Estabelecimento"
    )
    
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
        return f"Envio {self.id} do Pedido {self.pedido.id} ({self.estabelecimento.nome}) - Status: {self.get_status_display()}"

    @property
    def valor_total_envio(self):
        total_sum_result = self.itens_enviados.aggregate(total=Sum('subtotal')).get('total')
        return total_sum_result if total_sum_result is not None else 0

    class Meta:
        verbose_name = "Envio para Cozinha"
        verbose_name_plural = "Envios para Cozinha"
        ordering = ['-data_hora_envio']