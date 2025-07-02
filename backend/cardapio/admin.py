# backend/cardapio/admin.py

from django.contrib import admin
from .models import Categoria, ItemCardapio

# Registra o modelo Categoria no painel de administração
@admin.register(Categoria)
class CategoriaAdmin(admin.ModelAdmin):
    list_display = ('nome',) # Campos a serem exibidos na lista de categorias

# Registra o modelo ItemCardapio no painel de administração
@admin.register(ItemCardapio)
class ItemCardapioAdmin(admin.ModelAdmin):
    list_display = ('nome', 'categoria', 'preco', 'disponivel')
    list_filter = ('categoria', 'disponivel') # Filtros na barra lateral
    search_fields = ('nome', 'descricao') # Campos para busca
    raw_id_fields = ('categoria',) # Ajuda a selecionar categoria em listas grandes