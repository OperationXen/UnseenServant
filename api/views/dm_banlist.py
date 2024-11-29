from rest_framework.permissions import IsAuthenticatedOrReadOnly
from rest_framework.response import Response
from rest_framework.viewsets import ViewSet
from rest_framework.status import *

from core.models import DM, CustomUser
from api.serialisers.dm_banlist import DMBanListSerialiser


class DMBanListViewset(ViewSet):
    """Viewset for DM banlisting"""

    permission_classes = [IsAuthenticatedOrReadOnly]

    def create(self, request):
        """Make a new DM profile"""
        description = request.data.get("description")
        discord_name = request.data.get("discord_name")

        try:
            dm = DM.objects.get(user=request.user)
        except DM.DoesNotExist:
            return Response({"message": "You are not registered as a DM yet"}, HTTP_400_BAD_REQUEST)

        try:
            user = CustomUser.objects.get(name=discord_name)
            dm.banlist.add(user, through_defaults={"description": description})
            dm.save()
            return Response({"message": f"User {user.discord_name} added to banlist"}, HTTP_200_OK)
        except CustomUser.DoesNotExist:
            return Response(
                {"message": "No Unseen Servant user with that discord name can be found"}, HTTP_400_BAD_REQUEST
            )

    def list(self, request):
        """Get the variants of games available for a game"""
        try:
            dm = DM.objects.get(user=request.user)
        except DM.DoesNotExist:
            return Response({"message": "You are not registered as a DM yet"}, HTTP_400_BAD_REQUEST)

        serialsed = DMBanListSerialiser(data=dm.banlist.all())
        return Response(serialsed.data)

    def delete(self, request, pk=None):
        """remove a user from the banlist"""
        discord_name = request.data.get("discord_name")
        try:
            dm = DM.objects.get(user=request.user)
        except DM.DoesNotExist:
            return Response({"message": "You are not registered as a DM yet"}, HTTP_400_BAD_REQUEST)

        try:
            user = CustomUser.objects.get(name=discord_name)
            dm.banlist.remove(user)
            dm.save()
            return Response({"message": f"User {user.discord_name} removed from banlist"}, HTTP_200_OK)
        except CustomUser.DoesNotExist:
            return Response(
                {"message": "No Unseen Servant user with that discord name can be found"}, HTTP_400_BAD_REQUEST
            )
