# backend/core/urls.py

from django.contrib import admin
from django.urls import path, include
from rest_framework.routers import DefaultRouter

# Importar ViewSets dos seus apps
from estabelecimento.views import EstabelecimentoViewSet
from mesa.views import MesaViewSet
from cardapio.views import CategoriaViewSet, ItemCardapioViewSet
from pedido.views import PedidoViewSet, EnvioCozinhaViewSet # NOVO: Importar EnvioCozinhaViewSet
from cliente.views import ClienteViewSet # NOVO: Importar ClienteViewSet

# Criar um router para registrar os ViewSets
router = DefaultRouter()
router.register(r'estabelecimento', EstabelecimentoViewSet)
router.register(r'mesa', MesaViewSet)
router.register(r'cardapio/categorias', CategoriaViewSet) # Rota para categorias
router.register(r'cardapio/itens', ItemCardapioViewSet) # Rota para itens de cardápio
router.register(r'pedido', PedidoViewSet)
router.register(r'envios_cozinha', EnvioCozinhaViewSet) # NOVO: Registrar EnvioCozinhaViewSet
router.register(r'cliente', ClienteViewSet) # NOVO: Registrar ClienteViewSet


urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/', include(router.urls)), # Inclui todas as rotas registradas no router
]
