from rest_framework.serializers import ModelSerializer, ReadOnlyField, SerializerMethodField

from core.models import Game, Player


class PlayerSummarySerialiser(ModelSerializer):
    """Serialise a player (basic, no personal data)"""

    class Meta:
        model = Player
        fields = ["discord_id", "discord_name", "standby"]


class GameSerialiser(ModelSerializer):
    """Serialiser for game objects"""

    id = ReadOnlyField(source="pk")
    dm_name = ReadOnlyField(source="dm.name")
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
            "datetime_release",
            "datetime_open_release",
            "datetime",
            "length",
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
            "datetime_release",
            "datetime_open_release",
            "datetime",
            "length",
            "ready",
        ]
        read_only_fields = ["dm"]
