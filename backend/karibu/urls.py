# backend/karibu/urls.py (seu arquivo de urls principal do projeto)

from django.contrib import admin
from django.urls import path, include
from rest_framework_simplejwt.views import (
    TokenRefreshView,
)

# Importe sua view customizada de login
from usuarios.views import MyTokenObtainPairView # Importar a nova view customizada

# >>> ADICIONE ESTAS DUAS LINHAS <<<
from django.conf import settings
from django.conf.urls.static import static
# >>> FIM DA ADIÇÃO <<<

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/token/', MyTokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('api/token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    
    path('api/usuarios/', include('usuarios.urls')),
    path('api/configuracao/', include('configuracao.urls')),
    path('api/cardapio/', include('cardapio.urls')),
    path('api/mesas/', include('mesa.urls')),
    # Se você tiver outros apps (cliente, pedido, chamada, etc.) que o frontend acessa, inclua-os também:
    # path('api/cliente/', include('cliente.urls')),
    # path('api/pedido/', include('pedido.urls')),
    # path('api/chamada/', include('chamada.urls')),
]

# >>> ESTE BLOCO É ESSENCIAL PARA SERVIR ARQUIVOS DE MÍDIA EM DESENVOLVIMENTO <<<
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
# >>> FIM DO BLOCO ESSENCIAL <<<