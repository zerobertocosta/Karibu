# backend/karibu/urls.py

from django.contrib import admin
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from mesa.views import MesaViewSet
# **** ATENÇÃO AQUI: Mudou de CategoriaCardapioViewSet para CategoriaViewSet ****
from cardapio.views import ItemCardapioViewSet, CategoriaViewSet 
from pedido.views import PedidoViewSet, EnvioCozinhaViewSet
from chamada.views import ChamadaGarcomViewSet # NOVO: Importa o novo ViewSet

router = DefaultRouter()
router.register(r'mesa', MesaViewSet)
router.register(r'cardapio/itens', ItemCardapioViewSet)
# **** ATENÇÃO AQUI: Mudou de CategoriaCardapioViewSet para CategoriaViewSet ****
router.register(r'cardapio/categorias', CategoriaViewSet) 
router.register(r'pedido', PedidoViewSet)
router.register(r'envios_cozinha', EnvioCozinhaViewSet)
router.register(r'chamadas-garcom', ChamadaGarcomViewSet, basename='chamada-garcom') # NOVO: Registra o ViewSet

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/', include(router.urls)),
]

