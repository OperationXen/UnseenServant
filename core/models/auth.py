from django.contrib.auth.models import AbstractUser
from django.db import models


class Rank(models.Model):
    """User ranks"""

    name = models.CharField(max_length=32, help_text="User friendly name for this rank")
    discord_id = models.CharField(null=True, blank=True, max_length=32, help_text="Discord role ID number")
    priority = models.IntegerField(
        help_text="The relative seniority of this rank compared to others (higher = more senior)"
    )
    max_games = models.IntegerField(
        default=0, help_text="Upper limit for games members of this rank are allowed to join"
    )
    patreon = models.BooleanField(default=False, help_text="this rank is reserved for paying members")

    def __str__(self):
        return f"{self.priority} - {self.name} ({self.max_games})"

    class Meta:
        indexes = [models.Index(fields=["priority", "name"])]


class CustomUser(AbstractUser):
    """Custom user model includes things like discord username"""

    discord_id = models.CharField(null=True, blank=True, max_length=32, help_text="Discord ID of user")
    discord_name = models.CharField(max_length=32, help_text="Discord username")

    avatar = models.URLField(null=True, blank=True, help_text="Path to the users avatar image")
    ranks = models.ManyToManyField(
        Rank, related_name="users", help_text="Ranks held by this user (determined by roles)"
    )

    class Meta:
        verbose_name = "Discord User"
        verbose_name_plural = "Discord Users"
