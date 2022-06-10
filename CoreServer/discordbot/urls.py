from django.urls import path

from discordbot.views import BotView

urlpatterns = [path('start', BotView.as_view()),]