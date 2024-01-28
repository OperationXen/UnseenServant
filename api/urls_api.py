from django.urls import path, include, re_path
from rest_framework.routers import DefaultRouter

from api.views.games import GamesViewSet
from api.views.dm_profile import DMProfileViewset
from api.views.options import GameRealmOptionsViewset, GameVariantOptionsViewset
from api.views.status import StatusViewSet
from api.views.statistics import GameStatsViewSet, PlayerStatsViewSet, GeneralStatsViewSet, DetailedStatsViewSet

view_actions = {"get": "details", "post": "create", "patch": "partial_update", "delete": "delete"}

router = DefaultRouter()
router.register(r"games", GamesViewSet, basename="games")
router.register(r"game/variants", GameVariantOptionsViewset, basename="game-variants")
router.register(r"game/realms", GameRealmOptionsViewset, basename="game-realms")

urlpatterns = [
    path(r"", include(router.urls)),
    re_path("dungeonmasters/(?P<pk>\w+)/?", DMProfileViewset.as_view(view_actions), name="dms-detail"),
    re_path("dungeonmasters/?$", DMProfileViewset.as_view({"get": "list", "post": "create"}), name="dms-list"),
    re_path("status/?", StatusViewSet.as_view(), name="status"),
    re_path("statistics/games/?", GameStatsViewSet.as_view(), name="stats-games"),
    re_path("statistics/players/?", PlayerStatsViewSet.as_view(), name="stats-players"),
    re_path("statistics/detailed/?", DetailedStatsViewSet.as_view(), name="stats-detailed"),
    re_path("statistics/?", GeneralStatsViewSet.as_view(), name="stats"),
]
