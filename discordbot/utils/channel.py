from discord import PermissionOverwrite
from discordbot import bot
from core.utils.channels import get_game_channel_for_game


async def get_channel_for_game(game):
    """Get a discord object for a given game"""
    try:
        game_channel = get_game_channel_for_game(game)
        channel = await bot.get_channel(game_channel.discord_id)
        return channel
    except:
        pass
    return None


async def notify_game_channel(game, message):
    """Send a notification to a game channel"""
    channel = get_channel_for_game(game, message)
    status = await channel.send(message)
    return status


async def game_channel_tag_promoted_player(game, player):
    """Send a message to the game channel notifying the player that they've been promoted"""
    message = f"<@{player.discord_id}> promoted from waitlist"
    message = await notify_game_channel(game, message)


async def game_channel_tag_removed_player(game, player):
    """Send a message to the game channel notifying the DM that a player has dropped"""
    message = f"{player.discord_name} dropped out"
    message = await notify_game_channel(game, message)


async def channel_add_player(discord_channel, player):
    """Give a specific player permission to view and post in the channel for an upcoming game"""
    discord_user = await bot.get_user(player.discord_id)
    discord_channel.set_permissions(discord_user, read_messages=True, send_messages=True)


async def channel_remove_player(channel, player):
    """Remove a specific player from a game channel"""
    discord_user = await bot.get_user(player.discord_id)
    channel.set_permissions(discord_user, read_messages=False, send_messages=False)


async def create_channel_hidden(guild, parent, name, topic):
    """creates a channel which can only be seen and used by the bot"""
    overwrites = {
        guild.default_role: PermissionOverwrite(read_messages=False, send_messages=False),
        guild.me: PermissionOverwrite(read_messages=True, send_messages=True),
    }
    channel = await guild.create_text_channel(category=parent, name=name, topic=topic, overwrites=overwrites)
    return channel
