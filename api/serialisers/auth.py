from rest_framework.serializers import ModelSerializer

from django.contrib.auth import get_user_model

UserModel = get_user_model()

class UserSerialiser(ModelSerializer):

    class Meta:
        model = UserModel
        fields = ['username', 'email', 'discord_name']
