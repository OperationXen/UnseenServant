from django.utils import timezone
from discord import Embed, Colour


class BaseEmbed(Embed):
    """ Baseclass for banner type embed objects """
    def __init__(self, title = None, colour=Colour.dark_grey()):
        """ Create an empty embed """
        if not title:
            title = 'Announcement'
        super().__init__(title=title, colour=colour)


class CalendarSummaryBanner(BaseEmbed):
    """ An embed to top calendar channel posts about upcoming """
    def __init__(self, title = None, description = None):
        """ Create the embed """
        if not title:
            title = 'Upcoming games'
        super().__init__(title=title, colour = Colour.dark_purple())
        if description:
            self.description = description


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
