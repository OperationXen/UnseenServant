from config.settings import DISCORD_TOKEN, DISCORD_GUILDS
from config.settings import DISCORD_GAME_LOG_CHANNEL

from discord_bot.logs import logger as log
from discord_bot.bot import bot
from discord_bot.commands import *
from discord_bot.schedule.games import GamesPoster
from discord_bot.schedule.channels.manager import ChannelController
from discord_bot.schedule.channels.membership import ChannelMembershipController
from discord_bot.schedule.embeds import EmbedController

from discord_bot.moonseacodex.messages import handle_game_log_posted


def start_bot():
    """bot startup routine"""
    bot.run(DISCORD_TOKEN)


@bot.event
async def on_ready():
    log.info(f"[-] {bot.user.name} has connected to discord")
    log.info("Starting automated services")

    try:
        guild_id = int(DISCORD_GUILDS[0])
        discord_bot.core.guild = bot.get_guild(guild_id)

        discord_bot.core.game_controller = GamesPoster()
        log.info("[+] Started service: Games poster")
        discord_bot.core.channel_controller = ChannelController(discord_bot.core.guild)
        log.info("[+] Started service: Channel creation/deletion")
        discord_bot.core.channel_membership_controller = ChannelMembershipController(discord_bot.core.guild)
        log.info("[+] Started service: Channel membership manager")
        discord_bot.core.embed_controller = EmbedController()
        log.info("[+] Started service: Embed auto update worker")
    except IndexError:
        log.info("Unable to find the specified guild")


@bot.event
async def on_message(message):
    """Handle messages sent to the bot"""
    # Ignore messages from the bot itself
    if message.author == bot.user:
        return

    try:
        if message.channel.name.startswith(DISCORD_GAME_LOG_CHANNEL):
            await handle_game_log_posted(message)
    except Exception as e:
        pass
