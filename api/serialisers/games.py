from rest_framework.serializers import ModelSerializer, ReadOnlyField, SerializerMethodField

from core.models import Game, Player
from core.utils.user import user_is_player_in_game, user_is_waitlisted_in_game


class PlayerSummarySerialiser(ModelSerializer):
    """Serialise a player (basic, no personal data)"""

    class Meta:
        model = Player
        fields = ["discord_id", "discord_name", "standby"]


class PlayerSerialiser(ModelSerializer):
    """Serialise a player (include related fields)"""

    game_name = ReadOnlyField(source="game.name")

    class Meta:
        model = Player
        fields = ["game", "game_name", "discord_id", "discord_name", "standby", "waitlist"]


class GameSerialiser(ModelSerializer):
    """Serialiser for game objects"""

    def get_user_is_dm(self, game):
        """Checks if the currently logged in user is the DM for this game"""
        try:
            requesting_user = self.context["request"].user
            return game.dm.user == requesting_user
        except:
            return False

    def get_user_is_player(self, game):
        """check to see if the current user is a player in the game"""
        try:
            requesting_user = self.context["request"].user
            return user_is_player_in_game(requesting_user, game)
        except:
            return False

    def get_user_is_waitlisted(self, game):
        """check to see if the current user is a player in the game"""
        try:
            requesting_user = self.context["request"].user
            return user_is_waitlisted_in_game(requesting_user, game)
        except:
            return False

    def get_waitlist(self, game):
        """Get a list of the players who are waitlisted"""
        waitlist = game.players.filter(standby=True)
        return PlayerSummarySerialiser(waitlist, many=True).data

    def get_players(self, game):
        """Get a list of the players who are confirmed as playing"""
        party = game.players.filter(standby=False)
        return PlayerSummarySerialiser(party, many=True).data

    id = ReadOnlyField(source="pk")
    dm_name = ReadOnlyField(source="dm.name")
    players = SerializerMethodField()
    waitlist = SerializerMethodField()
    user_is_dm = SerializerMethodField()
    user_is_player = SerializerMethodField()
    user_is_waitlisted = SerializerMethodField()

    class Meta:
        model = Game
        fields = [
            "id",
            "dm_name",
            "name",
            "module",
            "realm",
            "variant",
            "description",
            "max_players",
            "level_min",
            "level_max",
            "warnings",
            "streaming",
            "play_test",
            "datetime_release",
            "datetime_open_release",
            "datetime",
            "duration",
            "user_is_dm",
            "user_is_player",
            "user_is_waitlisted",
            "players",
            "waitlist",
        ]


class GameCreationSerialiser(ModelSerializer):
    class Meta:
        model = Game
        fields = [
            "name",
            "module",
            "realm",
            "variant",
            "description",
            "max_players",
            "level_min",
            "level_max",
            "warnings",
            "streaming",
            "play_test",
            "datetime_release",
            "datetime_open_release",
            "datetime",
            "duration",
            "ready",
        ]
        read_only_fields = ["dm"]
