from django.contrib.auth.backends import BaseBackend
from rest_framework.views import Request

from core.models.admin import CustomUser


class DiscordAuthenticationBackend(BaseBackend):
    def authenticate(self, request: Request, user_data, roles) -> CustomUser:
        """ look for an existing user, or create one if not known"""
        existing_user = CustomUser.objects.filter(discord_id=user_data['id']).first()
        if existing_user:
            return existing_user
        existing_user = CustomUser.objects.filter(username=f"{user_data['username']}#{user_data['discriminator']}").first()
        if existing_user:
            return existing_user
        
        print(f"User not found in database, creating a new entry for {user_data['username']}")
        new_user = CustomUser.objects.create_user(
            f"{user_data['username']}#{user_data['discriminator']}",
            discord_name=user_data['username'],
            discord_discriminator=user_data['discriminator'], 
            discord_id=user_data['id'], 
            avatar=user_data['avatar'])
        return new_user
