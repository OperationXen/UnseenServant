from threading import Thread
from config.settings import DISCORD_TOKEN

import discordbot.core
from discordbot.logs import logger as log
from discordbot.bot import bot
from discordbot.commands import *
from discordbot.schedule.games import GamesPoster
from discordbot.schedule.calendar import GamesCalendarManager


def run_bot():
    while True:
        log.info("Starting bot...")
        bot.run(DISCORD_TOKEN)
        log.error("Bot died... performing some light necromancy")

def start_bot():
    log.info("Creating dedicated discordbot thread")
    bot_thread = Thread(target=run_bot, daemon=True)
    bot_thread.start()

@bot.event
async def on_ready():
    log.info(f"{bot.user.name} has connected to discord")

    log.info("Starting automated services")
    discordbot.core.game_controller = GamesPoster()
    discordbot.core.game_calendar_manager = GamesCalendarManager()
