from rest_framework.permissions import IsAuthenticatedOrReadOnly
from rest_framework.response import Response
from rest_framework.viewsets import ViewSet
from rest_framework.status import *

from core.models.dm import DM
from api.serialisers.dm import DMSerialiser


class DMProfileViewset(ViewSet):
    """Viewset for DM profile information"""

    permission_classes = [IsAuthenticatedOrReadOnly]

    def create(self, request):
        """Make a new DM profile"""
        existing_profile = DM.objects.filter(user=request.user)
        if existing_profile.exists():
            return Response({"message": "You're already registered as a DM"}, HTTP_400_BAD_REQUEST)

        serialiser = DMSerialiser(data=request.data)
        if serialiser.is_valid():
            # Don't allow users to register other people as DMs, that would be weird
            serialiser.save(user=request.user)
            return Response(serialiser.data, HTTP_201_CREATED)
        else:
            errors = serialiser.errors
            return Response({"message": "Failed to create DM profile", "errors": errors}, HTTP_400_BAD_REQUEST)

    def details(self, request, pk=None):
        """get single DM profile"""
        try:
            if pk == "me":
                if request.user.is_anonymous:
                    return Response({"message": "You are not logged in"}, status=HTTP_401_UNAUTHORIZED)
                dm = DM.objects.get(user=request.user)
            else:
                dm = DM.objects.get(pk=pk)
            serialised = DMSerialiser(dm, many=False)
            return Response(serialised.data)
        except DM.DoesNotExist:
            return Response({"message": "This DM does not exist"}, status=HTTP_400_BAD_REQUEST)
        except Exception as e:
            return Response(status=HTTP_500_INTERNAL_SERVER_ERROR)

    def list(self, request):
        """Get the variants of games available for a game"""
        dms = DM.objects.all()
        serialised = DMSerialiser(dms, many=True)
        return Response(serialised.data)

    def partial_update(self, request, pk=None):
        """Update"""
        try:
            if pk == "me":
                if not DM.objects.filter(user=request.user).exists():
                    dm = DM.objects.create(user=request.user, name=f"DM {request.user.discord_name}")
                else:
                    dm = DM.objects.get(user=request.user)
            else:
                dm = DM.objects.get(pk=pk)
        except DM.DoesNotExist:
            return Response({"message": "This DM does not exist"}, status=HTTP_400_BAD_REQUEST)
        if dm.user != request.user and not request.user.is_superuser:
            return Response({"message": "You do not have permissions to change this DM profile"}, HTTP_403_FORBIDDEN)

        try:
            serialiser = DMSerialiser(dm, data=request.data, partial=True)
            if serialiser.is_valid():
                dm = serialiser.save()
                return Response(serialiser.data)
            else:
                errors = serialiser.errors
                return Response({"message": "Failed to update DM profile", "errors": errors}, HTTP_400_BAD_REQUEST)
        except Exception as e:
            return Response({"message": "Unable to change this DM profile"}, HTTP_500_INTERNAL_SERVER_ERROR)

    def delete(self, request, pk=None):
        """remove a DM profile"""
        try:
            dm = DM.objects.get(pk=pk)
            if dm.user != request.user and not request.user.is_superuser:
                return Response({"message": "You cannot delete another users profile"}, HTTP_403_FORBIDDEN)
            dm.delete()
            return Response({"message": "DM profile deleted"})
        except DM.DoesNotExist:
            return Response({"message": "This DM does not exist"}, status=HTTP_400_BAD_REQUEST)
