from django.db import models
from django.utils import timezone

from .game import Game


class GameChannel(models.Model):
    """Object that defines a game channel"""

    class ChannelStatuses(models.TextChoices):
        """ Internal class to define possible game types """
        READY = 'Ready', ('Channel created')
        REMINDED = 'Reminder sent', ('Members reminded of game')
        WARNED = 'Warning sent', ('1 Hour ping sent')

    game = models.ForeignKey(Game, on_delete=models.CASCADE, related_name="text_channel")
    discord_id = models.CharField(null=True, blank=True, max_length=32, help_text="Discord channel ID")
    link = models.URLField(null=True, blank=True, help_text="Link to the channel on discord")
    name = models.CharField(blank=False, max_length=64, default="Unnamed game")
    status = models.TextField(choices=ChannelStatuses.choices, max_length=32, default=ChannelStatuses.READY, help_text='Status of the channel') 
