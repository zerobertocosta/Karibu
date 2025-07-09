# backend/cardapio/urls.py

from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import CategoriaViewSet, ItemCardapioViewSet # Importar o novo ViewSet

router = DefaultRouter()
router.register(r'categorias', CategoriaViewSet)
router.register(r'itens', ItemCardapioViewSet) # Registrar o ItemCardapioViewSet

urlpatterns = [
    path('', include(router.urls)),
]