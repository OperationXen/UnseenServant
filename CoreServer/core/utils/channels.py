from datetime import timedelta
from django.utils import timezone
from asgiref.sync import sync_to_async

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
    queryset = queryset.filter(channel=None)  # Only interested in games which don't yet have a channel
    return list(queryset)  # force evaluation before leaving this sync context


@sync_to_async
def get_game_channels_pending_reminder():
    """Identify games in need of a 24 hour warning sending"""
    queryset = get_games_pending(hours=24)
    queryset = queryset.exclude(channel=None)  # not interested in anything without a channel
    return list(queryset)  # force evaluation before leaving this sync context


@sync_to_async
def get_game_channels_pending_warning():
    """Get those games which need a 1 hour warning sending"""
    queryset = get_games_pending(hours=1)
    queryset = queryset.exclude(channel=None)  # not interested in anything without a channel
    return list(queryset)  # force evaluation before leaving this sync context
