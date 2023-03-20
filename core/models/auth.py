from django.contrib.auth.models import AbstractUser
from django.db import models


class Rank(models.Model):
    """ User ranks """
    name = models.CharField(max_length=32, help_text='User friendly name for this rank')
    discord_id = models.CharField(null=True, blank=True, max_length=32, help_text='Discord role ID number')
    priority = models.IntegerField(help_text='The relative seniority of this rank compared to others (higher = more senior)')
    max_games = models.IntegerField(default=0, help_text='Upper limit for games members of this rank are allowed to join')
    patreon = models.BooleanField(default=False, help_text='this rank is reserved for paying members')

    def __str__(self):
        return f"{self.priority} - {self.name} ({self.max_games})"

    class Meta:
        indexes = [models.Index(fields=['priority', 'name'])]

class CustomUser(AbstractUser):
    """ Custom user model for storing discord user information """
    discord_name = models.CharField(null=True, blank=True, max_length=64, help_text='User name and discriminator')
    discord_discriminator = models.CharField(null=True, blank=True, max_length=16, help_text='Discord discriminator number')
    discord_id = models.PositiveBigIntegerField(null=True, blank=True, help_text='The discord ID number of the user')
    avatar = models.URLField(null=True, blank=True, help_text='Path to the users avatar image')

    ranks = models.ManyToManyField(Rank, related_name='users', help_text='Ranks held by this user (determined by roles)')

    class Meta:
        verbose_name = "Discord User"
        verbose_name_plural = "Discord Users"
