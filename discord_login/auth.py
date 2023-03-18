from django.contrib.auth.backends import BaseBackend
from rest_framework.views import Request

from core.models.admin import CustomUser


class DiscordAuthenticationBackend(BaseBackend):
    def authenticate(self, request: Request, user_data, roles) -> CustomUser:
        try:
            existing_user = CustomUser.objects.get(discord_id=user_data['id'])
            return existing_user
        except CustomUser.DoesNotExist:
            print(f"User not found in database, creating a new entry for {user_data['username']}")
            new_user = CustomUser.objects.create_user(
                f"{user_data['username']}#{user_data['discriminator']}",
                discord_name=user_data['username'],
                discord_discriminator=user_data['discriminator'], 
                discord_id=user_data['id'], 
                avatar=user_data['avatar'])
            return new_user
