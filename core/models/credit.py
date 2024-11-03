from django.contrib.contenttypes.fields import GenericForeignKey
from django.contrib.contenttypes.models import ContentType
from django.db import models

from core.models import CustomUser


class Credit(models.Model):
    """Defines a game credit, used to purchase slots in games"""

    owner = models.ForeignKey(CustomUser, related_name="credits", on_delete=models.CASCADE)
    origin = models.CharField(max_length=32, blank=True, null=True)
    locked = models.BooleanField(default=False, help_text="User prevented from modifying")

    target_type = models.ForeignKey(ContentType, on_delete=models.CASCADE, default=None, blank=True)
    target_id = models.PositiveIntegerField(blank=True, null=True)
    target = GenericForeignKey("target_type", "target_id")

    datetime_earned = models.DateTimeField(auto_now_add=True, blank=True, null=True)
    datetime_spent = models.DateTimeField(blank=True, null=True)
    datetime_expiry = models.DateTimeField(blank=True, null=True, help_text="When the credit becomes unspendable")

    def __str__(self):
        return f"Credit - {self.owner.discord_name}{' (unspent)' if self.available else ''}"

    class Meta:
        indexes = [models.Index(fields=["owner", "locked", "origin", "datetime_expiry", "datetime_spent"])]


class PrioritySeat(models.Model):
    pass
