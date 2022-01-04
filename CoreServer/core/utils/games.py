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
    try:
        game_obj = Game.objects.get(pk=game_id)
        return game_obj
    except Game.DoesNotExist:
        return None
    

def get_waitlist_position():
    return 4

@sync_to_async
def add_player_to_game(game, user):
    """ Add a new player to an existing game """
    max_players = (game.max_players)
    players = game.players.filter(standby=False)
    waitlist = game.players.filter(standby=True)

    if players.filter(discord_id=user.id):
        return False, 'You are already in this game'
    if waitlist.filter(discord_id=user.id):
        return False, f"You\'re already in the waitlist for this game in position: {waitlist.get(discord_id=user.id).waitlist}"
    
    name = f"{user.name}:{user.discriminator}"
    if players.count() >= max_players:
        print('Game full - adding user to waitlist')
        position = get_waitlist_position()
        player = Player.objects.create(game=game, discord_id = user.id, discord_name = name, character = None, standby=True, waitlist=position)
        return True, f"Added you to the waitlist, you are in position: {player.waitlist}"
    else:
        player = Player.objects.create(game=game, discord_id = user.id, discord_name = name, character = None, standby=False)
        return True, f"Added you to the game, enjoy!"

@sync_to_async
def remove_player_from_game(game, user):
    """ Remove an existing player from a game """
    players = game.players.filter(standby=False)
    waitlist = game.players.filter(standby=True)

    player = waitlist.filter(discord_id=user.id).first()
    if player:
        player.delete()
        return True, f"You have been removed from the waitlist for {game.name}"    

    player = players.filter(discord_id=user.id).first()
    if player:
        player.delete()
        return True, f"You have dropped out of {game.name}"
