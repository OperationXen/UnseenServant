from typing import List

from discord import PermissionOverwrite
from discord import User as DiscordUser
from discord.channel import TextChannel
from discord.member import Member

from discord_bot.bot import bot
from discord_bot.logs import logger as log
from config.settings import CHANNEL_SEND_PINGS
from core.models import Game, GameChannel, GameChannelMember
from core.utils.announcements import async_get_player_announce_text
from core.utils.user import async_get_user_by_discord_id
from core.utils.channels import async_add_user_to_game_channel, async_remove_user_from_game_channel
from core.utils.channels import async_get_game_channel_for_game
from discord_bot.utils.games import async_get_game_from_message


def get_discord_channel(game_channel: GameChannel) -> TextChannel:
    """Get a discord channel object represent by an Unseen Servant GameChannel object"""
    channel = bot.get_channel(int(game_channel.discord_id))
    return channel


async def refresh_discord_channel(game_channel: GameChannel) -> TextChannel:
    channel = await bot.fetch_channel(int(game_channel.discord_id))
    return channel


async def get_discord_user_by_id(discord_id):
    """retrieve a discord user object from the server by its ID"""
    try:
        if not discord_id:
            return None

        discord_user = await bot.fetch_user(discord_id)
        return discord_user
    except Exception as e:
        return None


async def async_get_channel_for_game(game: Game) -> TextChannel:
    """Get a discord object for a given game"""
    try:
        game_channel = await async_get_game_channel_for_game(game)
        channel = get_discord_channel(game_channel)
        return channel
    except Exception as e:
        log.debug(f"Unable to get an active channel for {game.name}")
    return None


async def async_get_game_for_channel(channel: TextChannel) -> Game | None:
    """Given a discord channel, attempt to derive which game it represents"""
    try:
        message = await async_get_channel_first_message(channel)
        game = await async_get_game_from_message(message)
        if game:
            return game
        return None
    except Exception as e:
        return None


def async_get_mustering_view_for_game(game: Game):
    """Given a game object, check its mustering channel and retrieve the view attached to the mustering embed"""
    for view in bot.persistent_views:
        view_name = str(type(view))
        if "MusteringView" in view_name and view.game == game:
            return view
    return None


async def async_update_mustering_embed(game: Game):
    """Refresh a mustering embed for a specific game"""
    try:
        view = async_get_mustering_view_for_game(game)
        if view:
            return await view.update_message()
    except Exception as e:
        log.debug(f"Error when updating associated muster embed")
    return False


async def async_notify_game_channel(game: Game, message: str):
    """Send a notification to a game channel"""
    channel = await async_get_channel_for_game(game)
    if channel:
        log.debug(f"[.] Sending message to channel [{channel.name}]: {message}")
        status = await channel.send(message)
        return status
    else:
        log.debug(f"Cannot send message to non-existant channel")
    return False


# ################################################################ #
async def async_game_channel_tag_promoted_discord_id(game_channel: GameChannel, member: GameChannelMember):
    """Tag a user in a channel from a player object"""
    discord_user = await get_discord_user_by_id(member.user.discord_id)
    if CHANNEL_SEND_PINGS:
        user_text = discord_user.mention
    else:
        user_text = discord_user.display_name
    text = await async_get_player_announce_text(member.user, user_text)
    message = await game_channel.send(text)
    return message


async def async_game_channel_tag_removed_discord_user(game_channel: GameChannel, discord_user: DiscordUser):
    """Send a message to the game channel notifying the DM that a player has dropped"""
    try:
        text = f"{discord_user.display_name} left the channel"
        message = await game_channel.send(text)
        return message
    except Exception as e:
        log.error(f"[!] Exception occured whilst tagging a removed user: ${e}")
        return False


# ################################################################ #
async def async_channel_add_discord_user(
    channel: TextChannel,
    user: DiscordUser,
    read_messages=True,
    send_messages=True,
    read_message_history=True,
    use_slash_commands=True,
    manage_messages=False,
):
    """Give a specific user permission to view and post in the channel for an upcoming game"""

    # start by creating an override object that describes the desired permissions
    overwrite = PermissionOverwrite()
    overwrite.read_messages = read_messages
    overwrite.read_message_history = read_message_history
    overwrite.send_messages = send_messages
    overwrite.use_slash_commands = use_slash_commands
    overwrite.manage_messages = manage_messages

    # then apply the overwrites to the user
    try:
        await channel.set_permissions(user, overwrite=overwrite)
        return True
    except Exception as e:
        log.error(f"[!] Exception occured adding discord user {user.display_name} to channel")
    return False


async def async_channel_remove_discord_user(channel: TextChannel, user: DiscordUser):
    """Remove a specific player from a game channel"""
    try:
        log.debug(f"[-] Removing discord user [{user.display_name}] from channel [{channel.name}]")
        await channel.set_permissions(
            user,
            read_messages=False,
            send_messages=False,
            read_message_history=False,
            use_slash_commands=False,
            manage_messages=False,
        )
        return True
    except Exception as e:
        log.error(f"[!] Exception occured removing discord user {user.display_name} from channel")
    return False


