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
from core.utils.players import populate_game_from_waitlist
from core.utils.user import get_user_available_credit, user_in_game
from core.utils.user import user_on_dm_banlist, user_signup_permissions_valid
from core.utils.games import game_has_player_by_discord_id, player_dropout_permitted
from core.utils.games_rework import add_user_to_game, remove_user_from_game


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
        if game_has_player_by_discord_id(game, request.user.discord_id):
            return Response({"message": "You are already in this game"}, HTTP_400_BAD_REQUEST)
        if not check_discord_user_good_standing(request.user.discord_id):
            return Response({"message": "You are currently banned from using this system"}, HTTP_403_FORBIDDEN)

        if not user_signup_permissions_valid(request.user, game):
            return Response({"message": "You lack the roles needed to sign up to this game"})
        if user_on_dm_banlist(request.user, game.dm):
            return Response({"message": "You may not sign up to games run by this DM"})

        available_credit = get_user_available_credit(request.user)
        if not available_credit > 0:
            return Response({"message": "You do not have any available credits"}, HTTP_401_UNAUTHORIZED)
        # Ensure that any waitlisted players get priority
        populate_game_from_waitlist(game)
        player = add_user_to_game(request.user, game)
        if player:
            serialiser = PlayerSerialiser(player)
            return Response(serialiser.data, HTTP_200_OK)
        else:
            return Response({"message": "Unable to add you to this game"}, HTTP_500_INTERNAL_SERVER_ERROR)

    @action(detail=True, methods=["post"], permission_classes=[IsAuthenticated])
    def drop(self, request, pk):
        """Drop out of a specified game"""
        try:
            game = Game.objects.get(pk=pk)
        except Game.DoesNotExist:
            return Response({"message": "Invalid game ID"}, HTTP_400_BAD_REQUEST)

        if not player_dropout_permitted(game):
            return Response({"message": "This game is in the past and so you cannot leave it"}, HTTP_400_BAD_REQUEST)

        if not user_in_game(request.user, game):
            return Response({"message": "You are not in this game"}, HTTP_400_BAD_REQUEST)
        else:
            remove_user_from_game(request.user, game)
            populate_game_from_waitlist(game)
            # TODO update player channel permissions?
            return Response({"message": f"Removed {request.user.discord_name} from {game.name}"}, HTTP_200_OK)

    def list(self, request):
        """List games"""
        yesterday = timezone.now() - timedelta(days=1)

        queryset = Game.objects.filter(datetime__gte=yesterday)
        queryset = queryset.filter(ready=True)
        serialised = GameSerialiser(queryset, many=True, context={"request": request})
        return Response(serialised.data)

    def get(self, request, pk=None):
        """Get a single game"""
        try:
            game = Game.objects.get(pk=pk)
            serialised = GameSerialiser(game, many=False, context={"request": request})
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
                errors = serialiser.errors
                return Response({"message": "Failed to create game", "errors": errors}, HTTP_400_BAD_REQUEST)
        except DM.DoesNotExist:
            return Response({"message": "You are not registered as a DM"}, HTTP_403_FORBIDDEN)
        except DM.MultipleObjectsReturned:
            return Response({"message": "Multiple DMs detected for user"}, HTTP_400_BAD_REQUEST)

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
                errors = serialiser.errors
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
