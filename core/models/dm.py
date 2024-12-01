from django.utils import timezone
from django.db import models
from core.models.auth import CustomUser


class DM(models.Model):
    """Representation of a DM"""

    name = models.CharField(max_length=64, help_text="DM's chosen alias or handle")
    discord_id = models.CharField(null=True, blank=True, max_length=32, help_text="Discord ID of DM")
    discord_name = models.CharField(blank=True, max_length=32, help_text="Discord username")
    description = models.TextField(blank=True, null=True, help_text="Flavour text / details to show")
    rules_text = models.TextField(blank=True, null=True, max_length=1024, help_text="Any banned items / spells, etc")
    muster_text = models.TextField(
        blank=True, null=True, max_length=1024, help_text="Default text to add to mustering embed (option)"
    )
    user = models.ForeignKey(
        CustomUser, null=True, related_name="dm", on_delete=models.CASCADE, help_text="Associated user account"
    )
    banlist = models.ManyToManyField(CustomUser, related_name="banlisted_by", through="DMBanList")

    class Meta:
        verbose_name = "DM"
        verbose_name_plural = "DMs"
        indexes = [models.Index(fields=["name", "discord_id"])]

    def __str__(self):
        return f"{self.name}"


class DMBanList(models.Model):
    """A record that a specific user is banned from playing in games run by a DM"""

    datetime_created = models.DateTimeField(default=timezone.now)
    description = models.CharField(
        max_length=512, blank=True, null=True, help_text="Optional notes field for grudge holding"
    )

    dm = models.ForeignKey(DM, on_delete=models.CASCADE, related_name="banned_by")
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name="banlist")

    def __str__(self):
        return f"DM: {self.dm.user.discord_name} ban on {self.user.discord_name}"
