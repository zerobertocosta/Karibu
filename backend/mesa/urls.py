# backend/mesa/urls.py
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import MesaViewSet

router = DefaultRouter()
router.register(r'', MesaViewSet, basename='mesa') # Adicione basename para evitar warnings futuros
# O 'r''' vazio significa que as URLs serão na raiz do que for incluído (e será 'api/mesas/')

urlpatterns = router.urls # Use diretamente router.urls, não include(router.urls) aqui