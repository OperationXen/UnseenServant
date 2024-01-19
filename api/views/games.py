from datetime import timedelta

from django.utils import timezone
from rest_framework.permissions import IsAuthenticated, IsAuthenticatedOrReadOnly
from rest_framework.response import Response
from rest_framework.decorators import action
from rest_framework.status import *
from rest_framework.viewsets import ViewSet

from api.serialisers.games import GameCreationSerialiser, GameSerialiser, PlayerSerialiser
from core.models import DM, Game, Player
from core.utils.sanctions import check_discord_user_good_standing
from core.utils.user import get_user_available_credit
from core.utils.games import handle_game_player_add


class GamesViewSet(ViewSet):
    """Views for game objects"""

    permission_classes = [IsAuthenticatedOrReadOnly]

    @action(detail=True, methods=["post"], permission_classes=[IsAuthenticated])
    def join(self, request, pk):
        """Request to join a specified game"""
        try:
            game = Game.objects.get(pk=pk)
        except Game.DoesNotExist:
            return Response({"message": "Invalid game ID"}, HTTP_400_BAD_REQUEST)

        if game.dm.user == request.user:
            return Response({"message": "You cannot play in your own game"}, HTTP_400_BAD_REQUEST)
        if not check_discord_user_good_standing(request.user.discord_id):
            return Response({"message": "You are currently banned from using this system"}, HTTP_403_FORBIDDEN)
        available_credit = get_user_available_credit(request.user)
        if not available_credit > 0:
            return Response(
                {"message": "You do not have enough available credits to join this game"}, HTTP_401_UNAUTHORIZED
            )
        player = handle_game_player_add(game, request.user.discord_id, request.user.discord_name)

        serialiser = PlayerSerialiser(player)
        return Response(serialiser.data, HTTP_200_OK)

    def list(self, request):
        """List games"""
        yesterday = timezone.now() - timedelta(days=1)

        queryset = Game.objects.filter(datetime__gte=yesterday)
        queryset = queryset.filter(ready=True)
        serialised = GameSerialiser(queryset, many=True)
        return Response(serialised.data)

    def get(self, request, pk=None):
        """Get a single game"""
        try:
            game = Game.objects.get(pk=pk)
            serialised = GameSerialiser(game, many=False)
            return Response(serialised.data)
        except Game.DoesNotExist:
            return Response({"message": "Cannot find this game"}, HTTP_404_NOT_FOUND)
        
    def create(self, request):
        """Create a new game"""
        try:
            dm = DM.objects.get(user=request.user)
            serialiser = GameCreationSerialiser(data=request.data)
            if serialiser.is_valid():
                game = serialiser.save(dm=dm)
                serialised = GameSerialiser(game, many=False)
                return Response(serialised.data, HTTP_201_CREATED)
            else:
                errors = serialiser.errors;
                return Response({"message": "Failed to create game", "errors": errors}, HTTP_400_BAD_REQUEST)        
        except DM.DoesNotExist:
            return Response({"message": "You are not registered as a DM"}, HTTP_403_FORBIDDEN)

    def partial_update(self, request, pk=None):
        """Update an existing game"""
        try:
            game = Game.objects.get(pk=pk)
        except Game.DoesNotExist:
            return Response({"message": "Cannot find this game"}, HTTP_400_BAD_REQUEST)
        if game.dm.user != request.user:
            return Response({"message": "You do not have permissions to change this game"}, HTTP_403_FORBIDDEN)

        try:
            serialiser = GameCreationSerialiser(game, data=request.data, partial=True)
            if serialiser.is_valid():
                game = serialiser.save()
                return Response(serialiser.data, HTTP_200_OK)
            else:
                errors = serialiser.errors;
                return Response({"message": "Failed to update game", "errors": errors}, HTTP_400_BAD_REQUEST)        
        except Exception as e:
            return Response({"message": "Unable to change this game"}, HTTP_500_INTERNAL_SERVER_ERROR)

    def delete(self, request, pk=None):
        """Delete a game"""
        try:
            game = Game.objects.get(pk=pk)
        except Game.DoesNotExist:
            return Response({"message": "Cannot find this game"}, HTTP_400_BAD_REQUEST)

        if game.dm.user != request.user:
            return Response({"message": "You do not have permissions to change this game"}, HTTP_403_FORBIDDEN)
        # Remove players and game
        players = Player.objects.filter(game=game)
        players.delete()
        game.delete()
        return Response({"message": "Game deleted"}, HTTP_200_OK)
    
    def game_variants(self, request):
        """Get the variants of games available for a game"""
        choices = [(key, value) for key, value in Game.GameTypes.choices]
        return Response(choices);

    def game_realms(self, request):
        """Get the realms available for a game"""
        choices = [(key, value) for key, value in Game.Realms.choices]
        return Response(choices);
