from django.db import models
from django.utils import timezone
from django.core.exceptions import ValidationError

from core.models.admin import DM

class Game(models.Model):
    """ Defines an specific scheduled game """
    class GameTypes(models.TextChoices):
        """ Internal class to define possible game types """
        RES_AL = 'Resident AL', ('Resident Adventurers League')
        GST_AL = 'Guest AL DM', ('Guest DM Adventurers League')
        EPC_AL = 'Epic AL', ('Epic Adventurers League')
        NON_AL = 'Non-AL One Shot', ('Non-AL One Shot')
        CMPGN = 'Campaign', ('Campaign')

    class Realms(models.TextChoices):
        """ Internal class to define possible realms """
        FAERUN = 'Forgotten Realms', ('Forgotten Realms')
        WILDEMOUNT = 'Wildemount', ('Wildemount')
        EBERRON = 'Eberron', ('Eberron')
        MISTHUNTERS = 'Misthunters', ('Misthunters')
        STRIX = 'Strixhaven', ('Strixhaven')
        RAVNICA = 'Ravnica', ('Ravnica')
        OTHER = 'Other setting', ('Any Other setting')

    dm = models.ForeignKey(DM, related_name='games', on_delete=models.CASCADE, help_text='Dungeon Master for this game')
    name = models.CharField(max_length=128, help_text='User defined game name')
    module = models.CharField(blank=True, max_length=32, help_text='AL module code')
    realm = models.TextField(max_length=16, choices=Realms.choices, default=Realms.FAERUN, help_text='Game setting')
    variant = models.TextField(max_length=16, choices=GameTypes.choices, default=GameTypes.RES_AL, help_text='Game type')
    description = models.TextField(blank=True, help_text='Description of this game or flavour text')
    max_players = models.IntegerField(default=6, help_text='Max players for this game')
    level_min = models.IntegerField(default=1, help_text='Minumum starting level')
    level_max = models.IntegerField(default=4, help_text='Maximum player level')
    warnings = models.TextField(blank=False, default='None', help_text='Content warnings or advisories')
    channel = models.CharField(blank=True, max_length=32, help_text='Discord channel to use for this game')
    streaming = models.BooleanField(default=False, help_text='Game is streaming or not')

    datetime_release = models.DateTimeField(blank=True, null=True, help_text='Date/Time game is released for signups (your local time)')
    datetime_open_release = models.DateTimeField(blank=True, null=True, help_text='Date/Time game is released to gen-pop (your local time)')
    datetime = models.DateTimeField(help_text='Date/Time game is starting (your local time)')
    length = models.CharField(max_length=48, default="2 hours", blank=True, help_text='Planned duration of game')

    ready = models.BooleanField(default=True, help_text='If this game is ready to be published, if this is not set the game will be hidden')

    def __str__(self):
        return f"{self.dm.discord_name} - {self.name}"

    def clean(self):
        """ Validate data before saving """
        now = timezone.now()
        if self.datetime < now:
            raise ValidationError({'datetime': 'Game cannot be in the past'})
        if not self.datetime_release and not self.datetime_open_release:
            raise ValidationError({'datetime_release': 'Game needs at least one release time', 'datetime_open_release': 'Game needs at least one release time'})
    
    class Meta:
        indexes = [models.Index(fields=['dm', 'datetime', 'datetime_release', 'datetime_open_release'])]


class Character(models.Model):
    """ Character instances """
    dnd_beyond_link = models.URLField(blank=True, help_text='Link to character sheet on D&D Beyond')
    forewarning = models.TextField(blank=True, help_text='Warnings of shenanigans, or notes for DM')
