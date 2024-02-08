from core.models.auth import CustomUser
from core.models.game import Game
from core.models.players import Player


# ########################################################################## #


def add_user_to_game(user: CustomUser, game: Game) -> bool:
    """2024 Rework - Attempt to add a user to a game"""
    current_players = game.players.all().order_by("waitlist")
    if current_players.count() >= game.max_players:  # party is full
        # Add player to end of waitlist
        last_waitlist_position = current_players[-1].waitlist
        player = Player.objects.create(game=game, waitlist=last_waitlist_position + 1, standby=True)
    else:
        # Add player to party
        player = Player.objects.create(game=game, waitlist=0, standby=False)
    return player
