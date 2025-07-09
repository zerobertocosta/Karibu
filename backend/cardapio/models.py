# backend/cardapio/models.py

from django.db import models
from configuracao.models import Estabelecimento

class Categoria(models.Model):
    estabelecimento = models.ForeignKey(
        Estabelecimento,
        on_delete=models.CASCADE,
        related_name='categorias',
        verbose_name='Estabelecimento'
    )
    nome = models.CharField(max_length=100, unique=False)
    descricao = models.TextField(blank=True, null=True)
    ativa = models.BooleanField(default=True)
    ordem = models.IntegerField(default=0, help_text="Ordem de exibição da categoria no cardápio")
    data_criacao = models.DateTimeField(auto_now_add=True)
    data_atualizacao = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Categoria do Cardápio"
        verbose_name_plural = "Categorias do Cardápio"
        unique_together = ('nome', 'estabelecimento')
        ordering = ['ordem', 'nome']

    def __str__(self):
        return f"{self.nome} ({self.estabelecimento.nome})"

# NOVO MODELO: ItemCardapio
class ItemCardapio(models.Model):
    # Relacionamento com Estabelecimento (para multi-tenancy)
    estabelecimento = models.ForeignKey(
        Estabelecimento,
        on_delete=models.CASCADE,
        related_name='itens_cardapio',
        verbose_name='Estabelecimento'
    )
    # Relacionamento com Categoria (deve ser do MESMO estabelecimento)
    categoria = models.ForeignKey(
        Categoria,
        on_delete=models.CASCADE,
        related_name='itens',
        verbose_name='Categoria'
    )
    nome = models.CharField(max_length=150, unique=False) # unique=False para permitir nomes iguais em diferentes estabelecimentos/categorias
    descricao = models.TextField(blank=True, null=True)
    preco = models.DecimalField(max_digits=10, decimal_places=2)
    disponivel = models.BooleanField(default=True)
    imagem = models.ImageField(upload_to='itens_cardapio/', blank=True, null=True)
    ordem = models.IntegerField(default=0, help_text="Ordem de exibição do item na categoria")
    data_criacao = models.DateTimeField(auto_now_add=True)
    data_atualizacao = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Item de Cardápio"
        verbose_name_plural = "Itens de Cardápio"
        # Garante que a combinação de nome E estabelecimento E categoria seja única
        unique_together = ('nome', 'estabelecimento', 'categoria')
        ordering = ['ordem', 'nome']

    def __str__(self):
        return f"{self.nome} ({self.categoria.nome} - {self.estabelecimento.nome})"

    # Adicionar validação customizada para garantir que categoria e item pertençam ao mesmo estabelecimento
    def clean(self):
        # Garante que a categoria selecionada pertence ao mesmo estabelecimento do item
        if self.categoria and self.estabelecimento and self.categoria.estabelecimento != self.estabelecimento:
            from django.core.exceptions import ValidationError
            raise ValidationError(
                {'categoria': 'A categoria deve pertencer ao mesmo estabelecimento do item.'}
            )
        super().clean()

    def save(self, *args, **kwargs):
        self.full_clean() # Chama clean() para executar validações antes de salvar
        super().save(*args, **kwargs)