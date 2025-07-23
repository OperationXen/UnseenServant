from django.utils import timezone
import django.contrib.admin as admin

from core.models import Game

class PlayerAdmin(admin.ModelAdmin):
    list_display = ["game__name", "user__discord_name", "standby", "waitlist"]

    fieldsets = [
        (
            "Player Information",
            {
                "fields": [
                    "game",
                    "user",
                ]
            },
        ),
        (
            "Waitlist Config", 
            {
                "fields": [
                    ("standby",
                    "waitlist")
                    ]
            }
        )
    ]

    def formfield_for_foreignkey(self, db_field, request, **kwargs):
        if db_field.name == "game":

            now = timezone.now()
            yesterday = now - timezone.timedelta(days=1)

            kwargs["queryset"] = Game.objects.filter(ready=True).filter(datetime__gte=yesterday).order_by("datetime")
        return super().formfield_for_foreignkey(db_field, request, **kwargs)