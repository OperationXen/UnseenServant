from typing import List

from datetime import timedelta
from django.utils import timezone
from asgiref.sync import sync_to_async

from core.errors import ChannelError
from config.settings import CHANNEL_CREATION_DAYS, CHANNEL_REMIND_HOURS, CHANNEL_WARN_MINUTES, CHANNEL_DESTROY_HOURS
from core.models.channel import GameChannel
from core.models.game import Game


def get_games_pending(hours=0, days=0, minutes=0):
    """Get games due to start within the specified timeframe"""
    now = timezone.now()
    end_time = now + timedelta(hours=hours, days=days, minutes=minutes)

    queryset = Game.objects.filter(ready=True)
    queryset = queryset.filter(datetime__gte=now).filter(datetime__lte=end_time)
    return queryset.order_by("datetime")


def get_games_recent(hours=0, days=0, minutes=0):
    """get games that have started within a specified timeframe"""
    now = timezone.now()
    start_time = now - timedelta(hours=hours, days=days, minutes=minutes)
    queryset = Game.objects.filter(ready=True)
    queryset = queryset.filter(datetime__lte=now).filter(datetime__gte=start_time)
    return queryset.order_by("datetime")


def get_games_in_progress(hours_start=2, hours_elapsed=1):
    """get games that have started within a number of hours, but which have been going for an elapsed period"""
    now = timezone.now()
    # List of all the games that have started within the last X hours
    recently_started = get_games_recent(hours=hours_start)
    # filter those to those that started at least Y hours ago
    started_before = now - timedelta(hours=hours_elapsed)
    queryset = recently_started.filter(datetime__lte=started_before)
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


@sync_to_async
def async_set_game_channel_summarised(game_channel):
    """Update a game channel object to show the session log summary"""
    game_channel.status = GameChannel.ChannelStatuses.SUMMARISED
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


# ################################################################## #
def get_games_pending_channel_reminder():
    """Identify games in need of a 24 hour warning sending"""
    queryset = get_games_pending(hours=CHANNEL_REMIND_HOURS)
    queryset = queryset.exclude(text_channel=None)  # not interested in anything without a channel
    queryset = queryset.exclude(text_channel__status=GameChannel.ChannelStatuses.REMINDED)
    queryset = queryset.exclude(text_channel__status=GameChannel.ChannelStatuses.WARNED)
    # force evaluation before leaving this sync context
    return list(queryset)


@sync_to_async
def async_get_games_pending_channel_reminder():
    game_channels = get_games_pending_channel_reminder()
    return game_channels


# ################################################################## #
def get_games_pending_channel_warning() -> List[Game]:
    """Get those games which need a 1 hour warning sending"""
    queryset = get_games_pending(minutes=CHANNEL_WARN_MINUTES)
    queryset = queryset.exclude(text_channel=None)  # not interested in anything without a channel
    queryset = queryset.exclude(text_channel__status=GameChannel.ChannelStatuses.WARNED)
    # force evaluation before leaving this sync context
    return list(queryset)


@sync_to_async
def async_get_games_pending_channel_warning():
    game_channels = get_games_pending_channel_warning()
    return game_channels


# ################################################################## #
@sync_to_async
def async_get_games_pending_channel_creation():
    """Retrieve all game objects that need a channel posting"""
    queryset = get_games_pending(days=CHANNEL_CREATION_DAYS)
    queryset = queryset.filter(text_channel=None)  # Only interested in games which don't yet have a channel
    return list(queryset)  # force evaluation before leaving this sync context


# ################################################################## #
def get_games_pending_summary_post() -> list[Game]:
    """Retrieve all games that have started but which have not yet had a summary posted"""

    queryset = get_games_in_progress(hours_start=4, hours_elapsed=1)  # get games which are at least an hour old
    queryset = queryset.exclude(text_channel=None)  # not interested in anything without a channel
    queryset = queryset.exclude(text_channel__status=GameChannel.ChannelStatuses.SUMMARISED)
    return list(queryset)


@sync_to_async
def async_get_games_pending_summary_post() -> list[Game]:
    game_channels = get_games_pending_summary_post()
    return game_channels


# ################################################################## #
def get_game_channel_for_game(game: Game) -> GameChannel | None:
    """Get the channel for the specified game if it exists"""
    game_channel = game.text_channel.all().first()
    if game_channel is None:
        raise ChannelError(f"GameChannel does not exist for game: {game.name}")
    return game_channel


@sync_to_async
def async_get_game_channel_for_game(game: Game) -> GameChannel | None:
    """Get the game channel object related to a game"""
    return get_game_channel_for_game(game)


# ################################################################################ #
def get_all_current_game_channels():
    """Retrieve all current game channels"""
    queryset = GameChannel.objects.all()
    return list(queryset)  # force evaluation before leaving this sync context


@sync_to_async
def async_get_all_current_game_channels():
    return get_all_current_game_channels()
