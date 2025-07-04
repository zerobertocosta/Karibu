# backend/pedido/urls.py
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import PedidoViewSet # Importe seu ViewSet aqui

router = DefaultRouter()
router.register(r'', PedidoViewSet, basename='pedido') # Registra o PedidoViewSet na raiz de 'api/pedidos/'

urlpatterns = router.urls # Apenas as URLs do router aqui