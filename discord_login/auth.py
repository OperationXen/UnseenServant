from django.contrib.auth.backends import BaseBackend
from rest_framework.views import Request

from core.utils.ranks import get_user_ranks
from core.models.auth import CustomUser


class DiscordAuthenticationBackend(BaseBackend):
    def set_user_ranks(self, user, roles: list):
        user_ranks = get_user_ranks(roles)
        user.ranks.set(user_ranks)
        user.save()

    def update_user(self, user, user_data: dict, roles: list) -> bool:
        """Update an existing user object with latest data"""
        try:
            user_ranks = get_user_ranks(roles)
            user.ranks.set(user_ranks)

            user.username = f"{user_data['username']}"
            user.discord_id = user_data["id"]
            user.save()
            return True
        except Exception as e:
            return False

    def authenticate(self, request: Request, user_data, roles) -> CustomUser:
        """look for an existing user, or create one if not known"""
        try:
            existing_user = CustomUser.objects.filter(discord_id=user_data["id"]).first()
            if not existing_user:
                existing_user = CustomUser.objects.filter(username=f"{user_data['username']}").first()

            if existing_user:
                self.update_user(existing_user, user_data, roles)
                return existing_user

            print(f"User not found in database, creating a new entry for {user_data['username']}")
            new_user = CustomUser.objects.create_user(
                f"{user_data['username']}",
                discord_name=user_data["username"],
                discord_id=user_data["id"],
                avatar=user_data["avatar"],
            )
            self.set_user_ranks(new_user, roles)
            return new_user
        except Exception as e:
            return False

    def get_user(self, user_id):
        """Get the user object for a given user ID"""
        user = CustomUser.objects.get(pk=user_id)
        return user
