# backend/pedido/admin.py

from django.contrib import admin
# Importa os modelos definidos no app 'pedido' (dentro da pasta models/)
from .models.pedido import Pedido, ItemPedido
from .models.envio_cozinha import EnvioCozinha

# IMPORTANTE: Não importe Mesa, ItemCardapio, Categoria aqui se eles são registrados em seus próprios apps de admin.
# Se você tiver 'backend/mesa/admin.py' e 'backend/cardapio/admin.py' que já registram esses modelos,
# estas importações não são necessárias neste admin.py.
# Mas para o funcionamento dos Inlines e Serializers que referenciam, vamos manter as importações dos modelos.
from mesa.models import Mesa # Mantenha a importação para referências de FK se necessário
from cardapio.models import ItemCardapio, Categoria # Mantenha a importação para referências de FK se necessário


# Registre o novo modelo EnvioCozinha no admin
@admin.register(EnvioCozinha)
class EnvioCozinhaAdmin(admin.ModelAdmin):
    list_display = ('id', 'pedido', 'data_hora_envio', 'status', 'valor_total_envio')
    list_filter = ('status', 'data_hora_envio', 'pedido')
    search_fields = ('pedido__mesa__numero', 'observacoes')
    readonly_fields = ('data_hora_envio', 'valor_total_envio')
    raw_id_fields = ('pedido',)

# Inline para ItemPedido, permitindo adicionar/editar itens diretamente no Pedido
class ItemPedidoInline(admin.TabularInline):
    model = ItemPedido
    extra = 0 # Não mostra campos extras por padrão
    fields = ('cardapio', 'quantidade', 'subtotal', 'envio_cozinha') # Inclui o campo envio_cozinha
    readonly_fields = ('subtotal',)

# Registre o modelo Pedido no admin
@admin.register(Pedido)
class PedidoAdmin(admin.ModelAdmin):
    list_display = ('id', 'mesa', 'data_hora_pedido', 'status', 'valor_total')
    list_filter = ('status', 'data_hora_pedido', 'mesa')
    search_fields = ('mesa__numero',)
    inlines = [ItemPedidoInline] # Adiciona a edição de ItemPedido diretamente no Pedido
    readonly_fields = ('data_hora_pedido', 'valor_total')

# REMOVIDOS OS REGISTROS DUPLICADOS:
# @admin.register(Mesa)
# class MesaAdmin(admin.ModelAdmin):
#     list_display = ('numero', 'capacidade', 'disponivel')
#     list_filter = ('disponivel',)
#     search_fields = ('numero',)

# @admin.register(Categoria)
# class CategoriaAdmin(admin.ModelAdmin):
#     list_display = ('nome',)
#     search_fields = ('nome',)

# @admin.register(ItemCardapio)
# class ItemCardapioAdmin(admin.ModelAdmin):
#     list_display = ('nome', 'categoria', 'preco', 'disponivel')
#     list_filter = ('categoria', 'disponivel')
#     search_fields = ('nome', 'descricao')
#     raw_id_fields = ('categoria',)
