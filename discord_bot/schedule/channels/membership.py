from typing import List

from django.contrib.auth import get_user_model
from discord.ext import tasks
from discord.utils import get as discord_get
from discord.member import Member

from discord_bot.logs import logger as log
from core.models.channel import GameChannel
from core.utils.games import async_get_dm, async_get_player_list
from core.utils.channels import async_get_all_current_game_channels, async_get_game_channel_members
from discord_bot.utils.channel import async_get_channel_current_members, get_discord_channel
from discord_bot.utils.channel import async_add_discord_ids_to_channel, async_remove_discord_ids_from_channel

UserModel = get_user_model()


class ChannelMembershipController:
    """Manager class for syncing channel membership to database state"""

    initialised = False

    def __init__(self, guild):
        """initialisation function"""
        self.guild = guild
        self.channel_event_loop.start()

    def get_discord_ids(self, data: Member | UserModel) -> List[str]:
        """Return a list of discord IDs"""
        discord_ids = []

        for element in data:
            if type(element) == Member:
                discord_ids.append(str(element.id))
            if type(element) == UserModel and element.discord_id:
                discord_ids.append(element.discord_id)
        return discord_ids

    async def sync_channel_membership(self, game_channel: GameChannel):
        """Update the channel membership to match that expected in the database state"""
        discord_channel = get_discord_channel(game_channel)

        expected_members = await async_get_game_channel_members(game_channel)
        expected_member_ids = self.get_discord_ids(expected_members)
        actual_members = await async_get_channel_current_members(discord_channel)
        actual_member_ids = self.get_discord_ids(actual_members)

        missing_users = list(set(expected_member_ids) - set(actual_member_ids))
        if missing_users:
            log.debug(f"[-] Channel {game_channel.name} is missing players {missing_users}")
            num_added = await async_add_discord_ids_to_channel(missing_users, discord_channel)
            log.debug(f"[-] added {num_added} users to channel")

        excess_users = list(set(actual_member_ids) - set(expected_member_ids))
        if excess_users:
            log.debug(f"[-] Channel {game_channel.name} has excess players {missing_users}")
            num_removed = await async_remove_discord_ids_from_channel(excess_users, discord_channel)
            log.debug(f"[-] removed {num_removed} users from channel")

    @tasks.loop(seconds=42)
    async def channel_event_loop(self):
        if not self.initialised:
            log.debug("[++] Starting up the Channel Membership Controller loop")
            self.initialised = True

        channels = await async_get_all_current_game_channels()
        for channel in channels:
            await self.sync_channel_membership(channel)
