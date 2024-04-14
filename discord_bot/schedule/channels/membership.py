from typing import List

from discord.ext import tasks
from discord.member import Member
from discord.channel import TextChannel

from discord_bot.logs import logger as log
from core.models.channel import GameChannel, ChannelMember

from core.utils.channels import async_set_default_channel_membership
from core.utils.channels import async_get_all_current_game_channels, async_get_game_channel_members
from discord_bot.utils.channel import async_get_channel_current_members, refresh_discord_channel
from discord_bot.utils.channel import async_set_discord_id_channel_overrides, async_remove_discord_ids_from_channel


class ChannelMembershipController:
    """Manager class for syncing channel membership to database state"""

    initialised = False

    def __init__(self, guild):
        """initialisation function"""
        self.guild = guild
        self.channel_event_loop.start()

    def get_discord_ids(self, data: Member | ChannelMember) -> List[str]:
        """Return a list of discord IDs"""
        discord_ids = []

        for element in data:
            if type(element) == Member:
                discord_ids.append(str(element.id))
            if type(element) == ChannelMember and element.user and element.user.discord_id:
                discord_ids.append(element.user.discord_id)
        return discord_ids

    async def update_discord_channel_member_overrides(
        self, channel: TextChannel, current: Member | None, expected: ChannelMember
    ) -> bool:
        """Check a discord channel member's overrides and update if incorrect"""
        if not current:
            await async_set_discord_id_channel_overrides(
                expected.user.discord_id, channel, expected.is_admin, expected.is_readonly
            )
        if expected.is_admin:
            pass

    async def sync_channel_membership(self, game_channel: GameChannel):
        """Update the channel membership to match that expected in the database state"""
        excess_users = []
        discord_channel = await refresh_discord_channel(game_channel)

        await async_set_default_channel_membership(game_channel)
        expected_channel_members = await async_get_game_channel_members(game_channel)
        permitted_discord_ids = self.get_discord_ids(expected_channel_members)
        actual_channel_members = await async_get_channel_current_members(discord_channel)

        # Identify and remove anyone who shouldn't be in the channel
        for discord_member in actual_channel_members:
            if discord_member.id not in permitted_discord_ids:
                excess_users.append(discord_member.id)
        if excess_users:
            log.debug(f"[-] Channel {game_channel.name} has excess players {excess_users}")
            await async_remove_discord_ids_from_channel(excess_users, discord_channel)

        # Add to overrides or update anyone who doesn't have the permissions they should
        for channel_member in expected_channel_members:
            discord_id = channel_member.user.discord_id
            discord_channel_member = self.get_discord_channel_member(actual_channel_members, discord_id)
            await self.update_discord_channel_member_overrides(discord_channel_member, channel_member)

    @tasks.loop(seconds=60)
    async def channel_event_loop(self):
        if not self.initialised:
            log.debug("[++] Starting up the Channel Membership Controller loop")
            self.initialised = True

        channels = await async_get_all_current_game_channels()
        for channel in channels:
            await self.sync_channel_membership(channel)
