from django.contrib.auth.backends import BaseBackend
from rest_framework.views import Request

from discord_login.models import DiscordUser


class DiscordAuthenticationBackend(BaseBackend):
    def authenticate(self, request: Request, userdata) -> DiscordUser:
        try:
            existing_user = DiscordUser.objects.get(discord_id=userdata['discord_id'])
            return existing_user
        except DiscordUser.DoesNotExist:
            print(f"User not found in database, creating a new entry for {userdata.discord_name}")
            new_user = DiscordUser.objects.create_user(
                discord_name=userdata['username'], 
                discord_discriminator=userdata['discriminator'], 
                discord_id=userdata['id'], 
                avatar=userdata['avatar'])
            return new_user
