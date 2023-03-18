from django.urls import path

from discord_login.views import discord_login, discord_auth_done


urlpatterns = [
    path('', discord_login, name='discord_home'),
    path('login/', discord_login, name='discord_login'),
    path('done/', discord_auth_done, name='discord_auth_done')
    # path('logout/', discord_logout, name='logout'),
]
