# backend/mesa/urls.py

from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import MesaViewSet

router = DefaultRouter()
# Altere r'clientes' para r'' (string vazia) para ter URLs limpas
router.register(r'', MesaViewSet, basename='mesas') # Registra o ViewSet para a rota 'mesas'

urlpatterns = [
    path('', include(router.urls)),
]