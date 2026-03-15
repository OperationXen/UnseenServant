from discord.ext import tasks, commands

from discord_bot.logs import logger as log
from discord_bot.bot import bot


class EmbedController(commands.Cog):
    def __init__(self):
        """initialisation function"""
        self.worker.start()
        log.info("[+] Started service: Embed auto update worker")

    def cog_unload(self):
        """cleanup function"""
        self.worker.cancel()

    @tasks.loop(seconds=60)
    async def worker(self):
        try:
            for view in bot.persistent_views:
                await view.update_message()
        except Exception as e:
            log.error(f"[!] An unhandled exception has occured in the EmbedManager Loop: " + str(e))

    @worker.before_loop
    async def before_loop_start(self):
        await self.bot.wait_until_ready()
