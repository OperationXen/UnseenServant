from rest_framework.serializers import ModelSerializer, ReadOnlyField, SerializerMethodField

from core.models import DMBanList


class DMBanListSerialiser(ModelSerializer):
    """Serialise a DM"""

    user_name = ReadOnlyField(source="user.discord_name")
    dm_name = ReadOnlyField(source="dm.discord_name")

    class Meta:
        model = DMBanList
        fields = ["datetime_created", "description", "user_name", "dm_name"]
