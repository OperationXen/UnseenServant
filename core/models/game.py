from django.db import models
from django.utils import timezone
from django.core.exceptions import ValidationError

from core.models.dm import DM


class Game(models.Model):
    """Defines an specific scheduled game"""

    class GameTypes(models.TextChoices):
        """Internal class to define possible game types"""

        RES_AL = "Resident AL", ("Resident Adventurer's League")
        GST_AL = "Guest AL DM", ("Community DM Adventurer's League")
        EPC_AL = "Epic AL", ("Epic Adventurers League")
        NON_AL = "Non-AL One Shot", ("Non-AL One Shot")
        CMPGN = "Campaign", ("Campaign")

    class Realms(models.TextChoices):
        """Internal class to define possible realms"""

        FAERUN = "Forgotten Realms", ("Forgotten Realms")
        WILDEMOUNT = "Wildemount", ("Wildemount")
        EBERRON = "Eberron", ("Eberron")
        MISTHUNTERS = "Misthunters", ("Misthunters")
        STRIX = "Strixhaven", ("Strixhaven")
        RAVNICA = "Ravnica", ("Ravnica")
        OTHER = "Other setting", ("Any Other setting")

    dm = models.ForeignKey(
        DM, related_name="games", on_delete=models.CASCADE, help_text="Dungeon Master for this game"
    )
    name = models.CharField(max_length=128, help_text="Adventure Name")
    module = models.CharField(blank=True, max_length=32, help_text="Adventure Code (e.g. CCC-GHC-09)")
    realm = models.TextField(max_length=16, choices=Realms.choices, default=Realms.FAERUN, help_text="Game setting")
    variant = models.TextField(
        max_length=16, choices=GameTypes.choices, default=GameTypes.RES_AL, help_text="Game type"
    )
    description = models.TextField(max_length=1024, blank=True, help_text="Description of this game or flavour text")
    max_players = models.IntegerField(default=6, help_text="Max players for this game")
    level_min = models.IntegerField(default=1, help_text="Minumum starting level")
    level_max = models.IntegerField(default=4, help_text="Maximum player level")
    warnings = models.TextField(blank=True, default="None", help_text="Content warnings or advisories")
    streaming = models.BooleanField(default=False, help_text="Set to indicate that you may wish to stream the game")
    play_test = models.BooleanField(default=False, help_text="Set to indicate that this is a playtest")

    datetime_release = models.DateTimeField(
        blank=True,
        null=True,
        help_text="Date/Time game is released for PATREON signups (UTC)",
        verbose_name="Patreon Release Time",
    )
    datetime_open_release = models.DateTimeField(
        blank=True,
        null=True,
        help_text="Date/Time game is released for GENERAL signups (UTC)",
        verbose_name="General Release Time",
    )
    datetime = models.DateTimeField(help_text="Date/Time game is starting (UTC)", verbose_name="Game Time")
    duration = models.IntegerField(default=4, null=True, help_text="Planned duration of game (hours)")
    ready = models.BooleanField(default=True, help_text="Game is ready for release")

    def __str__(self):
        return f"{self.datetime.date()} | {self.dm.discord_name} - {self.name}"

    def clean(self):
        """Validate data before saving"""
        now = timezone.now()
        if not self.datetime:
            raise ValidationError({"datetime": "Game must have a time"})
        if not self.datetime_release and not self.datetime_open_release:
            raise ValidationError(
                {
                    "datetime_release": "Game needs at least one release time",
                    "datetime_open_release": "Game needs at least one release time",
                }
            )

    class Meta:
        indexes = [models.Index(fields=["dm", "datetime", "datetime_release", "datetime_open_release"])]


class Character(models.Model):
    """Character instances"""

    dnd_beyond_link = models.URLField(blank=True, help_text="Link to character sheet on D&D Beyond")
    forewarning = models.TextField(blank=True, help_text="Warnings of shenanigans, or notes for DM")
