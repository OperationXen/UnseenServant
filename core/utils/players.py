from datetime import timedelta, datetime

from asgiref.sync import sync_to_async
from django.db.models import Q, Sum, QuerySet
from django.utils import timezone

from core.models.players import BonusCredit, Player
from discord_bot.logs import logger as log
from core.utils.ranks import get_user_highest_rank


@sync_to_async
def async_issue_player_bonus_credit(user, number, issuer, reason="Not supplied", valid_for=None):
    """Give a player some bonus credits"""
    if valid_for:
        now = timezone.now()
        end_date = now + timedelta(days=valid_for)
    else:
        end_date = None
    obj = BonusCredit.objects.create(
        discord_id=str(user.id),
        discord_name=f"{user.name}#{user.discriminator}",
        issuer_id=str(issuer.id),
        issuer_name=f"{issuer.name}#{issuer.discriminator}",
        credits=number,
        reason=reason,
        expires=end_date,
    )
    return obj


def get_player_game_count(discord_id: str):
    """get the total number of games a player is in"""
    now = timezone.now()
    queryset = Player.objects.filter(discord_id=discord_id)
    queryset = queryset.filter(game__datetime__gte=now)
    queryset = queryset.filter(game__ready=True)
    return queryset.count()


def get_bonus_credits(discord_id: str) -> int:
    """Get the total number of bonus games awarded to the user and currently valid"""
    now = timezone.now()
    queryset = BonusCredit.objects.filter(discord_id=discord_id)
    not_expired = Q(expires__gte=now) | Q(expires=None)
    queryset = queryset.filter(not_expired)
    total = queryset.aggregate(Sum("credits"))
    return total["credits__sum"] or 0


def get_player_max_games(discord_user) -> int:
    """get the total number of games a user can sign up for"""
    max_games = 0
    rank = get_user_highest_rank(discord_user.roles)
    if rank:
        max_games = max_games + rank.max_games
    bonuses = get_bonus_credits(str(discord_user.id))
    return max_games + bonuses


def get_user_pending_games_count(discord_id: str) -> int:
    now = timezone.now()

    queryset = Player.objects.filter(discord_id=discord_id)
    queryset = queryset.filter(game__datetime__gte=now)
    pending_games = queryset.count()
    return pending_games


def get_user_signups_remaining(user) -> int:
    """Get the total number of signups the user has availble to them"""
    max_games = get_player_max_games(user)
    game_count = get_user_pending_games_count(str(user.id))

    log.debug(f"{user.display_name} is signed up for {game_count}")
    return max_games - game_count


@sync_to_async
def async_get_user_signups_remaining(user) -> int:
    """Async wrapper to get signups remaining from async context"""
    return get_user_signups_remaining(user)


@sync_to_async
def async_get_player_credit_text(user):
    """Get a text string explaining to the user how many game credits they have"""
    credits = get_user_signups_remaining(user)
    max_games = get_player_max_games(user)
    if credits:
        return f"{credits} / {max_games} game credits available"
    else:
        return f"You have no game credits available from your [{max_games}] total"


@sync_to_async
def async_populate_game_from_waitlist(game):
    """fill a game up using the waitlist, return a list of the promoted players"""
    promoted = []
    players = Player.objects.filter(game=game).filter(standby=False)

    while len(players) < game.max_players:
        next = Player.objects.filter(game=game).filter(standby=True).order_by("waitlist").first()
        if next:
            next.standby = False
            next.save()
            promoted.append(next)
            players = Player.objects.filter(game=game).filter(standby=False)
        else:
            log.info("Not enough waitlisted players to fill game")
            break
    return promoted


def get_waitlist_rank(player):
    """get the rank of the player in the waitlist"""
    queryset = Player.objects.filter(game=player.game).filter(standby=True)
    waitlist = list(queryset.order_by("waitlist"))
    return waitlist.index(player) + 1


def get_last_waitlist_position(game):
    """get the position at the end of the waitlist"""
    queryset = Player.objects.filter(game=game).filter(standby=True)
    last_player = queryset.order_by("waitlist").last()
    if last_player and last_player.waitlist:
        return last_player.waitlist
    return 0


# ########################################################################## #
def get_historic_users(days: int = 31, start_date: datetime | None = None) -> QuerySet:
    """Get all players who have played in the last X days"""
    if start_date:
        start = start_date
        end = start + timedelta(days=days)
    else:
        now = timezone.now()
        start = now - timedelta(days=days)
        end = now

    queryset = Player.objects.filter(game__datetime__gte=start).filter(game__datetime__lte=end)
    queryset = queryset.order_by("discord_id")
    return queryset


@sync_to_async
def async_get_historic_users(days: int = 31) -> list[Player]:
    """Async wrapper for getting historic players"""
    queryset = get_historic_users(days=days)
    # Force the queryset to be evaluated before leaving the syncronous context
    return list(queryset)
