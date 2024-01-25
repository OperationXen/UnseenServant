from rest_framework.serializers import ModelSerializer, ReadOnlyField, SerializerMethodField

from core.models import DM, CustomUser


class DMSerialiser(ModelSerializer):
    """Serialise a DM"""

    class Meta:
        model = DM
        fields = "__all__"
