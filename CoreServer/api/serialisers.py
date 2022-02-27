from rest_framework.serializers import ModelSerializer, ReadOnlyField, SerializerMethodField

from core.models import Game

class GameSerialiser(ModelSerializer):
    """ Serialiser for game objects """
    id = ReadOnlyField(source='pk')
    number_of_players = SerializerMethodField()

    def get_number_of_players(self, game):
        """ Retrieve the current number of players for a given game """
        return 42

    class Meta:
        model = Game
        fields = ['id', 'dm', 'name', 'module', 'realm', 'variant', 'description', 'number_of_players', 'max_players', 'level_min', 'level_max', 'warnings', 'channel', 'streaming', 'datetime_release', 'datetime_open_release', 'datetime', 'length']
