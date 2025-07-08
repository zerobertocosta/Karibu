# backend/configuracao/models.py

from django.db import models
from django.conf import settings
import uuid

class Estabelecimento(models.Model):
    """
    Representa um estabelecimento (restaurante, bar, cafeteria, etc.) dentro do sistema.
    Cada dado sensível no sistema será vinculado a um Estabelecimento.
    """
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    nome = models.CharField(max_length=255, unique=True, verbose_name="Nome do Estabelecimento")
    cnpj = models.CharField(max_length=18, unique=True, null=True, blank=True, verbose_name="CNPJ")
    endereco = models.CharField(max_length=255, null=True, blank=True, verbose_name="Endereço")
    telefone = models.CharField(max_length=20, null=True, blank=True, verbose_name="Telefone")
    email_contato = models.EmailField(max_length=255, null=True, blank=True, verbose_name="Email de Contato")
    chave_pix = models.CharField(max_length=255, null=True, blank=True, verbose_name="Chave PIX")
    logotipo_url = models.URLField(max_length=500, null=True, blank=True, verbose_name="URL do Logotipo")
    cor_primaria = models.CharField(max_length=7, default="#007bff", verbose_name="Cor Primária (HEX)")
    cor_secundaria = models.CharField(max_length=7, default="#6c757d", verbose_name="Cor Secundária (HEX)")
    ativo = models.BooleanField(default=True, verbose_name="Ativo")
    data_criacao = models.DateTimeField(auto_now_add=True, verbose_name="Data de Criação")
    data_atualizacao = models.DateTimeField(auto_now=True, verbose_name="Última Atualização")

    class Meta:
        verbose_name = "Estabelecimento"
        verbose_name_plural = "Estabelecimentos"
        ordering = ['nome'] # Ordenar por nome por padrão

    def __str__(self):
        return self.nome

    def save(self, *args, **kwargs):
        # Opcional: Garante que o CNPJ seja salvo sem formatação, se fornecido
        if self.cnpj:
            self.cnpj = ''.join(filter(str.isdigit, self.cnpj))
        super().save(*args, **kwargs)