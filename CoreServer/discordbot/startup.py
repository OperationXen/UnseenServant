import asyncio
from threading import Thread
from config.settings import DISCORD_TOKEN

import discordbot.core
from discordbot.logs import logger as log
from discordbot.bot import bot
from discordbot.commands import *
from discordbot.schedule.games import GamesPoster
from discordbot.schedule.calendar import GamesCalendarManager


def start_bot():
    #log.info("Creating dedicated discordbot thread")
    #Thread(target=bot.run, args=(DISCORD_TOKEN,)).start()
    
    bot.run(DISCORD_TOKEN)
    #loop = asyncio.get_event_loop()
    #loop.create_task(bot.run(DISCORD_TOKEN))
    #Thread(target=loop.run_forever).start()

@bot.event
async def on_ready():
    log.info(f"{bot.user.name} has connected to discord")

    log.info("Starting automated services")
    discordbot.core.game_controller = GamesPoster()
    # discordbot.core.game_calendar_manager = GamesCalendarManager()
