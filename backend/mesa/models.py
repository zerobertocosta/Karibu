# backend/mesa/models.py

from django.db import models
from configuracao.models import Estabelecimento # Importa o modelo Estabelecimento

class Mesa(models.Model):
    STATUS_CHOICES = [
        ('LIVRE', 'Livre'),
        ('OCUPADA', 'Ocupada'),
        ('RESERVADA', 'Reservada'),
        ('MANUTENCAO', 'Em Manutenção'),
    ]

    estabelecimento = models.ForeignKey(
        Estabelecimento,
        on_delete=models.CASCADE,
        related_name='mesas',
        verbose_name='Estabelecimento'
    )
    numero = models.CharField(max_length=50, unique=False,
                              help_text="Número ou identificador da mesa (ex: 'Mesa 5', 'Balcão A')")
    capacidade = models.IntegerField(
        default=2,
        help_text="Capacidade máxima de pessoas nesta mesa"
    )
    status = models.CharField(
        max_length=15,
        choices=STATUS_CHOICES,
        default='LIVRE',
        verbose_name='Status da Mesa'
    )
    descricao = models.TextField(
        blank=True,
        null=True,
        help_text="Breve descrição ou localização da mesa (opcional)"
    )
    data_criacao = models.DateTimeField(auto_now_add=True)
    data_atualizacao = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Mesa"
        verbose_name_plural = "Mesas"
        # Garante que não haja duas mesas com o mesmo número/identificador no mesmo estabelecimento
        unique_together = (('numero', 'estabelecimento'),)
        ordering = ['numero']

    def __str__(self):
        return f"Mesa {self.numero} ({self.estabelecimento.nome})"

    def clean(self):
        from django.core.exceptions import ValidationError
        # Validação extra para garantir unicidade do número da mesa por estabelecimento,
        # se o unique_together não for suficiente ou para mensagens mais claras.
        if self.estabelecimento:
            query = Mesa.objects.filter(numero=self.numero, estabelecimento=self.estabelecimento)
            if self.pk: # Se estiver atualizando uma mesa existente
                query = query.exclude(pk=self.pk)
            if query.exists():
                raise ValidationError({'numero': f"Já existe uma mesa com o número '{self.numero}' para este estabelecimento."})

    def save(self, *args, **kwargs):
        self.full_clean() # Executa o método clean() antes de salvar
        super().save(*args, **kwargs)