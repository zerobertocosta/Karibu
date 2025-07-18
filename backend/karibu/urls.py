# backend/karibu/urls.py (seu arquivo de urls principal do projeto)

from django.contrib import admin
from django.urls import path, include
from rest_framework_simplejwt.views import (
    TokenRefreshView,
)

# Importe sua view customizada de login
from usuarios.views import MyTokenObtainPairView # Importar a nova view customizada

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/token/', MyTokenObtainPairView.as_view(), name='token_obtain_pair'), # <-- APONTE PARA SUA NOVA VIEW AQUI
    path('api/token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('api/usuarios/', include('usuarios.urls')),
    path('api/configuracao/', include('configuracao.urls')),
    # ... outras urls
]