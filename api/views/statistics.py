from rest_framework.response import Response
from rest_framework.status import *
from rest_framework.views import APIView

from core.utils.games import _get_historic_games


class GameStatsViewSet(APIView):
    """Game statistics"""

    def get(self, request):
        """Build a game statistics message"""
        historic_games = _get_historic_games(days=31)
        return Response({"games_in_last_month": historic_games.count()})
