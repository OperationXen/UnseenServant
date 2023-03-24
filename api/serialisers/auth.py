from rest_framework.serializers import ModelSerializer

from django.contrib.auth import get_user_model

from core.serialisers import RankSerialiser

UserModel = get_user_model()

class UserSerialiser(ModelSerializer):
    ranks = RankSerialiser(many=True, read_only=True)

    class Meta:
        model = UserModel
        fields = ['username', 'email', 'discord_name', 'ranks']
