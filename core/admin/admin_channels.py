from django.utils import timezone
import django.contrib.admin as admin

from core.models import GameChannel, GameChannelMember

class ChannelAdmin(admin.ModelAdmin):
    list_display = ["game__name", "game__dm__user__discord_name", "status", "name", "link"]


class ChannelMemberAdmin(admin.ModelAdmin):
    list_display = ["channel__game__name", "user__discord_name"]
