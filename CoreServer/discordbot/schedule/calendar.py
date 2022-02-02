from discord.ext import tasks
from django.utils import timezone

from discordbot.logs import logger as log
from config.settings import CALENDAR_CHANNEL_NAME
from discordbot.utils.messaging import get_channel_by_name, get_bot_game_postings
from discordbot.components.games import GameSummaryEmbed
from core.utils.games import get_outstanding_games

class GamesCalendarManager():
    initialised = False
    channel_calendar = None
    messages = []

    def __init__(self):
        """ initialisation function """
        log.info("Starting GamesCalendarManager")
        self.check_and_update_calendar.start()
    
    async def startup(self):
        """ Asyncronous startup routine """
        log.info("GamesCalendarManager initialising in background")
        self.channel_calendar = get_channel_by_name(CALENDAR_CHANNEL_NAME)
        if self.channel_calendar:
            self.messages = await get_bot_game_postings(self.channel_calendar)
            self.initialised = True

    def check_update_required(self):
        """ Check to see if the messages were posted today or not """
        today = timezone.now().date()
        if not self.messages:
            return True

        header = self.messages[0]
        if today > header.created_at.date():
            print("pew")
            return True
        return False

    async def remove_messages(self):
        """ Remove all messages """
        for message in self.messages:
            await message.delete()

    async def post_upcoming_games(self, days=30):
        """ Post a summary for each game occuring in the next N days """
        log.info("Updating upcoming games calendar post")

    @tasks.loop(seconds=10)
    async def check_and_update_calendar(self):
        """ post a summary of the next N days of games """
        if not self.initialised:
            await self.startup()

        if not self.check_update_required():
            return

        if self.channel_calendar:
            await self.remove_messages()
            await self.post_upcoming_games()