from django.db import models

from core.models.auth import CustomUser


class Announcement(models.Model):
    """Describes a player announcement to a channel"""

    users = models.ManyToManyField(
        CustomUser,
        related_name="announcements",
        blank=True,
        help_text="Users this announcement can be used for",
    )
    generic = models.BooleanField(default=False, help_text="Announcement is used as a global fallback")

    text = models.CharField(
        max_length=256,
        blank=False,
        null=False,
        default="%u joins the game",
        help_text="Text to use - %u marks where user name is inserted",
    )

    def __str__(self):
        if self.generic:
            return f"Generic: {self.text}"
        return f"Individual: {self.text}"

    class Meta:
        indexes = [models.Index(fields=["text"])]
