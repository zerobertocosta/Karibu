# backend/cardapio/urls.py
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import CategoriaViewSet, ItemCardapioViewSet

router = DefaultRouter()
router.register(r'categorias', CategoriaViewSet, basename='categoria')
router.register(r'itens', ItemCardapioViewSet, basename='itemcardapio') # <--- MUDANÇA AQUI!

urlpatterns = router.urls # Use diretamente router.urls