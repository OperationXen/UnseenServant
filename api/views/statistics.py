from rest_framework.response import Response
from rest_framework.status import *
from rest_framework.views import APIView

from core.utils.games import _get_historic_games
from core.utils.players import _get_historic_users


def get_gamestats() -> dict:
    """build a game statistics object"""
    historic_games = _get_historic_games(days=31)
    unique_dms = historic_games.values_list("dm__discord_id").distinct().count()

    stats = {"games_in_last_month": historic_games.count(), "unique_dms": unique_dms}
    return stats


def get_playerstats() -> dict:
    """build a player statistic object"""
    historic_users = _get_historic_users()

    user_count = historic_users.values_list("discord_id").distinct().count()
    all_players = historic_users.filter(standby=False)
    all_players_count = len(all_players)
    unique_players = all_players.values_list("discord_id").distinct()
    unique_players_count = len(unique_players)

    average_games_per_player = 0
    if unique_players_count:
        average_games_per_player = all_players_count / unique_players_count

    all_waitlisters = historic_users.filter(standby=True)
    all_waitlisters_count = len(all_waitlisters)

    not_selected = historic_users.exclude(discord_id__in=all_players.values_list("discord_id"))
    not_selected_ids = not_selected.values_list("discord_id").distinct()
    not_selected_count = not_selected_ids.count()

    playerstats = {
        "active_users": user_count,
        "total_players": all_players_count,
        "unique_players": unique_players_count,
        "games_per_player": average_games_per_player,
        "total_unselected_players": not_selected_count,
    }
    return playerstats


class GameStatsViewSet(APIView):
    """Game statistics"""

    def get(self, request):
        """Return a game statistics message"""
        gamestats = get_gamestats()
        return Response(gamestats)


class PlayerStatsViewSet(APIView):
    """Player statistics"""

    def get(self, request):
        """Return player statistics message"""
        playerstats = get_playerstats()
        return Response(playerstats)


class GeneralStatsViewSet(APIView):
    """All statistics"""

    def get(self, response):
        gamestats = get_gamestats()
        playerstats = get_playerstats()
        return Response(gamestats | playerstats)
