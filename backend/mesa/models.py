# backend/mesa/models.py
from django.db import models
from configuracao.models import Estabelecimento # Importa Estabelecimento do app 'configuracao'

class Mesa(models.Model):
    # Foreign Key para Estabelecimento.
    # Será sempre obrigatório. Removido null=True, blank=True.
    estabelecimento = models.ForeignKey(
        Estabelecimento,
        on_delete=models.CASCADE,
        related_name='mesas',
        verbose_name="Estabelecimento"
    )
    
    # Removido unique=True daqui, a unicidade será garantida por unique_together
    numero = models.IntegerField(verbose_name="Número da Mesa") 
    capacidade = models.IntegerField(default=4, verbose_name="Capacidade de Pessoas")
    disponivel = models.BooleanField(default=True, verbose_name="Mesa Disponível")
    data_cadastro = models.DateTimeField(auto_now_add=True, verbose_name="Data de Cadastro")

    class Meta:
        # Garante que o número da mesa seja único APENAS para um determinado estabelecimento
        unique_together = ('estabelecimento', 'numero')
        verbose_name = "Mesa"
        verbose_name_plural = "Mesas"
        ordering = ['numero']

    def __str__(self):
        return f"Mesa {self.numero} ({self.estabelecimento.nome})"