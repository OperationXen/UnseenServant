from django.contrib.auth.models import AbstractUser
from django.db import models


class CustomUser(AbstractUser):
    """Custom user model includes things like discord username"""

    discord_name = models.CharField(max_length=32, help_text="Discord username")

    class Meta:
        verbose_name = "Admin panel user"
        verbose_name_plural = "Admin panel users"


class DM(models.Model):
    """Representation of a DM"""

    name = models.CharField(max_length=64, help_text="DM's chosen alias or handle")
    discord_id = models.CharField(null=True, blank=True, max_length=32, help_text="Discord ID of DM")
    discord_name = models.CharField(blank=True, max_length=32, help_text="Discord username")
    description = models.TextField(blank=True, null=True, help_text="Flavour text / details to show")
    rules_text = models.TextField(blank=True, null=True, max_length=1024, help_text="Any banned items / spells, etc")
    muster_text = models.TextField(
        blank=True, null=True, max_length=1024, help_text="Default text to add to mustering embed (option)"
    )
    user = models.ForeignKey(
        CustomUser, null=True, related_name="dm", on_delete=models.CASCADE, help_text="Associated user account"
    )

    class Meta:
        verbose_name = "DM"
        verbose_name_plural = "DMs"
        indexes = [models.Index(fields=["name", "discord_id"])]

    def __str__(self):
        return f"{self.name}"
