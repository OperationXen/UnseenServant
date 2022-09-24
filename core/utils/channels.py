from datetime import timedelta
from django.utils import timezone
from asgiref.sync import sync_to_async

from core.models.channel import GameChannel
from core.models.game import Game


def get_games_pending(hours=0, days=0):
    """Get games due to start within the specified timeframe"""
    now = timezone.now()
    end_time = now + timedelta(hours=hours, days=days)

    queryset = Game.objects.filter(ready=True)
    queryset = queryset.filter(datetime__gte=now).filter(datetime__lte=end_time)
    return queryset.order_by("datetime")

@sync_to_async
def get_game_channels_pending_creation():
    """Retrieve all game objects that need a channel posting"""
    queryset = get_games_pending(days=7)
    queryset = queryset.filter(text_channel=None)  # Only interested in games which don't yet have a channel
    return list(queryset)  # force evaluation before leaving this sync context

@sync_to_async
def destroy_game_channel(game_channel):
    """ Destroy a given game channel object """
    game_channel.delete()
    return True

@sync_to_async
def get_game_channels_pending_destruction():
    """ Retrieve all game channel objects which are defunct """
    now = timezone.now()
    expiry_time = now - timedelta(days=3)

    queryset = GameChannel.objects.filter(game__datetime__lte=expiry_time)
    queryset = queryset.order_by('game__datetime')
    return list(queryset)   # force evaluation before dropping back to async

@sync_to_async
def set_game_channel_created(game, channel_id, link='', name=''):
    """ Set the game channel status to created"""
    game_channel = GameChannel.objects.create(game=game, discord_id=channel_id, link=link, name=name)
    if game_channel:
        return game_channel
    return None

@sync_to_async
def get_game_channels_pending_reminder():
    """Identify games in need of a 24 hour warning sending"""
    queryset = get_games_pending(hours=24)
    queryset = queryset.exclude(channel=None)  # not interested in anything without a channel
    queryset = queryset.exclude(game__text_channel_status=GameChannel.ChannelStatuses.REMINDED)
    queryset = queryset.exclude(game__text_channel_status=GameChannel.ChannelStatuses.WARNED)
    return list(queryset)  # force evaluation before leaving this sync context


@sync_to_async
def get_game_channels_pending_warning():
    """Get those games which need a 1 hour warning sending"""
    queryset = get_games_pending(hours=1)
    queryset = queryset.exclude(channel=None)  # not interested in anything without a channel
    queryset = queryset.exclude(game__channel_status=GameChannel.ChannelStatuses.WARNED)
    return list(queryset)  # force evaluation before leaving this sync context
