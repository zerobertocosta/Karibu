# backend/pedido/models/__init__.py

from mesa.models import Mesa # Importa Mesa do app 'mesa'
from cardapio.models import Categoria, ItemCardapio # CORRIGIDO: Categoria, não CategoriaCardapio
from .pedido import Pedido, ItemPedido
from .envio_cozinha import EnvioCozinha