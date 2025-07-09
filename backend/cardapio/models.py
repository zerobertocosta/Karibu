# backend/cardapio/models.py

from django.db import models
# Importar o modelo Estabelecimento do app configuracao
from configuracao.models import Estabelecimento

class Categoria(models.Model):
    # Adicionando o campo estabelecimento como ForeignKey
    # CASCADE: Se o estabelecimento for deletado, suas categorias também serão.
    # related_name: Permite acessar categorias a partir de um estabelecimento (ex: estabelecimento.categorias.all())
    estabelecimento = models.ForeignKey(
        Estabelecimento,
        on_delete=models.CASCADE,
        related_name='categorias',
        verbose_name='Estabelecimento'
    )
    nome = models.CharField(max_length=100, unique=False) # unique=False pois o nome pode se repetir em outros estabelecimentos
    descricao = models.TextField(blank=True, null=True)
    ativa = models.BooleanField(default=True)
    ordem = models.IntegerField(default=0, help_text="Ordem de exibição da categoria no cardápio")
    data_criacao = models.DateTimeField(auto_now_add=True)
    data_atualizacao = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Categoria do Cardápio"
        verbose_name_plural = "Categorias do Cardápio"
        # Garante que a combinação de nome E estabelecimento seja única
        unique_together = ('nome', 'estabelecimento')
        ordering = ['ordem', 'nome'] # Ordena por ordem e depois por nome

    def __str__(self):
        return f"{self.nome} ({self.estabelecimento.nome})"

# O modelo ItemCardapio será modificado em um passo futuro para também incluir 'estabelecimento'
# e ser vinculado a uma Categoria do MESMO estabelecimento.