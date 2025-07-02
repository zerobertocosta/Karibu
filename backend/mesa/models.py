# backend/mesa/models.py
from django.db import models
from estabelecimento.models import Estabelecimento # Importa Estabelecimento

class Mesa(models.Model):
    numero = models.IntegerField(unique=True, verbose_name="Número da Mesa")
    
    # Tornando o campo estabelecimento opcional para facilitar testes,
    # ou para permitir mesas sem estabelecimento associado por enquanto.
    # No futuro, se for sempre obrigatório, remova null=True, blank=True
    estabelecimento = models.ForeignKey(
        Estabelecimento, 
        on_delete=models.CASCADE, 
        related_name='mesas',
        null=True,    # Permite que o campo seja NULL no banco de dados
        blank=True,   # Permite que o campo seja vazio no formulário do Admin
        verbose_name="Estabelecimento Associado"
    )
    
    capacidade = models.IntegerField(default=4, verbose_name="Capacidade de Pessoas")
    disponivel = models.BooleanField(default=True, verbose_name="Mesa Disponível")
    data_cadastro = models.DateTimeField(auto_now_add=True, verbose_name="Data de Cadastro")

    class Meta:
        verbose_name = "Mesa"
        verbose_name_plural = "Mesas"
        ordering = ['numero']

    def __str__(self):
        # Proteção para o caso de o estabelecimento ser None
        if self.estabelecimento:
            return f"Mesa {self.numero} ({self.estabelecimento.nome})"
        return f"Mesa {self.numero} (Sem Estabelecimento)"
