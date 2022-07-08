from django.utils import timezone
from datetime import timedelta
from rest_framework.viewsets import ViewSet
from rest_framework.response import Response

from core.models import Game
from api.serialisers.games import GameSerialiser


class GamesViewSet(ViewSet):
    """ Views for game objects """
    def list(self, request):
        """ List games """
        yesterday = timezone.now() - timedelta(days=1)

        queryset = Game.objects.filter(datetime__gte=yesterday)
        queryset = queryset.filter(ready=True)
        serialised = GameSerialiser(queryset, many=True)
        return Response(serialised.data)
