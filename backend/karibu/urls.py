# backend/karibu/urls.py

from django.contrib import admin
from django.urls import path, include
from rest_framework_simplejwt.views import (
    TokenObtainPairView,
    TokenRefreshView,
)

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/token/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('api/token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),

    # Incluir as URLs dos seus aplicativos
    path('api/configuracao/', include('configuracao.urls')),
    path('api/usuarios/', include('usuarios.urls')),
    path('api/cardapio/', include('cardapio.urls')),
    path('api/clientes/', include('cliente.urls')), # <-- Adicione esta linha
    path('api/mesas/', include('mesa.urls')),
]