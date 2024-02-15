from rest_framework.serializers import ModelSerializer, SerializerMethodField

from core.models import CustomUser
from core.serialisers import RankSerialiser
from core.utils.user import get_user_credit_balance, get_user_credits_max


class UserSerialiser(ModelSerializer):
    ranks = RankSerialiser(many=True, read_only=True)

    class Meta:
        model = CustomUser
        fields = ["username", "email", "discord_id", "discord_name", "ranks"]


class UserDetailsSerialiser(ModelSerializer):
    """Get user details"""

    def get_credit_max(self, user: CustomUser):
        return get_user_credits_max(user)

    def get_credit_available(self, user: CustomUser):
        return get_user_credit_balance(user)

    ranks = RankSerialiser(many=True, read_only=True)
    credit_max = SerializerMethodField()
    credit_available = SerializerMethodField()

    class Meta:
        model = CustomUser
        fields = ["username", "email", "discord_name", "credit_max", "credit_available", "ranks"]
