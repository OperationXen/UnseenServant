from django.db import models
from django.utils import timezone

from .game import Game
from .auth import CustomUser


class GameChannel(models.Model):
    """Object that defines a game channel"""

    class ChannelStatuses(models.TextChoices):
        """Internal class to define possible game types"""

        READY = "Ready", ("Channel created")
        REMINDED = "Reminder sent", ("Members reminded of game")
        WARNED = "Warning sent", ("1 Hour ping sent")
        SUMMARISED = "Game started", ("Session summary posted")

    game = models.ForeignKey(Game, on_delete=models.CASCADE, related_name="text_channel")
    discord_id = models.CharField(null=True, blank=True, max_length=32, help_text="Discord channel ID")
    link = models.URLField(null=True, blank=True, help_text="Link to the channel on discord")
    name = models.CharField(blank=False, max_length=64, default="Unnamed game")
    status = models.TextField(
        choices=ChannelStatuses.choices,
        max_length=32,
        default=ChannelStatuses.READY,
        help_text="Status of the channel",
    )

    members = models.ManyToManyField(CustomUser, related_name="game_channels", through="gamechannelmember")

    class Meta:
        indexes = [
            models.Index("game", name="gamechannel_game_idx"),
            models.Index("discord_id", name="gamechannel_discord_idx"),
        ]

    def __str__(self):
        return f"{self.name} [{self.status}]"


class GameChannelMember(models.Model):
    """Object that defines membership in a channel"""

    read_messages = models.BooleanField(null=False, default=True)
    send_messages = models.BooleanField(null=False, default=True)
    read_message_history = models.BooleanField(null=False, default=True)
    use_slash_commands = models.BooleanField(null=False, default=True)
    manage_messages = models.BooleanField(null=False, default=False)

    channel = models.ForeignKey(GameChannel, on_delete=models.CASCADE, related_name="text_channel")
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name="text_channel")

    def __str__(self):
        return f"{self.channel} - {self.user}"
