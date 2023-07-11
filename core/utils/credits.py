from django.db.models import QuerySet
from django.utils import timezone
from asgiref.sync import sync_to_async

from discord_bot.logs import logger as log
from core.exceptions import GameCreditException
from core.models import Credit, CustomUser, Game


# ########################################################################## #
def get_user_credit_available(user: CustomUser) -> QuerySet:
    """Get the available, spendable credits for a user"""
    queryset = user.credits.filter(datetime_spent=None).filter(locked=False)
    return queryset


@sync_to_async
def async_get_user_credit_available(user: CustomUser) -> list[Credit]:
    """async wrapper that gets a user's available credits"""
    queryset = get_user_credit_available(user)
    # Forcing to list collapses the lazy queryset down to a solved query
    return list(queryset)


# ########################################################################## #
def get_user_credit(user: CustomUser) -> QuerySet:
    """Get all of a user's current credit balance, including anything currently being used to hold a slot"""
    now = timezone.now()
    queryset = user.credits.exclude(datetime_expiry__lte=now)
    return queryset


@sync_to_async
def async_get_user_credit(user: CustomUser) -> list[Credit]:
    """async wrapper to get a user's current credit balance"""
    queryset = get_user_credit(user)
    # Forcing to list collapses the lazy queryset down to a solved query before we leave syncronous context
    return list(queryset)


# ########################################################################## #
def get_user_credit_locked(user: CustomUser) -> QuerySet:
    """Retrieve all currently valid, but locked credits"""
    queryset = get_user_credit(user)
    queryset = queryset.filter(locked=True)
    return queryset


@sync_to_async
def get_user_credit_locked(user: CustomUser) -> QuerySet:
    """Asyncronous wrapper to retrieve all currently used credits"""
    queryset = get_user_credit_locked(user)
    # Forcing to list collapses the lazy queryset down to a solved query before we leave syncronous context
    return list(queryset)


# ########################################################################## #
def spend_user_credit_on_game(user: CustomUser, game: Game, cost: int = 1, lock: bool = False) -> Credit:
    """spend a user's available credit on a game"""
    try:
        now = timezone.now()
        credits = get_user_credit_available(user)
        credits.order_by("datetime_expiry")

        selected_credits = credits[:cost]
        if len(selected_credits) != cost:
            raise GameCreditException("Insufficient credit")

        for credit in selected_credits:
            credit.update(game=game, datetime_spent=now, locked=lock)
            credit.save()

    except Exception as e:
        log.debug(f"Exception occured in spend_user_credit_on_game - user: {user}, game: {game}")
