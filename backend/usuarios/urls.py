# backend/karibu/usuarios/urls.py

from django.urls import path, include
from rest_framework.routers import DefaultRouter
# REMOVA FuncaoViewSet daqui, se estiver!
from .views import UsuarioViewSet, PerfilViewSet, EstabelecimentoViewSet 

router = DefaultRouter()
router.register(r'users', UsuarioViewSet, basename='user')
router.register(r'estabelecimentos', EstabelecimentoViewSet)
# REMOVA A LINHA ABAIXO, SE ELA EXISTIR:
# router.register(r'funcoes', FuncaoViewSet) 

urlpatterns = [
    path('', include(router.urls)),
]