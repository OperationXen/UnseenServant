from django.urls import path, include, re_path
from rest_framework.routers import DefaultRouter

from api.views.games import GamesViewSet
from api.views.status import StatusViewSet
from api.views.statistics import GameStatsViewSet, PlayerStatsViewSet, GeneralStatsViewSet, DetailedStatsViewSet

router = DefaultRouter()
router.register(r"games", GamesViewSet, basename="games")

urlpatterns = [
    path(r"", include(router.urls)),
    path('game_variants/', GamesViewSet.as_view(({"get":"game_variants"})), name="game-variants"),
    path('game_realms/', GamesViewSet.as_view(({"get":"game_realms"})), name="game-realms"),
    re_path("status/?", StatusViewSet.as_view(), name="status"),
    re_path("statistics/games/?", GameStatsViewSet.as_view(), name="stats-games"),
    re_path("statistics/players/?", PlayerStatsViewSet.as_view(), name="stats-players"),
    re_path("statistics/detailed/?", DetailedStatsViewSet.as_view(), name="stats-detailed"),
    re_path("statistics/?", GeneralStatsViewSet.as_view(), name="stats"),
]
