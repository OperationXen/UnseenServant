from django.contrib.auth.models import AbstractUser
from django.db import models

class CustomUser(AbstractUser):
    """ Custom user model includes things like discord username """
    discord_name = models.CharField(max_length=32, help_text='Discord username')

    class Meta:
        verbose_name = 'Admin panel user'
        verbose_name_plural = 'Admin panel users'
