from django.db import models


class Character(models.Model):
    """Character instances"""

    dnd_beyond_link = models.URLField(blank=True, help_text="Link to character sheet on D&D Beyond")
    forewarning = models.TextField(blank=True, help_text="Warnings of shenanigans, or notes for DM")
