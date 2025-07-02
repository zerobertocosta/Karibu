# backend/cardapio/urls.py

from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import CategoriaViewSet, ItemCardapioViewSet

router = DefaultRouter()
router.register(r'categorias', CategoriaViewSet)
router.register(r'itens', ItemCardapioViewSet)

urlpatterns = [
    path('', include(router.urls)),
]