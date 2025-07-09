# backend/karibu/urls.py

from django.contrib import admin
from django.urls import path, include
from rest_framework_simplejwt.views import (
    TokenObtainPairView,
    TokenRefreshView,
)

urlpatterns = [
    path('admin/', admin.site.urls),
    # URLs para autenticação JWT
    path('api/token/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('api/token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    # URLs da API dos seus apps
    path('api/configuracao/', include('configuracao.urls')),
    path('api/usuarios/', include('usuarios.urls')),
    path('api/cardapio/', include('cardapio.urls')), # <-- Adicione esta linha
    # Outras URLs da API virão aqui conforme você desenvolver outros apps
]