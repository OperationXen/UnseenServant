from django.utils import timezone
from datetime import timedelta
from rest_framework.viewsets import ViewSet
from rest_framework.response import Response
from rest_framework.status import *
from rest_framework.permissions import IsAuthenticatedOrReadOnly

from core.models import Game
from api.serialisers.games import GameSerialiser, GameCreationSerialiser


class GamesViewSet(ViewSet):
    """ Views for game objects """
    permission_classes = [IsAuthenticatedOrReadOnly]

    def list(self, request):
        """ List games """
        yesterday = timezone.now() - timedelta(days=1)

        queryset = Game.objects.filter(datetime__gte=yesterday)
        queryset = queryset.filter(ready=True)
        serialised = GameSerialiser(queryset, many=True)
        return Response(serialised.data)

    def create(self, request):
        """ Create a new game """
        serialiser = GameCreationSerialiser(data = request.data)
        if serialiser.is_valid():
            game = serialiser.save()
            return Response(serialiser.data, HTTP_201_CREATED)
        return Response({'message': 'Failed to create game'}, HTTP_400_BAD_REQUEST)
