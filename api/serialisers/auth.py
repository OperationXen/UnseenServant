from rest_framework.serializers import ModelSerializer

from core.models import CustomUser


class UserSerialiser(ModelSerializer):

    class Meta:
        model = CustomUser
        fields = ['username', 'email', 'discord_name']
