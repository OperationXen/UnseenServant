from rest_framework.response import Response
from rest_framework.status import *
from rest_framework.views import APIView

from core.utils.games import _get_historic_games
from core.utils.players import _get_historic_players


def get_gamestats() -> dict:
    """build a game statistics object"""
    historic_games = _get_historic_games(days=31)
    stats = {"games_in_last_month": historic_games.count()}
    return stats


def get_playerstats() -> dict:
    """build a player statistic object"""
    historic_players = _get_historic_players()

    player_count = historic_players.count()
    unique_players = historic_players.values_list("discord_id").distinct()
    unique_players_count = unique_players.count()

    average_games_per_player = 0
    if unique_players_count:
        average_games_per_player = player_count / unique_players_count

    playerstats = {
        "all_players": player_count,
        "unique_players": unique_players_count,
        "games_per_player": average_games_per_player,
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
