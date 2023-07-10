from django.db import models

from core.models import CustomUser, Game


class Credit(models.Model):
    """Defines a game credit, used to purchase slots in games"""

    owner = models.ForeignKey(CustomUser, related_name="credits", on_delete=models.CASCADE)
    game = models.ForeignKey(Game, related_name="game_credits", on_delete=models.SET_NULL)
    origin = models.CharField(max_length=32, blank=True, null=True)
    datetime_earned = models.DateTimeField(auto_now_add=True, blank=True, null=True)
    datetime_spent = models.DateTimeField(blank=True, null=True)
    datetime_refundable = models.DateTimeField(blank=True, null=True)
    datetime_expiry = models.DateTimeField(blank=True, null=True, help_text="When the credit becomes unspendable")

    locked = models.BooleanField(default=False, help_text="User prevented from modifying")
    active = models.BooleanField(default=True, help_text="Credit is being used for something")
    expired = models.BooleanField(default=True, help_text="Credit is not usable")

    def __str__(self):
        return f"Credit - {self.owner.discord_name}{' (unspent)' if self.available else ''}"

    class Meta:
        indexes = [models.Index(fields=["owner", "game", "datetime_expiry", "available", "locked"])]
