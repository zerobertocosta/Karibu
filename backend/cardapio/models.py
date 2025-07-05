# backend/cardapio/models.py
from django.db import models
from configuracao.models import Estabelecimento # Importa Estabelecimento

class Categoria(models.Model):
    # Foreign Key para Estabelecimento
    estabelecimento = models.ForeignKey(
        Estabelecimento,
        on_delete=models.CASCADE,
        related_name='categorias_cardapio',
        verbose_name="Estabelecimento"
    )
    nome = models.CharField(max_length=100) # Removido unique=True daqui
    descricao = models.TextField(blank=True, null=True)

    class Meta:
        unique_together = ('estabelecimento', 'nome') # Unicidade por estabelecimento
        verbose_name = "Categoria de Cardápio"
        verbose_name_plural = "Categorias de Cardápio"
        ordering = ['nome'] # Ordenar categorias pelo nome
    
    def __str__(self):
        return f"{self.nome} ({self.estabelecimento.nome})"

class ItemCardapio(models.Model):
    # Foreign Key para Estabelecimento (também para itens do cardápio)
    estabelecimento = models.ForeignKey(
        Estabelecimento,
        on_delete=models.CASCADE,
        related_name='itens_cardapio',
        verbose_name="Estabelecimento"
    )
    categoria = models.ForeignKey(Categoria, on_delete=models.CASCADE, related_name='itens')
    nome = models.CharField(max_length=200) # Removido unique=True daqui
    descricao = models.TextField(blank=True, null=True)
    preco = models.DecimalField(max_digits=6, decimal_places=2)
    disponivel = models.BooleanField(default=True)
    imagem = models.ImageField(upload_to='cardapio_imagens/', blank=True, null=True)

    class Meta:
        unique_together = ('estabelecimento', 'nome') # Unicidade por estabelecimento
        verbose_name = "Item de Cardápio"
        verbose_name_plural = "Itens de Cardápio"
        ordering = ['categoria__nome', 'nome'] # Ordenar por categoria e depois por nome
    
    def __str__(self):
        return f"{self.nome} ({self.estabelecimento.nome})"