from rest_framework.serializers import ModelSerializer, ReadOnlyField, SerializerMethodField

from core.models import Game, Player


class PlayerSummarySerialiser(ModelSerializer):
    """ Serialise a player (basic, no personal data) """
    class Meta:
        model = Player
        fields = ['discord_name', 'standby']


class GameSerialiser(ModelSerializer):
    """ Serialiser for game objects """
    id = ReadOnlyField(source='pk')
    dm_name = ReadOnlyField(source='dm.name')
    players = PlayerSummarySerialiser(many=True)

    number_of_players = SerializerMethodField()
    number_of_waitlisted = SerializerMethodField()

    def get_number_of_players(self, game):
        """ Retrieve the current number of players for a given game """
        players = game.players.filter(standby=False)
        return players.count()

    def get_number_of_waitlisted(self, game):
        """ Retrieve the current number of players waitlisted for the specified game """
        players = game.players.filter(standby=True)
        return players.count()

    class Meta:
        model = Game
        fields = ['id', 'dm_name', 'name', 'module', 'realm', 'variant', 'description', 'players', 'number_of_players', 'number_of_waitlisted', 'max_players', 'level_min', 'level_max', 'warnings', 'channel', 'streaming', 'datetime_release', 'datetime_open_release', 'datetime', 'length']


class GameCreationSerialiser(ModelSerializer):
    class Meta:
        model = Game
        fields = ['dm', 'name', 'module', 'realm', 'variant', 'description', 'max_players', 'level_min', 'level_max', 'warnings', 'streaming', 'datetime_release', 'datetime_open_release', 'datetime', 'length', 'ready']
