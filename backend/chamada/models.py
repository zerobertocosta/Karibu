# backend/chamada/models.py

from django.db import models
from mesa.models import Mesa # Importa o modelo Mesa

class ChamadaGarcom(models.Model):
    # Foreign Key para a Mesa que fez a chamada
    mesa = models.ForeignKey(Mesa, on_delete=models.CASCADE, related_name='chamadas_garcom', verbose_name="Mesa")
    # Data e hora em que a chamada foi criada
    data_hora_chamada = models.DateTimeField(auto_now_add=True, verbose_name="Data e Hora da Chamada")
    # Status da chamada: True se atendida, False se pendente
    atendida = models.BooleanField(default=False, verbose_name="Atendida")

    class Meta:
        verbose_name = "Chamada de Garçom"
        verbose_name_plural = "Chamadas de Garçom"
        # Ordena as chamadas pelas mais recentes primeiro (ou as pendentes antes)
        ordering = ['data_hora_chamada'] 

    def __str__(self):
        # Representação legível do objeto
        return f"Chamada da Mesa {self.mesa.numero} às {self.data_hora_chamada.strftime('%H:%M')} - {'Atendida' if self.atendida else 'Pendente'}"

