from api.views.games import GamesViewSet
from rest_framework.routers import DefaultRouter

router = DefaultRouter()
router.register(r'games', GamesViewSet, basename='games')

urlpatterns = router.urls
