# backend/cliente/urls.py

from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import ClienteViewSet

router = DefaultRouter()
router.register(r'', ClienteViewSet) # Registra o ViewSet para a rota 'clientes'

urlpatterns = [
    path('', include(router.urls)),
]