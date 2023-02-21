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
        """ Retrieve information about a single game"""
        pass

    def list(self, request):
        """ list players in games """
        discord_id = request.GET.get("discord_id")
        exclude_old = request.GET.get("exclude_old", True)
        now = datetime.now()

        players = Player.objects.all()
        if exclude_old:
            players = players.filter(datetime__gte=now)

    def create(self, request):
        """ join a player to a game """
        game_id = request.POST.get("game_id")
        discord_id = request.POST.get("discord_id")
        waitlist = request.POST.get("waitlist", False)
        now = datetime.now()

        try:
            valid_games = Game.objects.filter(datetime__gte=now)
            game = valid_games.get(pk=game_id)
        except Game.DoesNotExist:
            return Response({"message": "Invalid Game"}, HTTP_400_BAD_REQUEST)

        if discord_id:
            # allow DM to add arbitrary people to their own game
            if request.user.has_perm('admin') or game.dm.user == request.user:
                add_player_to_game(discord_id, game, waitlist=waitlist)
        else:
            if user_has_credit(request.user):
                add_player_to_game(request.user, game)
                return Response({"message": f"Added {request.user.username} to {game.name}"}, HTTP_200_OK)
            else: 
                return Response({"message": "You do not have sufficient credit to join this game"}, HTTP_401_UNAUTHORIZED)
      
    def partial_update(self, request):
        """ edit an existing signup """
        pass

    def delete(self, request):
        """ remove a player from a game """
        pass
