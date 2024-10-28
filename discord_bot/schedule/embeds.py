from discord.ext import tasks

from discord_bot.logs import logger as log
from discord_bot.bot import bot


class EmbedController:
    def __init__(self):
        """initialisation function"""
        self.embed_refresh_loop.start()

    @tasks.loop(seconds=30)
    async def embed_refresh_loop(self):
        try:
            for view in bot.persistent_views:
                await view.update_message()
        except Exception as e:
            log.error(f"[!] An unhandled exception has occured in the EmbedManager Loop: " + str(e))
