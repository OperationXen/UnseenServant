from typing import Tuple
from datetime import datetime

from rest_framework.response import Response
from rest_framework.request import Request
from rest_framework.status import *
from rest_framework.views import APIView
from rest_framework.permissions import IsAdminUser

from core.utils.statistics import get_game_stats, get_player_stats, get_unsuccessful_player_details
from core.utils.statistics import get_waitlist_stats

from core.utils.games import get_historic_games
from core.utils.players import get_historic_users


class StatsView(APIView):
    def get_admin_params(self, request: Request) -> Tuple[int, datetime]:
        """Get the parameters for a request"""
        if request.user.is_superuser:
            days = int(request.GET.get("days", 31))
            try:
                start_date = datetime.strptime(request.GET.get("start_date"), "%Y-%m-%d")
            except Exception:
                pass
            return (days, start_date)
        return (31, None)


class GameStatsViewSet(StatsView):
    """Game statistics"""

    def get(self, request):
        """Return a game statistics message"""
        (days, start_date) = self.get_admin_params(request)

        game_data = get_historic_games(days, start_date)
        game_stats = get_game_stats(game_data)
        general_stats = {"days_of_data": days}
        if start_date:
            general_stats["start_date"] = start_date
        return Response(general_stats | game_stats)


class PlayerStatsViewSet(StatsView):
    """Player statistics"""

    def get(self, request):
        """Return player statistics message"""
        (days, start_date) = self.get_admin_params(request)

        player_data = get_historic_users(days, start_date)
        player_stats = get_player_stats(player_data)
        waitlist_stats = get_waitlist_stats(player_data)
        general_stats = {"days_of_data": days}
        if start_date:
            general_stats["start_date"] = start_date
        return Response(general_stats | player_stats | waitlist_stats)


class GeneralStatsViewSet(StatsView):
    """All statistics"""

    def get(self, request):
        """Get a summary of server statistics for the last 31 days"""
        (days, start_date) = self.get_admin_params(request)

        player_data = get_historic_users(days, start_date)
        game_data = get_historic_games(days, start_date)

        general_stats = {"days_of_data": days}
        if start_date:
            general_stats["start_date"] = start_date
        game_stats = get_game_stats(game_data)
        player_stats = get_player_stats(player_data)
        waitlist_stats = get_waitlist_stats(player_data)
        return Response(general_stats | game_stats | player_stats | waitlist_stats)


class DetailedStatsViewSet(APIView):
    """Authenticated endpoint for admin users"""

    permission_classes = [
        IsAdminUser,
    ]

    def get(self, request):
        """Produce a more details view for admin users"""
        days = int(request.GET.get("days", 31))
        player_data = get_historic_users(days=days)
        unsuccessful_players = get_unsuccessful_player_details(player_data)
        return Response({"days_of_data": days, "user_details": unsuccessful_players})
