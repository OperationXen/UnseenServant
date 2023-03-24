from rest_framework.serializers import ModelSerializer

from core.models import Rank


class RankSerialiser(ModelSerializer):
    """ Serialise a player (basic, no personal data) """
    class Meta:
        model = Rank
        fields = ['name', 'discord_id', 'priority', 'max_games', 'patreon']
