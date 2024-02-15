from asgiref.sync import sync_to_async

from django.db.models import QuerySet
from django.utils import timezone

from core.utils.players import get_bonus_credits
from core.utils.ranks import get_user_highest_rank, get_highest_rank
from core.models.auth import CustomUser
from core.models.players import Player
from core.models.game import Game


def get_user_by_discord_id(discord_id: str) -> CustomUser:
    try:
        return CustomUser.objects.get(discord_id=discord_id)
    except CustomUser.DoesNotExist:
        return None


def user_in_game(user: CustomUser, game: Game, standby: bool | None = None) -> bool:
    """Checks if a user is in a given game or not"""
    queryset = Player.objects.filter(game=game)
    # if standby parameter not set, get all players
    if standby is not None:
        queryset = queryset.filter(standby=standby)
    queryset = queryset.filter(user=user)
    if queryset.exists():
        return True
    return False


# ################################################################### #
def get_user_credits_max(user: CustomUser) -> int:
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


def get_user_games(user: CustomUser, all: bool = False) -> QuerySet:
    """Get upcoming games for a user, optionally fetch past games too"""
    queryset = Player.objects.filter(user=user)
    if not all:
        now = timezone.now()
        queryset = queryset.filter(game__datetime__gte=now)
    return queryset


def get_user_credit_balance(user) -> int:
    """Get the total number of signup credits the user has availble to them"""
    max_games = get_user_credits_max(user)
    game_count = get_user_games(user).count()
    return max_games - game_count


@sync_to_async
def async_get_user_credit_balance(user) -> int:
    """Async wrapper to get signups remaining from async context"""
    return get_user_credit_balance(user)


# ############################################################# #


@sync_to_async
def async_user_credit_text(user: CustomUser) -> str:
    """Get a text string explaining to the user how many game credits they have"""
    credits = get_user_credit_balance(user)
    max_games = get_user_credits_max(user)
    if credits:
        return f"{credits} / {max_games} game credits available"
    else:
        return f"You have no game credits available from your [{max_games}] total"
