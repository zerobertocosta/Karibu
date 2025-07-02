# backend/chamada/urls.py

from rest_framework.routers import DefaultRouter
from .views import ChamadaGarcomViewSet

router = DefaultRouter()
# Registra o ViewSet com um prefixo 'chamadas-garcom'.
# Isso criará URLs como /api/chamadas-garcom/ para listar/criar
# e /api/chamadas-garcom/{id}/ para detalhe/atualizar.
router.register(r'chamadas-garcom', ChamadaGarcomViewSet, basename='chamada-garcom')

urlpatterns = router.urls

