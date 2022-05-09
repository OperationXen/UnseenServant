from discord.ext import tasks

from discordbot.logs import logger as log


class ChannelManager:
    """Manager class for performing channel based functions"""

    @tasks.loop(seconds=10)
    async def check_and_post_games(self):
        if not self.initialised:
            await self.startup()
