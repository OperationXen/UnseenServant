from ast import Index
from config.settings import DISCORD_TOKEN, DISCORD_GUILDS

import discordbot.core
from discordbot.logs import logger as log
from discordbot.bot import bot
from discordbot.commands import *
from discordbot.schedule.games import GamesPoster
from discordbot.schedule.channel import ChannelManager


def start_bot():
    """ bot startup routine """
    bot.run(DISCORD_TOKEN)


@bot.event
async def on_ready():
    log.info(f"{bot.user.name} has connected to discord")
    log.info("Starting automated services")

    try:
        guild_id = int(DISCORD_GUILDS[0])
        guild = bot.get_guild(guild_id)
        discordbot.core.game_controller = GamesPoster()
        discordbot.core.channel_controller = ChannelManager(guild)
    except IndexError:
        log.info("Unable to find the specified guild")
    # discordbot.core.game_calendar_manager = GamesCalendarManager()
