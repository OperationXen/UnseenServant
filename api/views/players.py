from datetime import datetime

from rest_framework.permissions import IsAuthenticatedOrReadOnly
from rest_framework.response import Response
from rest_framework.status import *
from rest_framework.viewsets import ViewSet

from core.models import Player, Game


class PlayerViewSet(ViewSet):
    """Views for player objects"""

    permission_classes = [IsAuthenticatedOrReadOnly]

    def get(self, request):
        """Retrieve information about a single player in a single game"""
        pass

    def list(self, request):
        """list players in games"""
        exclude_old = request.GET.get("exclude_old", True)
        now = datetime.now()

        players = Player.objects.all()
        if exclude_old:
            players = players.filter(datetime__gte=now)

    def create(self, request):
        """force join a player to a game"""
        game_id = request.POST.get("game_id")
        waitlist = request.POST.get("waitlist", False)
        now = datetime.now()

        try:
            valid_games = Game.objects.filter(datetime__gte=now)
            game = valid_games.get(pk=game_id)
        except Game.DoesNotExist:
            return Response({"message": "Invalid Game"}, HTTP_400_BAD_REQUEST)

    def partial_update(self, request):
        """edit an existing signup"""
        pass

    def delete(self, request):
        """remove a player from a game"""
        pass
