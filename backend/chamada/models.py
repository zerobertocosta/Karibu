# backend/chamada/models.py

from django.db import models
from mesa.models import Mesa

class ChamadaGarcom(models.Model):
    STATUS_CHOICES = [
        ('pendente', 'Pendente'),
        ('resolvida', 'Resolvida'),
        # Você pode adicionar outros status se necessário, ex: ('cancelada', 'Cancelada')
    ]

    mesa = models.ForeignKey(Mesa, on_delete=models.CASCADE, related_name='chamadas_garcom', verbose_name="Mesa")
    data_hora_chamada = models.DateTimeField(auto_now_add=True, verbose_name="Data e Hora da Chamada")
    # ALTERAÇÃO: 'atendida' foi substituído por 'status' com choices
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pendente', verbose_name="Status da Chamada")

    class Meta:
        verbose_name = "Chamada de Garçom"
        verbose_name_plural = "Chamadas de Garçom"
        # ALTERAÇÃO: Ordena as chamadas pelas mais recentes e pendentes primeiro.
        # Isso significa que 'pendente' virá antes de 'resolvida', e dentro de cada status, as mais recentes primeiro.
        ordering = ['status', '-data_hora_chamada']

    def __str__(self):
        return f"Chamada da Mesa {self.mesa.numero} às {self.data_hora_chamada.strftime('%H:%M')} - {self.get_status_display()}"