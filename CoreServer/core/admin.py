from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models.user import CustomUser as User
from .models.game import Game, Ban, Player, DM

admin.site.register(User, UserAdmin)

admin.site.register(Game)
admin.site.register(Player)
admin.site.register(Ban)
admin.site.register(DM)
