# backend/karibu/urls.py
from django.contrib import admin
from django.urls import path, include
from rest_framework import routers

# Importações dos ViewSets existentes (agora MesaViewSet vem do lugar certo)
from mesa.views import MesaViewSet
from cardapio.views import ItemCardapioViewSet
from pedido.views import PedidoViewSet

# Importações das funções @api_view
from pedido import views as pedido_views
from chamada import views as chamadas_views

router = routers.DefaultRouter()
router.register(r'mesas', MesaViewSet)
router.register(r'cardapio', ItemCardapioViewSet)
router.register(r'pedidos', PedidoViewSet)
# Removido router.register para ChamadaGarcomViewSet, pois não é um ViewSet

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/', include(router.urls)),
    
    # URLs para funcionalidades de pedido
    path('api/pedidos/aberto/<int:mesa_id>/', pedido_views.pedido_aberto_mesa, name='pedido_aberto_mesa'),
    path('api/pedidos/criar/', pedido_views.criar_novo_pedido, name='criar_novo_pedido'),
    path('api/pedidos/adicionar-itens/', pedido_views.adicionar_itens_ao_pedido, name='adicionar_itens_ao_pedido'),
    path('api/pedidos/<int:pedido_id>/enviar-cozinha/', pedido_views.enviar_para_cozinha, name='enviar_para_cozinha'),
    
    # URL para funcionalidade de chamada de garçom
    #path('api/chamadas-garcom/criar/', chamadas_views.criar_chamada_garcom, name='criar_chamada_garcom'),
]