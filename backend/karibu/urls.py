# backend/karibu/urls.py (seu urls.py principal)

from django.contrib import admin
from django.urls import path, include
from rest_framework.routers import DefaultRouter

# IMPORTAÇÕES ESSENCIAIS:
# Importe as views que você quer registrar DIRETAMENTE neste router principal,
# SE ELAS NÃO TIVEREM SEUS PRÓPRIOS ARQUIVOS urls.py COM DefaultRouter
from pedido import views as pedido_views # Para MesaViewSet, PedidoViewSet, etc.

# --- ATENÇÃO: Verifique se estes ViewSets estão de fato em pedido.views ---
# Se ItemCardapioViewSet estiver em cardapio.views, você precisará:
# from cardapio import views as cardapio_views
# router.register(r'cardapio', cardapio_views.ItemCardapioViewSet)
# Por simplicidade aqui, vou assumir que estão todos em pedido.views ou que você ajustará.

router = DefaultRouter()
# Registros de ViewSets que NÃO possuem seu próprio urls.py com um router
router.register(r'mesas', pedido_views.MesaViewSet)
router.register(r'cardapio', pedido_views.ItemCardapioViewSet) # Verifique o path real se não for pedido_views
router.register(r'pedidos', pedido_views.PedidoViewSet) # <--- Mudei para 'pedidos' para evitar conflito com path('api/pedido/...')
router.register(r'itenspedido', pedido_views.ItemPedidoViewSet) # Mudei para 'itenspedido'

urlpatterns = [
    path('admin/', admin.site.urls),

    # URLs geradas automaticamente pelo router principal (para os ViewSets registrados acima)
    path('api/', include(router.urls)),

    # INCLUINDO AS URLs DOS SEUS APLICATIVOS (QUE POSSUEM SEUS PRÓPRIOS ROUTERS)
    # ESSENCIAL PARA "chamadas-garcom" e "envios_cozinha"
    path('api/', include('chamada.urls')),  # Inclui as URLs geradas pelo router em 'chamada/urls.py'
    path('api/', include('pedido.urls')),   # Inclui as URLs geradas pelo router em 'pedido/urls.py'
                                            # Este 'pedido.urls' deve conter EnvioCozinhaViewSet

    # Mantenha as outras rotas @api_view que você ainda usa:
    # Verifique se 'criar_novo_pedido', 'adicionar_itens_ao_pedido', 'enviar_para_cozinha'
    # estão no pedido.views. Eles parecem ser funções ou APIViews e não ViewSets.
    path('api/pedido/criar/', pedido_views.criar_novo_pedido, name='criar_novo_pedido'),
    path('api/pedido/adicionar_itens/', pedido_views.adicionar_itens_ao_pedido, name='adicionar_itens_ao_pedido'),
    path('api/pedido/enviar_cozinha/<int:pedido_id>/', pedido_views.enviar_para_cozinha, name='enviar_para_cozinha'),
    # ... outras rotas personalizadas se houver
]

# Nota importante:
# Certifique-se que o path para 'pedidos' no router principal (router.register(r'pedidos', pedido_views.PedidoViewSet))
# não causa conflito com as rotas manuais como path('api/pedido/criar/').
# O Django processa as URLs em ordem. Rotas mais específicas devem vir antes das mais genéricas.
# Mudar 'pedido' para 'pedidos' no router ajuda a evitar conflitos.

# Se 'ItemCardapioViewSet' estiver em 'cardapio.views', a importação e registro seriam assim:
# from cardapio import views as cardapio_views
# router.register(r'cardapio', cardapio_views.ItemCardapioViewSet)