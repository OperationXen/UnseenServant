from rest_framework.response import Response
from rest_framework.status import *
from rest_framework.views import APIView
from rest_framework.permissions import IsAdminUser

from core.utils.statistics import get_gamestats, get_playerstats, get_unsuccessful_player_details

from core.utils.games import get_historic_games
from core.utils.players import _get_historic_users


class GameStatsViewSet(APIView):
    """Game statistics"""

    def get(self, request):
        """Return a game statistics message"""
        days = 31
        if request.user.is_superuser:
            days = int(request.GET.get("days", 31))

        game_data = get_historic_games(days=days)
        game_stats = get_gamestats(game_data)
        general_stats = {"days_of_data": days}
        return Response(general_stats | game_stats)


class PlayerStatsViewSet(APIView):
    """Player statistics"""

    def get(self, request):
        """Return player statistics message"""
        days = 31
        if request.user.is_superuser:
            days = int(request.GET.get("days", 31))

        player_data = _get_historic_users(days=days)
        player_stats = get_playerstats(player_data)
        general_stats = {"days_of_data": days}
        return Response(general_stats | player_stats)


class GeneralStatsViewSet(APIView):
    """All statistics"""

    def get(self, request):
        """Get a summary of server statistics for the last 31 days"""
        days = 31
        if request.user.is_superuser:
            days = int(request.GET.get("days", 31))

        player_data = _get_historic_users(days=days)
        game_data = get_historic_games(days=days)

        general_stats = {"days_of_data": days}
        game_stats = get_gamestats(game_data)
        player_stats = get_playerstats(player_data)
        return Response(general_stats | game_stats | player_stats)


class DetailedStatsViewSet(APIView):
    """Authenticated endpoint for admin users"""

    permission_classes = [
        IsAdminUser,
    ]

    def get(self, request):
        """Produce a more details view for admin users"""
        days = int(request.GET.get("days", 31))
        player_data = _get_historic_users(days=days)
        unsuccessful_players = get_unsuccessful_player_details(player_data)
        return Response({"days_of_data": days, "user_details": unsuccessful_players})
