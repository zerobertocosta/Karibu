from rest_framework.routers import DefaultRouter
from .views import EstabelecimentoViewSet

router = DefaultRouter()
router.register(r'estabelecimentos', EstabelecimentoViewSet)

urlpatterns = router.urls