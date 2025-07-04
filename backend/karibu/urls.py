# Seu urls.py (ex: backend/karibu/urls.py)

from django.contrib import admin
from django.urls import path, include
from rest_framework.routers import DefaultRouter # <--- Certifique-se que esta importação existe

# Importe suas views, por exemplo:
from pedido import views as pedido_views

router = DefaultRouter()
router.register(r'mesas', pedido_views.MesaViewSet) # Se você tem um MesaViewSet
router.register(r'cardapio', pedido_views.ItemCardapioViewSet) # Se você tem um ItemCardapioViewSet
router.register(r'pedido', pedido_views.PedidoViewSet) # <--- ESSENCIAL PARA O PEDIDOVIEWSET
router.register(r'itempedido', pedido_views.ItemPedidoViewSet) # Se você tem um ItemPedidoViewSet


urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/', include(router.urls)), # <--- ESSENCIAL para que as URLs do ViewSet sejam geradas automaticamente

    # Certifique-se de que NÃO HÁ MAIS ESTA LINHA:
    # path('api/pedido/aberto/<int:mesa_id>/', pedido_views.pedido_aberto_mesa, name='pedido_aberto_mesa'),

    # Mantenha as outras rotas @api_view que você ainda usa:
    path('api/pedido/criar/', pedido_views.criar_novo_pedido, name='criar_novo_pedido'),
    path('api/pedido/adicionar_itens/', pedido_views.adicionar_itens_ao_pedido, name='adicionar_itens_ao_pedido'),
    path('api/pedido/enviar_cozinha/<int:pedido_id>/', pedido_views.enviar_para_cozinha, name='enviar_para_cozinha'),
    # ... outras rotas personalizadas se houver
]