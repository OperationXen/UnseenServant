from django.db import models
from django.utils import timezone

from game import Game


class GameChannel(models.Model):
    """Object that defines a game channel"""

    game = models.ForeignKey(Game, on_delete=models.CASCADE, related_name="channel")
    discord_id = models.CharField(null=True, blank=True, help_text="Discord channel ID")
    link = models.URLField(null=True, blank=True, help_text="Link to the channel on discord")
    name = models.CharField(blank=False, default="Unnamed game")
