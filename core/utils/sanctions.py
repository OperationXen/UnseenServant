from datetime import timedelta

from asgiref.sync import sync_to_async
from django.db.models import Q
from django.utils import timezone

from core.models.players import Ban, Strike, Player


def get_current_user_strikes(discord_id: str):
    """get the total number of outstanding strikes for a given user"""
    now = timezone.now()
    queryset = Strike.objects.filter(discord_id=discord_id)
    queryset = queryset.filter(expires__gte=now).filter(datetime__lte=now)
    # force evaluation before leaving this syncronous context
    return queryset.order_by("expires")


def clear_user_strikes(user):
    """Given a user, expire all of their outstanding strikes"""
    now = timezone.now()
    for strike in get_current_user_strikes(str(user.id)):
        strike.expires = now
        strike.save()


def check_strike_threshold(user, admin):
    """Checks a given user's strikes and issues bans as needed"""
    now = timezone.now()
    end = now + timedelta(weeks=12)
    outstanding = get_current_user_strikes(str(user.id))
    if len(outstanding) >= 3:
        Ban.objects.create(
            discord_id=str(user.id),
            discord_name=f"{user.name}",
            issuer_id=admin.id,
            issuer_name=f"{admin.name}",
            reason="Three strikes and you're out...",
            variant="ST",
            datetime_end=end,
        )
        clear_user_strikes(user)
        return True
    return False


def add_user_strike(user, reason, admin):
    """Create a new user strike object"""
    now = timezone.now()
    end = now + timedelta(weeks=52)
    Strike.objects.create(
        discord_id=str(user.id),
        discord_name=f"{user.name}",
        issuer_id=admin.id,
        issuer_name=f"{admin.name}",
        reason=reason,
        expires=end,
    )


@sync_to_async
def issue_player_strike(user, reason, admin):
    """Issue a strike to the player"""
    add_user_strike(user, reason, admin)
    return check_strike_threshold(user, admin)


@sync_to_async
def get_outstanding_strikes(user):
    """Get outstanding strikes for the user"""
    strikes = get_current_user_strikes(str(user.id))
    # force to list to evaluate before leaving async context
    return list(strikes)


def get_current_user_bans(discord_id: str):
    """Check a given discord user is in good standing - Needs to be syncronous"""
    now = timezone.now()
    not_expired = Q(datetime_end__gte=now) | Q(datetime_end=None)

    queryset = Ban.objects.filter(discord_id=discord_id).filter(datetime_start__lte=now)
    queryset = queryset.filter(not_expired)
    return queryset.order_by("datetime_end")


def check_discord_user_good_standing(discord_id: str) -> bool:
    """Checks if a given user is in good standing"""
    bans = get_current_user_bans(discord_id)
    if bans.count():
        return False
    return True


def get_all_current_bans():
    """Retrieve all currently outstanding bans"""
    now = timezone.now()
    not_expired = Q(datetime_end__gte=now) | Q(datetime_end=None)

    queryset = Ban.objects.filter(datetime_start__lte=now)
    queryset = queryset.filter(not_expired)
    return queryset.order_by("datetime_end")


def add_new_ban(user, variant, reason, admin, ban_length):
    """Add a new ban"""
    now = timezone.now()
    if ban_length == -1 or variant == "PM":
        variant = "PM"
        end = None
    else:
        end = now + timedelta(days=ban_length)
    # Remove player from games on hard ban
    if variant == "HD" or variant == "PM":
        queryset = Player.objects.filter(discord_id=str(user.id)).filter(game__datetime__gte=now)
        queryset.delete()

    Ban.objects.create(
        discord_id=str(user.id),
        discord_name=f"{user.name}",
        issuer_id=str(admin.id),
        issuer_name=f"{admin.name}",
        reason=reason,
        variant=variant,
        datetime_end=end,
    )


@sync_to_async
def get_outstanding_bans(user=None):
    if user:
        bans = get_current_user_bans(str(user.id))
    else:
        bans = get_all_current_bans()
    # force queryset evaluation before returning to async
    return list(bans)


@sync_to_async
def issue_player_ban(user, variant, reason, admin, ban_length):
    """Ban a player from using the signup bot"""
    add_new_ban(user, variant, reason, admin, ban_length)
