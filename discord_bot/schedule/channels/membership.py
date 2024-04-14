from typing import List

from discord.ext import tasks
from discord.member import Member
from discord.errors import NotFound

from discord_bot.logs import logger as log
from core.models.channel import GameChannel
from core.models.auth import CustomUser

from core.utils.channels import async_set_default_channel_membership
from core.utils.channels import async_get_all_current_game_channels, async_get_game_channel_members
from discord_bot.utils.channel import async_get_channel_current_members, refresh_discord_channel
from discord_bot.utils.channel import async_add_discord_ids_to_channel, async_remove_discord_ids_from_channel


class ChannelMembershipController:
    """Manager class for syncing channel membership to database state"""

    initialised = False

    def __init__(self, guild):
        """initialisation function"""
        self.guild = guild
        self.channel_event_loop.start()

    def get_discord_ids(self, data: Member | CustomUser) -> List[str]:
        """Return a list of discord IDs"""
        discord_ids = []

        for element in data:
            if type(element) == Member:
                discord_ids.append(str(element.id))
            if type(element) == CustomUser and element.discord_id:
                discord_ids.append(element.discord_id)
        return discord_ids

    async def sync_channel_membership(self, game_channel: GameChannel):
        """Update the channel membership to match that expected in the database state"""
        try:
            discord_channel = await refresh_discord_channel(game_channel)
        except NotFound:
            return

        await async_set_default_channel_membership(game_channel)
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
            log.debug(f"[-] Channel {game_channel.name} has excess players {excess_users}")
            num_removed = await async_remove_discord_ids_from_channel(excess_users, discord_channel)
            log.debug(f"[-] removed {num_removed} users from channel")

    @tasks.loop(seconds=60)
    async def channel_event_loop(self):
        try:
            if not self.initialised:
                log.debug("[++] Starting up the Channel Membership Controller loop")
                self.initialised = True

            channels = await async_get_all_current_game_channels()
            for channel in channels:
                await self.sync_channel_membership(channel)
        except Exception as e:
            log.error(f"[!] An unhandled exception has occured in the Channel Membership Controller Loop")
            self.initialised = False
