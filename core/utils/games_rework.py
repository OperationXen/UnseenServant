from core.models.auth import CustomUser
from core.models.game import Game
from core.models.players import Player

from discord_bot.logs import logger as log

# ########################################################################## #


def add_user_to_game(user: CustomUser, game: Game, force: bool = False) -> bool:
    """2024 Rework - Attempt to add a user to a game"""
    try:
        current_players = game.players.all()
        if current_players.count() >= game.max_players and not force:  # party is full
            # Add player to end of waitlist
            waitlist = current_players.filter(standby=True).order_by("-waitlist")
            last_waitlist_position = waitlist.last().waitlist or 0
            player = Player.objects.create(game=game, user=user, waitlist=last_waitlist_position + 1, standby=True)
        else:
            # Add player to party
            player = Player.objects.create(game=game, user=user, waitlist=0, standby=False)

        # Discord data currently still stored on player object for transition
        player.discord_id = user.discord_id
        player.discord_name = user.discord_name
        player.save()
        # Remove above lines when no longer required
        return player
    except Exception as e:
        log.error(f"[!] Exception occured when adding user {user.username} to game {game.name}")


def remove_user_from_game(user: CustomUser, game: Game) -> bool:
    """Remove a user from a game completely"""
    try:
        player = game.players.all().get(user=user)
        player.delete()
        return True
    except Player.DoesNotExist:
        return False
    except Exception as e:
        log.error(f"[!] Exception occured when removing user {user.username} from game {game.name}")
        return False
