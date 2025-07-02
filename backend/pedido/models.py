# backend/pedido/models.py (Este é o arquivo principal, não a pasta!)
# Este arquivo agora serve apenas para importar todos os seus modelos do subpacote 'models'

from .models.mesa import Mesa
from .models.cardapio import CategoriaCardapio, Cardapio
from .models.pedido import Pedido, ItemPedido
from .models.envio_cozinha import EnvioCozinha

# Se você tiver algum modelo abstrato ou base, importe-o também
# from .models.base import MeuModeloBase