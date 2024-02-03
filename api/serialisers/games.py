from rest_framework.serializers import ModelSerializer, ReadOnlyField, SerializerMethodField

from core.models import Game, Player


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

    id = ReadOnlyField(source="pk")
    dm_name = ReadOnlyField(source="dm.name")
    user_is_dm = SerializerMethodField()
    players = PlayerSummarySerialiser(many=True)

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
            "players",
            "max_players",
            "level_min",
            "level_max",
            "warnings",
            "streaming",
            "play_test",
            "datetime_release",
            "datetime_open_release",
            "datetime",
            "length",
            "user_is_dm",
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
            "length",
            "ready",
        ]
        read_only_fields = ["dm"]
