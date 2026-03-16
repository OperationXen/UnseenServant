from config.settings import DISCORD_TOKEN, DISCORD_GUILDS
from config.settings import DISCORD_GAME_LOG_CHANNEL

from discord_bot.logs import logger as log
from discord_bot.bot import bot
from discord_bot.commands import *

from discord_bot.schedule.games import GamesPoster
from discord_bot.schedule.embeds import EmbedController
from discord_bot.schedule.channels.controller import ChannelController
from discord_bot.schedule.channels.membership import ChannelMembershipController

from discord_bot.moonseacodex.messages import handle_game_log_posted


guild_id = int(DISCORD_GUILDS[0])

# Register cogs
bot.add_cog(GamesPoster(bot))
bot.add_cog(EmbedController(bot))
bot.add_cog(ChannelMembershipController(bot))
bot.add_cog(ChannelController(bot, guild_id))


def start_bot():
    """bot startup routine"""
    bot.run(DISCORD_TOKEN)


@bot.event
async def on_ready():
    log.info(f"[-] {bot.user.name} has connected to discord")


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
