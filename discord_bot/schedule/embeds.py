from discord.ext import tasks, commands

from discord_bot.logs import logger as log


class EmbedController(commands.Cog):
    bot = None

    def __init__(self, bot):
        """initialisation function"""
        self.bot = bot
        self.worker.start()

    def cog_unload(self):
        """cleanup function"""
        self.worker.cancel()

    @tasks.loop(seconds=60)
    async def worker(self):
        try:
            for view in self.bot.persistent_views:
                await view.update_message()
        except Exception as e:
            log.error(f"[!] An unhandled exception has occured in the EmbedManager Loop: " + str(e))

    @worker.before_loop
    async def before_loop_start(self):
        await self.bot.wait_until_ready()
        log.info("[+] Starting service: Embed auto update worker")
