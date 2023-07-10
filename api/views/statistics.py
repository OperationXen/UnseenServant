from rest_framework.response import Response
from rest_framework.status import *
from rest_framework.views import APIView
from rest_framework.permissions import IsAdminUser

from core.utils.statistics import get_gamestats, get_playerstats, get_unsuccessful_player_details

from core.utils.games import _get_historic_games
from core.utils.players import _get_historic_users


class GameStatsViewSet(APIView):
    """Game statistics"""

    def get(self, request):
        """Return a game statistics message"""
        data = _get_historic_games(days=31)
        gamestats = get_gamestats(data)
        return Response(gamestats)


class PlayerStatsViewSet(APIView):
    """Player statistics"""

    def get(self, request):
        """Return player statistics message"""
        data = _get_historic_users(days=31)
        playerstats = get_playerstats(data)
        return Response(playerstats)


class GeneralStatsViewSet(APIView):
    """All statistics"""

    def get(self, request):
        """Get a summary of server statistics for the last 31 days"""
        game_data = _get_historic_games(days=31)
        player_data = _get_historic_users(days=31)

        gamestats = get_gamestats(game_data)
        playerstats = get_playerstats(player_data)
        return Response(gamestats | playerstats)


class DetailedStatsViewSet(APIView):
    """Authenticated endpoint for admin users"""

    permission_classes = [
        IsAdminUser,
    ]

    def get(self, request):
        """Produce a more details view for admin users"""
        days = request.GET.get("days", 31)
        player_data = _get_historic_users(days=days)
        unsuccessful_players = get_unsuccessful_player_details(player_data)
        return Response(unsuccessful_players)
