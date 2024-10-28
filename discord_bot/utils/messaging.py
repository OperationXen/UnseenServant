from discord import Forbidden, User as DiscordUser

from discord_bot.bot import bot
from discord_bot.logs import logger as log


async def async_send_dm(message: str, discord_user: DiscordUser = None, discord_id: int = None):
    if not discord_user:
        discord_user = await bot.get_or_fetch_user(discord_id)
    try:
        return await discord_user.send(message)
    except Forbidden:
        return None
    except Exception as e:
        log.error(f"[!] Unexpected error sending DM to user {discord_user.name}: {e}")


def get_channel_by_name(channel_name):
    """Attempt to retieve a channel by a name"""
    for channel in bot.get_all_channels():
        if channel.name == channel_name:
            return channel
    return None


async def async_get_guild_channel(channel_name):
    """retrieve a specific named channel for a given guild"""
    for guild in await bot.fetch_guilds().flatten():
        for channel in await guild.fetch_channels():
            if channel.name == channel_name:
                print(f"Found channel named {channel_name}")
                return channel


def message_should_be_purged(m):
    """Helper function to determine if a message should be removed or not"""
    if m.author == bot.user:
        return True
    if m.content and m.content[0] == "!":
        return True
    return False


async def async_remove_existing_messages(channels):
    """Find and remove all previously posted bot messages - not the cleanest solution, but a first pass"""
    for channel in bot.get_all_channels():
        if channel.name in channels:
            await channel.purge(check=message_should_be_purged, limit=5000)


async def async_get_bot_game_postings(channel):
    """Retrieve a list of message objects posted by this bot in this channel"""
    messages = await channel.history().flatten()
    messages = filter(lambda message: message.author == bot.user, messages)
    return list(messages)
