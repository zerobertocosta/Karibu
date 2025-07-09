# backend/usuarios/urls.py

from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import UserViewSet, PerfilViewSet

router = DefaultRouter()
router.register(r'users', UserViewSet)
router.register(r'perfis', PerfilViewSet) # Endpoint para perfis

urlpatterns = [
    path('', include(router.urls)),
]