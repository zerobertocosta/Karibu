# backend/chamada/models.py

from django.db import models
from mesa.models import Mesa
from configuracao.models import Estabelecimento # Importa Estabelecimento

class ChamadaGarcom(models.Model):
    # Foreign Key para Estabelecimento
    estabelecimento = models.ForeignKey(
        Estabelecimento,
        on_delete=models.CASCADE,
        related_name='chamadas_garcom',
        verbose_name="Estabelecimento"
    )
    
    mesa = models.ForeignKey(Mesa, on_delete=models.CASCADE, related_name='chamadas')
    data_hora_chamada = models.DateTimeField(auto_now_add=True)
    
    STATUS_CHOICES = [
        ('pendente', 'Pendente'),
        ('resolvida', 'Resolvida'),
    ]
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='pendente')

    class Meta:
        verbose_name = "Chamada de Garçom"
        verbose_name_plural = "Chamadas de Garçons"
        ordering = ['status', '-data_hora_chamada'] # Primeiro pendentes, depois por data mais recente

    def __str__(self):
        return f"Chamada para Mesa {self.mesa.numero} no {self.estabelecimento.nome} - Status: {self.get_status_display()}"