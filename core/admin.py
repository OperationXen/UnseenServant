from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models.admin import CustomUser as User, DM
from .models.game import Game
from .models.channel import GameChannel
from .models.players import BonusCredit, Rank, Player, Strike, Ban

admin.site.register(User, UserAdmin)

admin.site.register(DM)
admin.site.register(Game)
admin.site.register(GameChannel)

admin.site.register(Player)
admin.site.register(BonusCredit)
admin.site.register(Rank)
admin.site.register(Strike)
admin.site.register(Ban)
