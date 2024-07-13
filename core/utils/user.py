from asgiref.sync import sync_to_async

from core.utils.players import get_bonus_credits, get_user_pending_games_count
from core.utils.ranks import get_highest_rank
from core.models.auth import CustomUser
from core.models.players import Player
from core.models.game import Game


def get_user_max_credit(user: CustomUser) -> int:
    """Get the maximum credit balance for a given user"""
    max_games = 0
    try:
        ranks = list(user.ranks.all())
        rank = get_highest_rank(ranks)
    except Exception as e:
        print(e)
    if rank:
        max_games = rank.max_games
    bonuses = get_bonus_credits(user.discord_id)
    return max_games + bonuses


def get_user_available_credit(user: CustomUser) -> int:
    """Attempt to get the available credits for a logged in user"""
    total_credits = get_user_max_credit(user)
    used_credits = get_user_pending_games_count(user.discord_id)
    return total_credits - used_credits


# ###################################################################### #
def get_user_by_discord_id(discord_id: str) -> CustomUser:
    try:
        user = CustomUser.objects.get(discord_id=discord_id)
        if user:  # force evaluation before leaving syncronous context
            return user
    except CustomUser.DoesNotExist:
        pass
    return None


@sync_to_async
def async_get_user_by_discord_id(discord_id: str) -> CustomUser:
    """Async wrapper for getting a discord user"""
    return get_user_by_discord_id(discord_id)


# ###################################################################### #
def user_in_game(user: CustomUser, game: Game) -> bool:
    """Checks if a user is in a given game or not"""
    queryset = Player.objects.filter(game=game)
    queryset = queryset.filter(discord_id=user.discord_id)
    matches = queryset.count()
    if matches > 0:
        return True
    return False


def user_is_player_in_game(user: CustomUser, game: Game) -> bool:
    """Checks if a user is playing in a given game or not"""
    queryset = Player.objects.filter(game=game)
    queryset = queryset.filter(standby=False)
    queryset = queryset.filter(discord_id=user.discord_id)
    if queryset.exists():
        return True
    return False


def user_is_waitlisted_in_game(user: CustomUser, game: Game) -> bool:
    """Checks if a user is waitlisted in a given game or not"""
    queryset = Player.objects.filter(game=game)
    queryset = queryset.filter(standby=True)
    queryset = queryset.filter(discord_id=user.discord_id)
    if queryset.exists():
        return True
    return False
