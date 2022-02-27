from rest_framework.viewsets import ViewSet
from rest_framework.response import Response

from core.models import Game
from api.serialisers import GameSerialiser

# Create your views here.
class GamesViewSet(ViewSet):
    """ Views for game objects """
    def list(self, request):
        """ List games """
        queryset = Game.objects.all()
        serialised = GameSerialiser(queryset, many=True)
        return Response(serialised.data)
