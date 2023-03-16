from django.contrib.auth.models import AbstractUser
from django.db import models


class DiscordUser(AbstractUser):
    """ Custom user model for storing discord user information """
    discord_name = models.CharField(max_length=64, help_text='User name and discriminator')
    discord_id = models.PositiveBigIntegerField(help_text='The discord ID number of the user')
    avatar = models.URLField(help_text='Path to the users avatar image')

    class Meta:
        verbose_name = "Discord User"
        verbose_name_plural = "Discord Users"
