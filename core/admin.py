from django.contrib import admin

from core.models import DM, CustomUser, Game, GameChannel, GameChannelMember
from core.models import BonusCredit, Rank, Player, Strike, Ban, Announcement

admin.site.register(CustomUser)
admin.site.register(DM)
admin.site.register(Game)
admin.site.register(GameChannel)
admin.site.register(GameChannelMember)

admin.site.register(Player)
admin.site.register(BonusCredit)
admin.site.register(Rank)
admin.site.register(Strike)
admin.site.register(Ban)
admin.site.register(Announcement)
