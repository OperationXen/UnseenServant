from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models.user import CustomUser as User
from .models.game import Game, DM
from .models.players import Rank, Player, Strike, Ban

admin.site.register(User, UserAdmin)

admin.site.register(Game)
admin.site.register(DM)

admin.site.register(Strike)
admin.site.register(Ban)
admin.site.register(Player)
admin.site.register(Rank)
