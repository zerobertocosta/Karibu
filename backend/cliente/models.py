# backend/cliente/models.py

from django.db import models
from django.core.exceptions import ValidationError
from django.utils.translation import gettext_lazy as _
import uuid
from configuracao.models import Estabelecimento # Importa o Estabelecimento

class Cliente(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    celular = models.CharField(max_length=20, unique=False) # Não unique=True aqui se a unicidade é por celular+estabelecimento
    nome_completo = models.CharField(max_length=255)
    data_nascimento = models.DateField(null=True, blank=True)
    logradouro = models.CharField(max_length=255, null=True, blank=True)
    numero = models.CharField(max_length=10, null=True, blank=True)
    bairro = models.CharField(max_length=100, null=True, blank=True)
    cidade = models.CharField(max_length=100, null=True, blank=True)
    estado = models.CharField(max_length=2, null=True, blank=True)
    cep = models.CharField(max_length=9, null=True, blank=True)
    foto_cliente = models.ImageField(upload_to='clientes/fotos/', null=True, blank=True)
    data_cadastro = models.DateTimeField(auto_now_add=True)
    data_atualizacao = models.DateTimeField(auto_now=True)
    # Relação com Estabelecimento
    estabelecimento = models.ForeignKey(
        Estabelecimento,
        on_delete=models.CASCADE,
        related_name='clientes'
    )

    class Meta:
        # Define a unicidade combinada de celular e estabelecimento
        unique_together = ('celular', 'estabelecimento',)
        verbose_name = _("Cliente")
        verbose_name_plural = _("Clientes")
        ordering = ['nome_completo']

    def __str__(self):
        return f"{self.nome_completo} ({self.celular})"

    def clean(self):
        super().clean()
        # Garante que a unicidade de celular seja por estabelecimento
        if self.celular and self.estabelecimento_id: # Corrigido para _id
            qs = Cliente.objects.filter(celular=self.celular, estabelecimento=self.estabelecimento)
            if self.pk: # Exclui o próprio objeto se estiver sendo atualizado
                qs = qs.exclude(pk=self.pk)
            if qs.exists():
                raise ValidationError({
                    'celular': _("Já existe um cliente com este celular para este estabelecimento.")
                })

    def save(self, *args, **kwargs):
        self.full_clean() # Executa o método clean() antes de salvar
        super().save(*args, **kwargs)