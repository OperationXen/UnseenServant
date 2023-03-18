from ast import Index
from config.settings import DISCORD_TOKEN, DISCORD_GUILDS

import discord_bot.core
from discord_bot.logs import logger as log
from discord_bot.bot import bot
from discord_bot.commands import *
from discord_bot.schedule.games import GamesPoster
from discord_bot.schedule.channel import ChannelManager


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
        roles = guild.roles
        print('\n'.join(f"{r.id} - {r.name}" for r in roles))

        discord_bot.core.game_controller = GamesPoster()
        discord_bot.core.channel_controller = ChannelManager(guild)
    except IndexError:
        log.info("Unable to find the specified guild")
    # discordbot.core.game_calendar_manager = GamesCalendarManager()
