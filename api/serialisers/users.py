from rest_framework.serializers import ModelSerializer, SerializerMethodField

from django.contrib.auth import get_user_model

from core.serialisers import RankSerialiser
from core.utils.user import get_user_max_credit, get_user_available_credit

UserModel = get_user_model()


class UserSerialiser(ModelSerializer):
    ranks = RankSerialiser(many=True, read_only=True)

    class Meta:
        model = UserModel
        fields = ["username", "email", "discord_name", "ranks"]


class UserDetailsSerialiser(ModelSerializer):
    """Get user details"""

    def get_credit_max(self, user: UserModel):
        return get_user_max_credit(user)

    def get_credit_available(self, user: UserModel):
        return get_user_available_credit(user)

    ranks = RankSerialiser(many=True, read_only=True)
    credit_max = SerializerMethodField()
    credit_available = SerializerMethodField()

    class Meta:
        model = UserModel
        fields = ["username", "email", "discord_name", "credit_max", "credit_available", "ranks"]
