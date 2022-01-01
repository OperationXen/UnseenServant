from datetime import datetime
from asgiref.sync import sync_to_async

from core.models.game import Game, Player


@sync_to_async
def get_dm(game):
    """ Get an object representing the games DM """
    if game.dm:
        return game.dm
    return None

@sync_to_async
def get_player_list(game):
    """ get a list of players subscribed to a game """
    return list(game.players.all())

@sync_to_async
def get_upcoming_games(days=30):
    now = datetime.now()
    queryset = Game.objects.filter(datetime__gte=now)
    # force evaluation before leaving this async context
    return list(queryset)

@sync_to_async
def get_specific_game(game_id):
    game_obj = Game.objects.get(pk=game_id)
    if game_obj:
        return game_obj
    return None
    