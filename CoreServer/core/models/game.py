from django.db import models


class DM(models.Model):
    """ Representation of a DM """
    discord_name = models.CharField(max_length=32, help_text='Discord username')
    name = models.CharField(max_length=64, help_text='DM\'s chosen alias or handle')
    description = models.TextField(help_text='Flavour text / details to show')

    def __str__(self):
        return f"{self.discord_name}"


class Game(models.Model):
    """ Defines an specific scheduled game """
    class Status(models.TextChoices):
        """ Internal class to specify game statuses """
        CANCELLED = 'Cancelled', ('Cancelled')
        DRAFT = 'Draft', ('Draft')
        PENDING = 'Pending', ('Pending')
        PRIORITY = 'Priority', ('Priority')
        RELEASED = 'Released', ('Released')

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
    warnings = models.TextField(blank=True, default='None', help_text='Content warnings or advisories')
    
    status = models.TextField(max_length=16, choices=Status.choices, default=Status.DRAFT, help_text='Game status')
    channel = models.CharField(blank=True, max_length=32, help_text='Discord channel to use for this game')
    streaming = models.BooleanField(default=False, help_text='Game is streaming or not')

    datetime_release = models.DateTimeField(help_text='Date/Time game is released for signups')
    datetime_open_release = models.DateTimeField(help_text='Date/Time game is released to gen-pop')
    datetime = models.DateTimeField(help_text='Date/Time game is starting')
    length = models.CharField(max_length=48, default="2 hours", blank=True, help_text='Planned duration of game')

    def __str__(self):
        return f"{self.dm.discord_name} - {self.name}"


class Character(models.Model):
    """ Character instances """

    # Character details could be placed in a dedicated model
    dnd_beyond_link = models.URLField(blank=True, help_text='Link to character sheet on D&D Beyond')
    forewarning = models.TextField(blank=True, help_text='Warnings of shenanigans, or notes for DM')


class Player(models.Model):
    """ Specifies a player within a specific game """
    game = models.ForeignKey(Game, related_name='players', on_delete=models.CASCADE, help_text='Game user is playing in')
    standby = models.BooleanField(default=False, help_text='If player is a standby player')
    waitlist = models.IntegerField(null=True, blank=True, help_text='Position in queue for place in game')
    discord_name = models.CharField(max_length=32, help_text='Discord username')
    character = models.ForeignKey(Character, null=True, blank=True, on_delete=models.SET_NULL, help_text='Character info')
    # waitlisting priority for higher ranks (exact implementation to follow)
    # waitlist alerting logic, perhaps pm users and give an hour to decline?

    def __str__(self):
        return f"{self.discord_name}"

class Ban(models.Model):
    """ Records of player bans """

    class BanTypes(models.TextChoices):
        """ Internal class to store enumeration of different ban types """
        PERM = 'PM', ('Permanent ban')
        HARD = 'HD', ('Hard ban')   # removes player from any games
        SOFT = 'ST', ('Soft ban')   # leaves player in games

    discord_name = models.CharField(max_length=32, help_text='Banned player name')
    datetime_start = models.DateTimeField(help_text='Ban start date/time')
    datetime_end = models.DateTimeField(help_text='Ban expiry date/time')
    issued_by = models.CharField(max_length=32, help_text='Name of the issuing admin')
    reason = models.TextField(help_text='Reason for the  ban to be issued')
    variant = models.TextField(max_length=2, choices=BanTypes.choices, default=BanTypes.HARD, help_text='Type of ban')

    def __str__(self):
        return(f"{self.discord_name}")