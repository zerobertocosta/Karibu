# backend/karibu/urls.py
from django.contrib import admin
from django.urls import path, include
from rest_framework_simplejwt.views import (
    TokenObtainPairView,
    TokenRefreshView,
    TokenVerifyView,
)

urlpatterns = [
    path('admin/', admin.site.urls),
    # URLs para autenticação e obtenção/renovação de tokens JWT
    path('api/token/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('api/token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('api/token/verify/', TokenVerifyView.as_view(), name='token_verify'),
    
    # URLs do Django REST Framework para a API browsable
    path('api-auth/', include('rest_framework.urls')),
    
    # Inclusão das URLs dos seus apps
    path('api/usuarios/', include('usuarios.urls')),
    path('api/configuracao/', include('configuracao.urls')),
    path('api/mesa/', include('mesa.urls')),
    path('api/cardapio/', include('cardapio.urls')),
    
    # !!! LINHA ADICIONADA PARA INCLUIR AS URLs DO APP CLIENTE !!!
    path('api/clientes/', include('cliente.urls')), 
]

# Configuração para servir arquivos de mídia (fotos) durante o desenvolvimento
from django.conf import settings
from django.conf.urls.static import static

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)