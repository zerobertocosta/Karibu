# backend/configuracao/models.py

from django.db import models

class Estabelecimento(models.Model):
    nome = models.CharField(max_length=255, unique=True, verbose_name="Nome do Estabelecimento")
    contato = models.CharField(max_length=100, blank=True, null=True, verbose_name="Contato Principal")
    email = models.EmailField(unique=True, verbose_name="Email de Contato")
    pais = models.CharField(max_length=100, verbose_name="País")
    cidade = models.CharField(max_length=100, verbose_name="Cidade")
    endereco = models.TextField(blank=True, null=True, verbose_name="Endereço Completo")
    chave_pix = models.CharField(max_length=255, blank=True, null=True, verbose_name="Chave PIX")

    # Campos para personalização visual
    logotipo_cabecalho = models.ImageField(upload_to='logos/', blank=True, null=True, verbose_name="Logotipo do Cabeçalho")
    imagem_fundo_sistema = models.ImageField(upload_to='backgrounds/', blank=True, null=True, verbose_name="Imagem de Fundo do Sistema")
    cor_primaria = models.CharField(max_length=7, default='#1976D2', verbose_name="Cor Primária (Hex)") # Ex: Azul Material Design
    cor_secundaria = models.CharField(max_length=7, default='#FFC107', verbose_name="Cor Secundária (Hex)") # Ex: Âmbar Material Design

    ativo = models.BooleanField(default=True, verbose_name="Ativo")
    data_cadastro = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "Estabelecimento"
        verbose_name_plural = "Estabelecimentos"
        ordering = ['nome']

    def __str__(self):
        return self.nome