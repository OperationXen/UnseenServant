from django.db import models

from core.models.game import Game, Character
from core.utils.time import a_year_from_now, a_month_from_now


class BonusCredit(models.Model):
    """ Describes a number of additional bonus games awarded to a given player """
    discord_id = models.CharField(null=True, blank=True, max_length=32, help_text='Discord ID of player')
    discord_name = models.CharField(blank=True, max_length=32, help_text='Player name to receive bonus game credits')
    credits = models.IntegerField(default=1, help_text='Number of additional credits', verbose_name='Number of bonus games')
    expires = models.DateTimeField(null=True, blank=True, help_text='Date that these credits expire', verbose_name='Expiry date (optional)')
    issuer_id = models.CharField(null=True, blank=True, max_length=32, help_text='Discord ID of issuing moderator')
    issuer_name = models.CharField(max_length=32, help_text='Name of the issuing moderator')
    reason = models.TextField(blank=True, null=True, help_text='The reason that these games have been awarded')
    
    def __str__(self):
        return f"[{self.expires.date()}] {self.discord_name} ({self.credits})"

    class Meta:
        indexes = [models.Index(fields=['discord_id', 'expires'])]


class Player(models.Model):
    """ Specifies a player within a specific game """
    game = models.ForeignKey(Game, related_name='players', on_delete=models.CASCADE, help_text='Game user is playing in')
    standby = models.BooleanField(default=False, help_text='If player is a waitlist player', verbose_name='Waitlist')
    waitlist = models.IntegerField(null=True, blank=True, help_text='Rank in queue for place in game', verbose_name='Waitlist Position')
    discord_id = models.CharField(null=True, blank=True, max_length=32, help_text='Discord ID of player')
    discord_name = models.CharField(blank=True, max_length=32, help_text='Discord username')
    character = models.ForeignKey(Character, null=True, blank=True, on_delete=models.SET_NULL, help_text='Character info')
    # waitlisting priority for higher ranks (exact implementation to follow)
    # waitlist alerting logic, perhaps pm users and give an hour to decline?

    def __str__(self):
        return f"{self.game.datetime.date()} | {self.game.name} - {self.discord_name}"

    class Meta:
        indexes = [models.Index(fields=['discord_id', 'game'])]


class Strike(models.Model):
    """ Disciplinary strikes against a user """
    discord_id = models.CharField(null=True, blank=True, max_length=32, help_text='Discord ID of player')
    discord_name = models.CharField(blank=True, max_length=32, help_text='Player name to receive strike')
    datetime = models.DateTimeField(auto_now_add=True, help_text='Strike issued')
    expires = models.DateTimeField(default=a_year_from_now, help_text='Strike expiry date/time')
    issuer_id = models.CharField(null=True, blank=True, max_length=32, help_text='Discord ID of issuing moderator')
    issuer_name = models.CharField(max_length=32, help_text='Name of the issuing moderator')
    reason = models.TextField(help_text='Reason for issuing the strike')

    def __str__(self):
        return f"{self.discord_name} - {self.expires.strftime('%Y/%m/%d %H:%M')}"

    class Meta:
        indexes = [models.Index(fields=['discord_id', 'issuer_id', 'datetime', 'expires'])]


class Ban(models.Model):
    """ Records of player bans """

    class BanTypes(models.TextChoices):
        """ Internal class to store enumeration of different ban types """
        PERM = 'PM', ('Permanent ban')
        HARD = 'HD', ('Hard ban')   # removes player from any games
        SOFT = 'ST', ('Soft ban')   # leaves player in games

    discord_id = models.CharField(null=True, blank=True, max_length=32, help_text='Discord ID of player')
    discord_name = models.CharField(blank=True, max_length=32, help_text='Banned player name')
    datetime_start = models.DateTimeField(auto_now_add=True, help_text='Ban start date/time')
    datetime_end = models.DateTimeField(blank=True, null=True, default=a_month_from_now, help_text='Ban expiry date/time')
    issuer_id = models.CharField(null=True, blank=True, max_length=32, help_text='Discord ID of issuing moderator')
    issuer_name = models.CharField(max_length=32, help_text='Name of the issuing moderator')
    reason = models.TextField(help_text='Reason for the ban to be issued (mandatory)')
    variant = models.TextField(max_length=2, choices=BanTypes.choices, default=BanTypes.HARD, help_text='\'Hard Ban\' removes existing signups, \'Soft\' does not')

    def __str__(self):
        return(f"{self.discord_name}")
    
    class Meta:
        indexes = [models.Index(fields=['discord_id', 'issuer_id', 'variant', 'datetime_start', 'datetime_end'])]
