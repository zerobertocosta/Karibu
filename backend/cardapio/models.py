# backend/cardapio/models.py
from django.db import models

class Categoria(models.Model):
    nome = models.CharField(max_length=100, unique=True)
    descricao = models.TextField(blank=True, null=True)

    def __str__(self):
        return self.nome

class ItemCardapio(models.Model):
    categoria = models.ForeignKey(Categoria, on_delete=models.CASCADE, related_name='itens')
    nome = models.CharField(max_length=200, unique=True)
    descricao = models.TextField(blank=True, null=True)
    preco = models.DecimalField(max_digits=6, decimal_places=2)
    disponivel = models.BooleanField(default=True)
    imagem = models.ImageField(upload_to='cardapio_imagens/', blank=True, null=True)

    def __str__(self):
        return self.nome