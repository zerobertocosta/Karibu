# backend/mesa/urls.py

from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import MesaViewSet

router = DefaultRouter()
router.register(r'', MesaViewSet) # Registra o MesaViewSet na raiz de 'api/mesa/'

urlpatterns = [
    path('', include(router.urls)),
]