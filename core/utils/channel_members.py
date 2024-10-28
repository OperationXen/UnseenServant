from typing import List
from asgiref.sync import sync_to_async

from core.models.channel import GameChannel, GameChannelMember


# ################################################################################ #
def get_game_channel_members(channel: GameChannel) -> List[GameChannelMember]:
    """Get a list of all of the channel member objects for a given game channel"""
    queryset = channel.members.through.objects.filter(channel=channel).prefetch_related("user")
    result = list(queryset)  # force evaluation before leaving this sync context
    return result


@sync_to_async
def async_get_game_channel_members(channel: GameChannel) -> List[GameChannelMember]:
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
        try:
            channel.members.add(player.user, through_defaults={"send_messages": False, "use_slash_commands": False})
        except Exception as e:
            print(e)
    # commit changes to DB
    channel.save()


def add_party_to_channel(channel: GameChannel):
    """add the party members to the channel with default (read / write) permissions"""
    game = channel.game

    party = game.players.filter(standby=False)
    for player in party:
        try:
            channel.members.add(player.user)
        except Exception as e:
            print(e)
    # commit changes to DB
    channel.save()


# ################################################################################ #
def set_default_channel_membership(channel: GameChannel, add_waitlist_read_only=False) -> bool:
    """Attempt to set a default membership list for a game channel"""
    try:
        game = channel.game
        # clear the channel members
        channel.members.set([])
        # add the DM with the additional "manage messages" permission
        channel.members.add(game.dm.user, through_defaults={"manage_messages": True})

        # get the waitlist and set them as read-only users
        if add_waitlist_read_only:
            add_waitlist_to_channel(channel)
        add_party_to_channel(channel)

        return True
    except Exception as e:
        return False


@sync_to_async
def async_set_default_channel_membership(channel: GameChannel, add_waitlist_read_only) -> bool:
    """async wrapper to allow channel membership to be set from discord bot"""
    return set_default_channel_membership(channel, bool(add_waitlist_read_only))
