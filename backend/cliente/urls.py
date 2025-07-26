# backend/cliente/urls.py
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import ClienteViewSet

# Cria um router para registrar ViewSets.
router = DefaultRouter()
# ALTERADO: O prefixo agora é uma string vazia '', e definimos 'basename'
# para que o DRF possa gerar nomes de URLs corretamente.
router.register(r'', ClienteViewSet, basename='clientes') 

urlpatterns = [
    # Inclui todas as URLs geradas pelo router (ex: /)
    path('', include(router.urls)),
]