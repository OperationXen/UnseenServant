from asgiref.sync import sync_to_async

from core.models.channel import CustomUser, GameChannel, GameChannelMember
from discord_bot.logs import logger as log


# ################################################################################ #
def get_game_channel_members(channel: GameChannel) -> list[GameChannelMember]:
    """Get a list of all of the channel member objects for a given game channel"""
    queryset = channel.members.through.objects.filter(channel=channel).prefetch_related("user")
    result = list(queryset)  # force evaluation before leaving this sync context
    return result


@sync_to_async
def async_get_game_channel_members(channel: GameChannel) -> list[GameChannelMember]:
    """Given a game channel object retrieve its expected membership list"""
    return get_game_channel_members(channel)


# ################################################################################### #
###                          Channel user add / remove logic                        ###
# ################################################################################### #
def add_waitlist_to_channel(channel: GameChannel):
    """add waitlisted users to the channel as read only users"""

    game = channel.game

    waitlist = game.players.filter(standby=True)
    for player in waitlist:
        log.debug(f"[.] Adding waitlister {player.user.discord_name} to game channel (read only)")
        add_user_to_game_channel(player.user, channel, read_only=True)


def add_party_to_channel(channel: GameChannel):
    """add the party members to the channel with default (read / write) permissions"""
    game = channel.game

    party = game.players.filter(standby=False)
    for player in party:
        log.debug(f"[.] Adding player {player.user.discord_name} to game channel")
        add_user_to_game_channel(player.user, channel, read_only=False)


# ################################################################################ #
def set_default_channel_membership(channel: GameChannel, add_waitlist_read_only=False) -> bool:
    """Attempt to set a default membership list for a game channel"""
    log.debug(f"[.] Setting default channel membership for {channel.name}")
    try:
        game = channel.game
        # clear the channel members
        channel.members.set([])
        if game.dm.user:
            log.debug(f"[-] Adding DM {game.dm.user.discord_name} with channel admin permissions")
            add_user_to_game_channel(game.dm.user, channel, read_only=False, admin=True)

        # get the waitlist and set them as read-only users
        if add_waitlist_read_only:
            add_waitlist_to_channel(channel)
        add_party_to_channel(channel)

        return True
    except Exception as e:
        return False


@sync_to_async
def async_set_default_channel_membership(channel: GameChannel, add_waitlist_read_only: bool) -> bool:
    """async wrapper to allow channel membership to be set from discord bot"""
    return set_default_channel_membership(channel, bool(add_waitlist_read_only))


# ###################################################################################### #
def add_user_to_game_channel(user: CustomUser, channel: GameChannel, read_only=False, admin=False) -> bool:
    """Add a user to a specified game channel"""
    # Get a list of all current members and see if user is already there
    try:
        existing = GameChannelMember.objects.filter(channel=channel).get(user=user)
        existing.read_message_history = True
        existing.read_messages = True
        existing.send_messages = not read_only
        existing.use_slash_commands = not read_only
        existing.manage_messages = admin
        existing.pin_messages = admin
        existing.save()
        return True
    except GameChannelMember.DoesNotExist:
        pass

    # User isn't already in the channel, so we need to add them
    channel.members.add(
        user,
        through_defaults={
            "send_messages": not read_only,
            "use_slash_commands": not read_only,
            "manage_messages": admin,
            "pin_messages": admin,
        },
    )
    channel.save()
    return True


@sync_to_async
def async_add_user_to_game_channel(user: CustomUser, channel: GameChannel) -> bool:
    return add_user_to_game_channel(user, channel)


def remove_user_from_game_channel(user: CustomUser, channel: GameChannel) -> bool:
    """Remove a user from a game channel"""
    try:
        channel.members.remove(user)
        channel.save()
        return True
    except Exception:
        return False


@sync_to_async
def async_remove_user_from_game_channel(user: CustomUser, channel: GameChannel) -> bool:
    return remove_user_from_game_channel(user, channel)
