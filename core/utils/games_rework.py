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
            if waitlist.last():
                last_waitlist_position = waitlist.last().waitlist or 0
            else:
                last_waitlist_position = 0
            player = Player.objects.create(game=game, user=user, waitlist=last_waitlist_position + 1, standby=True)
        else:
            try:
                # check to see if player is in the waitlist, and being force-added by the DM
                player = Player.objects.get(game=game, user=user)
                player.waitlist = False
            except Player.DoesNotExist:
                # User not already in waitlist, add a new player object to party
                player = Player.objects.create(game=game, user=user, waitlist=0, standby=False)

        # Discord data currently still stored on player object for transition
        player.discord_id = user.discord_id
        player.discord_name = user.discord_name or "Masked stranger"
        player.save()
        # Remove above lines when no longer required
        return player
    except Exception as e:
        log.error(f"[!] Exception occured when adding user {user.username} to game {game.name}")


def remove_user_from_game(user: CustomUser, game: Game) -> bool:
    """Remove a user from a game completely"""
    try:
        player_objects = game.players.all().filter(user=user)
        for player in player_objects:
            player.delete()
        return True
    except Player.DoesNotExist:
        # Replace this when all players have an associated user object
        # return False
        return remove_player_by_discord_id(game, user.discord_id)
    except Exception as e:
        log.error(f"[!] Exception occured when removing user {user.username} from game {game.name}")
        return False


# ########################################################################## #
def remove_player_by_discord_id(game: Game, discord_id: str) -> bool:
    """Syncronous worker to remove the player from the game"""
    try:
        player = game.players.all().filter(discord_id=discord_id).first()
        if player:
            player.delete()
            return True
    except Exception as e:
        log.error(f"[!] Exception occured removing player with discord ID {discord_id}: {str(e)}")
    return False
