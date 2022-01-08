from discord import Embed, Colour, ButtonStyle
from discord.ui import View, button

from discordbot.utils.format import generate_calendar_message
from core.utils.games import get_player_list, get_wait_list, get_dm
from core.utils.games import add_player_to_game, drop_from_game
from core.utils.time import discord_time, discord_countdown

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
