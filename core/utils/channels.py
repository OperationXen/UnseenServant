from datetime import timedelta
from django.utils import timezone
from asgiref.sync import sync_to_async
from typing import List

from config.settings import CHANNEL_CREATION_DAYS, CHANNEL_REMIND_HOURS, CHANNEL_WARN_MINUTES, CHANNEL_DESTROY_HOURS
from core.models import GameChannel, ChannelMember, Player, Game
from core.models.auth import CustomUser


def get_games_pending(hours=0, days=0, minutes=0):
    """Get games due to start within the specified timeframe"""
    now = timezone.now()
    end_time = now + timedelta(hours=hours, days=days, minutes=minutes)

    queryset = Game.objects.filter(ready=True)
    queryset = queryset.filter(datetime__gte=now).filter(datetime__lte=end_time)
    return queryset.order_by("datetime")


@sync_to_async
def async_destroy_game_channel(game_channel):
    """Destroy a given game channel object"""
    game_channel.delete()
    return True


# ################################################################## #
@sync_to_async
def async_set_game_channel_created(game, channel_id, link="", name=""):
    """Set the game channel status to created"""
    game_channel = GameChannel.objects.create(game=game, discord_id=channel_id, link=link, name=name)
    if game_channel:
        return game_channel
    return None


@sync_to_async
def async_set_game_channel_warned(game_channel):
    """Update a game channel object to show the 1 hour warning"""
    game_channel.status = GameChannel.ChannelStatuses.WARNED
    game_channel.save()
    return True


@sync_to_async
def async_set_game_channel_reminded(game_channel):
    """Update a game channel object to show the 1 day reminder"""
    game_channel.status = GameChannel.ChannelStatuses.REMINDED
    game_channel.save()
    return True


# ################################################################## #
@sync_to_async
def async_get_game_channels_pending_destruction():
    """Retrieve all game channel objects which are defunct"""
    now = timezone.now()
    expiry_time = now - timedelta(hours=CHANNEL_DESTROY_HOURS)

    queryset = GameChannel.objects.filter(game__datetime__lte=expiry_time)
    queryset = queryset.order_by("game__datetime")
    return list(queryset)  # force evaluation before dropping back to async


@sync_to_async
def async_get_game_channels_pending_reminder():
    """Identify games in need of a 24 hour warning sending"""
    queryset = get_games_pending(hours=CHANNEL_REMIND_HOURS)
    queryset = queryset.exclude(text_channel=None)  # not interested in anything without a channel
    queryset = queryset.exclude(text_channel__status=GameChannel.ChannelStatuses.REMINDED)
    queryset = queryset.exclude(text_channel__status=GameChannel.ChannelStatuses.WARNED)
    return list(queryset)  # force evaluation before leaving this sync context


@sync_to_async
def async_get_game_channels_pending_warning():
    """Get those games which need a 1 hour warning sending"""
    queryset = get_games_pending(minutes=CHANNEL_WARN_MINUTES)
    queryset = queryset.exclude(text_channel=None)  # not interested in anything without a channel
    queryset = queryset.exclude(text_channel__status=GameChannel.ChannelStatuses.WARNED)
    return list(queryset)  # force evaluation before leaving this sync context


@sync_to_async
def async_get_game_channels_pending_creation():
    """Retrieve all game objects that need a channel posting"""
    queryset = get_games_pending(days=CHANNEL_CREATION_DAYS)
    queryset = queryset.filter(text_channel=None)  # Only interested in games which don't yet have a channel
    return list(queryset)  # force evaluation before leaving this sync context


# ################################################################## #
def get_channel_for_game(game: Game) -> GameChannel | None:
    """Get the channel for the specified game if it exists"""
    return game.text_channel.first()


@sync_to_async
def async_get_game_channel_for_game(game: Game) -> GameChannel | None:
    """Get the game channel object related to a game"""
    return get_channel_for_game(game)


@sync_to_async
def async_get_all_current_game_channels():
    """Retrieve all current game channels"""
    queryset = GameChannel.objects.all()
    return list(queryset)  # force evaluation before leaving this sync context


@sync_to_async
def async_get_game_channel_members(channel: GameChannel) -> List[ChannelMember]:
    """Given a game channel object retrieve its expected membership list"""
    channel.refresh_from_db()
    queryset = channel.members.all()
    retval = list(queryset)  # force evaluation before leaving this sync context
    return retval


def add_user_to_channel(user: CustomUser, channel: GameChannel, admin=False, readonly=False) -> bool:
    """Add a user to a channel (or update an existing channel member) with a given set of permissions"""
    channel_member = None
    try:
        channel_member = ChannelMember.objects.get(user=user, channel=channel)
    except ChannelMember.DoesNotExist:
        channel_member = ChannelMember(user=user, channel=channel)
    channel_member.is_admin = admin
    channel_member.is_readonly = readonly
    try:
        channel_member.save()
        return True
    except Exception as e:
        return False


def remove_user_from_channel(user: CustomUser, channel: GameChannel) -> bool:
    """Remove a user from a channel membership"""
    channel_member = None
    try:
        channel_member = ChannelMember.objects.get(user=user, channel=channel)
        channel_member.delete()
        return True
    except ChannelMember.DoesNotExist:
        return False


def populate_channel(channel: GameChannel) -> int:
    """Add expected ChannelMember entries"""
    # Add DM with admin permissions
    add_user_to_channel(channel.game.dm.user, channel, admin=True, readonly=False)
    # Add players with read/write permissions
    all_players = Player.objects.filter(game=channel.game)
    party = all_players.filter(standby=False)
    for player in party:
        add_user_to_channel(player.user, channel, admin=False, readonly=False)
    waitlist = all_players.filter(standby=True)
    for player in waitlist:
        add_user_to_channel(player.user, channel, admin=False, readonly=True)


def remove_excess_members_from_channel(channel: GameChannel) -> int:
    """remove any unexpected Channelmember entries for a given game channel"""
    channel_members = ChannelMember.objects.filter(channel=channel)
    players = Player.objects.filter(game=channel.game).values_list("user")

    for member in channel_members:
        if member.user not in players and member.user is not channel.game.dm.user:
            member.delete()


def set_default_channel_membership(channel: GameChannel) -> bool:
    """Set a standard set of membership permissions"""
    populate_channel(channel)
    # remove_excess_members_from_channel(channel)
    return True


@sync_to_async
def async_set_default_channel_membership(channel: GameChannel) -> bool:
    """Async wrapper for setting channel membership"""
    return set_default_channel_membership(channel)
