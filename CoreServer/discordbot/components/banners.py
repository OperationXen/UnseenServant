from django.utils import timezone
from discord import Embed, Colour, ButtonStyle
from discord.ui import View, button

from discordbot.utils.format import generate_calendar_message
from core.utils.games import get_player_list, get_wait_list, get_dm
from core.utils.games import add_player_to_game, drop_from_game
from discordbot.utils.time import discord_time, discord_countdown


class BaseEmbed(Embed):
    """ Baseclass for banner type embed objects """

    def __init__(self, title = None, colour=Colour.dark_grey()):
        """ Create an empty embed """
        if not title:
            title = 'Announcement'
        super().__init__(title=title, colour=colour)


class GameAnnounceBanner(BaseEmbed):
    """ An embed to top posts about new game releases """

    def __init__(self, title = None, priority = False):
        """ Create the embed """
        if priority: 
            colour = Colour.dark_purple()
            default_title = 'Priority game now available for signup'
        else:
            colour = Colour.dark_green()
            default_title = 'New game available for general signup'
                        
        super().__init__(title=title or default_title, colour=colour)


class GameSummaryBanner(BaseEmbed):
    """ Embed to say how many games a player has upcoming """
    def __init__(self, games=None):
        now = timezone.now()
        if games:
            title = f"You are a player in [{games}] game"
            if games > 1:
                title = title + "s"
            colour = Colour.dark_purple()
        else:
            title = f"You are not queued for any games"
            colour = Colour.dark_red()
        
        super().__init__(title=title, colour=colour)


class DMSummaryBanner(BaseEmbed):
    """ Embed to summarise the games a DM is running """
    def __init__(self, games=None):
        now = timezone.now()
        if games:
            title = f"You are DMing [{games}] upcoming game"
            if games > 1:
                title = title + "s"
            colour = Colour.dark_blue()
        else:
            title = f"You are not DMing any upcoming games"
            colour = Colour.dark_red()

        super().__init__(title=title, colour=colour)


class WaitlistSummaryBanner(BaseEmbed):
    """ Embed to say how many games a player is waitlisted for """
    def __init__(self, games=None):
        now = timezone.now()
        if games:
            title = f"You are waitlisted for [{games}] game"
            if games > 1:
                title = title + "s"
            colour = Colour.dark_green()
        else:
            title = f"You are not on the waitlist for any upcoming games"
            colour = Colour.dark_red()
        
        super().__init__(title=title, colour=colour)
