from django.urls import path, include, re_path
from rest_framework.routers import DefaultRouter

from api.views.games import GamesViewSet
from api.views.status import StatusViewSet
from api.views.statistics import GameStatsViewSet

router = DefaultRouter()
router.register(r"games", GamesViewSet, basename="games")

urlpatterns = [
    path(r"", include(router.urls)),
    re_path("status/?", StatusViewSet.as_view(), name="status"),
    re_path("statistics/games?", GameStatsViewSet.as_view(), name="stats-games"),
]
