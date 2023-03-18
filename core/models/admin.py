from django.contrib.auth.models import AbstractUser
from django.db import models


class CustomUser(AbstractUser):
    """ Custom user model for storing discord user information """
    discord_name = models.CharField(null=True, blank=True, max_length=64, help_text='User name and discriminator')
    discord_discriminator = models.CharField(null=True, blank=True, max_length=16, help_text='Discord discriminator number')
    discord_id = models.PositiveBigIntegerField(null=True, blank=True, help_text='The discord ID number of the user')
    avatar = models.URLField(null=True, blank=True, help_text='Path to the users avatar image')

    class Meta:
        verbose_name = "Discord User"
        verbose_name_plural = "Discord Users"


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
