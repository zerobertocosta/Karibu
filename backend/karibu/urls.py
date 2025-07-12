# backend/karibu/urls.py
from django.contrib import admin
from django.urls import path, include
from rest_framework_simplejwt.views import (
    TokenObtainPairView,
    TokenRefreshView,
)

# IMPORTE ESTES DOIS MÓDULOS NOVOS
from django.conf import settings 
from django.conf.urls.static import static 

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/token/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('api/token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    # Incluir as URLs dos seus aplicativos
    path('api/configuracao/', include('configuracao.urls')),
    path('api/usuarios/', include('usuarios.urls')),
    path('api/cardapio/', include('cardapio.urls')),
    path('api/clientes/', include('cliente.urls')),
    path('api/mesas/', include('mesa.urls')),
]

# >>> ADICIONE ESTAS LINHAS AQUI PARA SERVIR ARQUIVOS DE MÍDIA EM DESENVOLVIMENTO <<<
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
# >>> FIM DA ADIÇÃO <<<