# ################################################################ #
async def async_create_channel_hidden(guild, parent, name, topic):
    """creates a channel which can only be seen and used by the bot"""
    log.info(f"Creating new game mustering channel: {name} ")
    overwrites = {
        guild.default_role: PermissionOverwrite(read_messages=False),
        guild.me: PermissionOverwrite(read_messages=True, send_messages=True, read_message_history=True),
    }
    channel = await guild.create_text_channel(category=parent, name=name, topic=topic, overwrites=overwrites)
    return channel


async def async_get_all_game_channels_for_guild(guild):
    """List all existing game channels"""
    all_channels = guild.by_category()
    for channel_group in all_channels:
        if channel_group[0] != None and channel_group[0].name == "Your Upcoming Games":
            return channel_group[1]
    return []


async def async_get_channel_first_message(channel: TextChannel):
    """Get the first message in a specified channel"""
    try:
        message = await channel.history(limit=1, oldest_first=True).flatten()
        return message[0]
    except Exception as e:
        log.error(f"[!] Exception occured finding first message in channel {channel.name}")
        return None


# async def async_remove_all_channel_members(channel: TextChannel) -> bool:
#     """Remove all the members of a specific channel"""
#     for member in channel.members:
#         if not member.bot:
#             log.info(f"Removed [{member.name}] from [{channel.name}]")
#             await channel.set_permissions(
#                 member, read_messages=False, send_messages=False, read_message_history=False, use_slash_commands=False
#             )
#     return True


# ################################################################################### #
#                          Channel permissions utilities                              #
# ################################################################################### #
def get_channel_overwrites_for_discord_user(channel: TextChannel, discord_user: DiscordUser) -> PermissionOverwrite:
    """Get the permissions for a channel member within a specific channel"""
    permissions = channel.overwrites_for(discord_user)
    return permissions


def set_channel_overwrites_for_discord_user(channel: TextChannel, discord_user: DiscordUser):
    """Sets permission overrides on a channel for a user"""
    pass


def get_channel_current_members(channel: TextChannel) -> List[Member]:
    """utility function to get all members in a private channel"""
    current_members = []

    for member in channel.overwrites:
        if type(member) != Member or member.bot:
            pass
        else:
            permissions = get_channel_overwrites_for_discord_user(channel, member)
            if permissions.read_messages:
                # construct a new dict type that contains the info we're interested in
                current_members.append(
                    {
                        "id": member.id,
                        "display_name": member.display_name,
                        "read_messages": permissions.read_messages,
                        "read_message_history": permissions.read_message_history,
                        "send_messages": permissions.send_messages,
                        "use_slash_commands": permissions.use_slash_commands,
                        "manage_messages": permissions.manage_messages,
                    }
                )
    return current_members


async def async_get_channel_current_members(channel: TextChannel):
    """Get all the current members of the channel on discord"""
    members = get_channel_current_members(channel)
    return members


# ################################################################################### #
#               Channel Membership Manager add / remove functions                     #
# ################################################################################### #
async def async_add_discord_member_to_game_channel(discord_user: DiscordUser, game_channel: GameChannel) -> bool:
    """Get the user from a discord user and add it as a channel member"""
    try:
        user = await async_get_user_by_discord_id(discord_user.id)
        added = await async_add_user_to_game_channel(user, game_channel)
        return added
    except Exception as e:
        return False


async def async_remove_discord_member_from_game_channel(discord_user: DiscordUser, game_channel: GameChannel) -> bool:
    """get the user from a discord user and remove it as a channel member"""
    try:
        user = await async_get_user_by_discord_id(discord_user.id)
        removed = await async_remove_user_from_game_channel(user, game_channel)
        return removed
    except Exception as e:
        return False


async def async_add_member_to_channel(membership: GameChannelMember, channel: TextChannel) -> int:
    """Add the users refered to by their discord ID in the list to the channel"""
    discord_user = await get_discord_user_by_id(membership.user.discord_id)
    if not discord_user:
        log.error(f"[!] Unable to find discord user id for: {membership.user.username}")
        return False

    success = await async_channel_add_discord_user(
        channel,
        discord_user,
        membership.read_messages,
        membership.send_messages,
        membership.read_message_history,
        membership.use_slash_commands,
        membership.manage_messages,
    )
    return success


async def async_remove_discord_id_from_channel(discord_id, channel: TextChannel) -> bool:
    """remove a user from a channel by their discord ID"""
    discord_user = await get_discord_user_by_id(discord_id)
    if discord_user:
        success = await async_channel_remove_discord_user(channel, discord_user)
        return success
    else:
        log.error(f"[!] Unable to find discord user id: {discord_id}")
        return False
