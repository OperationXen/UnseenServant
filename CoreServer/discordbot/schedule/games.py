from discord.ext import tasks

from config.settings import DEFAULT_CHANNEL_NAME, PRIORITY_CHANNEL_NAME
from discordbot.utils.messaging import get_channel_by_name
from discordbot.components.banners import GameAnnounceBanner
from discordbot.components.games import GameDetailEmbed, GameControlView
from core.utils.games import get_outstanding_games, set_game_announced

class GamesPoster():
    channel_general = None
    channel_priority = None

    def __init__(self):
        self.check_and_post_games.start()
        
    @tasks.loop(seconds=10)
    async def check_and_post_games(self):
        print("Checking for games")
        if not self.channel_general:
            self.channel_general = get_channel_by_name(DEFAULT_CHANNEL_NAME)
        if not self.channel_priority:
            self.channel_priority = get_channel_by_name(PRIORITY_CHANNEL_NAME)

        # get games for priority release
        outstanding_games = await get_outstanding_games(priority=True)
        await self.announce_games(outstanding_games, priority=True)

        # get games for general release
        outstanding_games = await get_outstanding_games(priority=False)
        await self.announce_games(outstanding_games, priority=False)
        
    async def announce_games(self, games, priority=False):
        for game in games:
            await self.do_game_announcement(game, priority)
            await set_game_announced(game)

    async def do_game_announcement(self, game, priority):
        """ Build an announcement """
        if priority:
            channel = self.channel_priority
        else:
            channel = self.channel_general

        embeds = [GameAnnounceBanner(priority=priority)]
        details_embed = GameDetailEmbed(game)
        await details_embed.build()
        embeds.append(details_embed)

        control_view = GameControlView(game)
        if channel:
            control_view.message = await channel.send(embeds=embeds, view=control_view)


scheduled_poster = GamesPoster()
