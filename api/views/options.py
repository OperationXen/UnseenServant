from rest_framework.response import Response
from rest_framework.viewsets import ViewSet

from core.models.game import Game


class GameVariantOptionsViewset(ViewSet):
    def list(self, request):
        """Get the variants of games available for a game"""
        choices = [{key: value} for key, value in Game.GameTypes.choices]
        return Response(choices)


class GameRealmOptionsViewset(ViewSet):
    def list(self, request):
        """Get the realms available for a game"""
        choices = [{key: value} for key, value in Game.Realms.choices]
        return Response(choices)
