from django.db import models

from core.models import CustomUser, Game


class Credit(models.Model):
    """Defines a game credit, used to purchase slots in games"""

    owner = models.ForeignKey(CustomUser, related_name="credits", on_delete=models.CASCADE)
    game = models.ForeignKey(Game, null=True, blank=True, related_name="game_credits", on_delete=models.SET_NULL)
    origin = models.CharField(max_length=32, blank=True, null=True)
    purpose = models.CharField(max_length=32, blank=True, null=True)
    locked = models.BooleanField(default=False, help_text="User prevented from modifying")

    datetime_earned = models.DateTimeField(auto_now_add=True, blank=True, null=True)
    datetime_spent = models.DateTimeField(blank=True, null=True)
    datetime_expiry = models.DateTimeField(blank=True, null=True, help_text="When the credit becomes unspendable")

    def __str__(self):
        return f"Credit - {self.owner.discord_name}{' (unspent)' if self.available else ''}"

    class Meta:
        indexes = [
            models.Index(fields=["owner", "game", "locked", "origin", "purpose", "datetime_expiry", "datetime_spent"])
        ]


class PrioritySeat(models.Model):
    pass


class LotteryTicket(models.Model):
    pass
