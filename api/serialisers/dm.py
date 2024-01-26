from rest_framework.serializers import ModelSerializer, ReadOnlyField, SerializerMethodField

from core.models import DM, CustomUser


class DMSerialiser(ModelSerializer):
    """Serialise a DM"""

    id = ReadOnlyField(source="pk")
    discord_id = ReadOnlyField(source="user.discord_id")
    discord_name = ReadOnlyField(source="user.discord_name")

    class Meta:
        model = DM
        fields = ["id", "name", "discord_id", "discord_name", "description", "rules_text", "muster_text"]
