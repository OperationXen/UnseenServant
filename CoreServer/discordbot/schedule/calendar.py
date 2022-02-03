from datetime import timedelta
from discord.ext import tasks
from django.utils import timezone

from discordbot.logs import logger as log
from config.settings import CALENDAR_CHANNEL_NAME
from discordbot.utils.messaging import get_channel_by_name, get_bot_game_postings
from discordbot.utils.time import discord_date
from discordbot.components.games import GameSummaryEmbed
from discordbot.components.banners import CalendarSummaryBanner
from core.utils.games import get_upcoming_games


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
            self.initialised = True

    async def post_upcoming_games(self, days=30, games = []):
        """ Post a summary for each game occuring in the next N days """
        log.info("Updating upcoming games calendar post")
        start = timezone.now()
        end = start + timedelta(days=days)
        games = await get_upcoming_games(days=days, released=True)

        title = f"[{len(games)}] Upcoming games in the next [{days}] days;"
        title = title + f"\n\t{discord_date(start)} to {discord_date(end)}"
        embeds = [CalendarSummaryBanner(title=title)]
        for game in games:
            summary = GameSummaryEmbed(game)
            await summary.build()
            embeds.append(summary)
        
        if self.messages:
            await self.messages[0].edit("", embeds=embeds)
        else:
            await self.channel_calendar.send("", embeds=embeds)

    @tasks.loop(seconds=30)
    async def check_and_update_calendar(self):
        """ post a summary of the next N days of games """
        if not self.initialised:
            await self.startup()

        self.messages = await get_bot_game_postings(self.channel_calendar)
        await self.post_upcoming_games()
