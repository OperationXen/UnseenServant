from typing import List

from discord.ext import tasks
from discord.errors import NotFound

from discord_bot.logs import logger as log
from core.models.channel import GameChannel
from core.models.auth import CustomUser

from core.utils.channels import async_get_all_current_game_channels, async_get_game_channel_members
from discord_bot.utils.channel import async_get_channel_current_members, refresh_discord_channel
from discord_bot.utils.channel import async_remove_discord_ids_from_channel, async_add_member_to_channel
from discord_bot.utils.channel import (
    async_game_channel_tag_promoted_discord_id,
    async_game_channel_tag_removed_discord_id,
)


class ChannelMembershipController:
    """Manager class for syncing channel membership to database state"""

    initialised = False

    def __init__(self, guild):
        """initialisation function"""
        self.guild = guild
        self.channel_event_loop.start()

    async def sync_channel_membership(self, game_channel: GameChannel):
        """Update the channel membership to match that expected in the database state"""
        try:
            discord_channel = await refresh_discord_channel(game_channel)
        except NotFound:
            log.warn(f"Unable to retrieve a channel from discord for {game_channel.name}")
            return

        # await async_set_default_channel_membership(game_channel)
        expected_members = await async_get_game_channel_members(game_channel)
        expected_member_ids = set(map(lambda x: x.user.discord_id, expected_members))
        actual_members = await async_get_channel_current_members(discord_channel)
        actual_member_ids = set(map(lambda x: str(x.id), actual_members))
        missing_users = list(
            filter(
                lambda m: m.user.discord_id != None and not actual_member_ids.__contains__(m.user.discord_id),
                expected_members,
            )
        )
        missing_user_ids = list(map(lambda m: m.user.id, missing_users))

        if len(missing_user_ids):
            for missing_user in missing_users:
                if await async_add_member_to_channel(missing_user, discord_channel):
                    await async_game_channel_tag_promoted_discord_id(discord_channel, missing_user)
                    log.debug(f"[.] added user to channel")
                else:
                    log.debug(f"[.] failed to add user to channel")

        excess_user_ids = list(actual_member_ids - expected_member_ids)
        if excess_user_ids:
            log.debug(f"[.] Channel {game_channel.name} has excess players {excess_user_ids}")
            num_removed = await async_remove_discord_ids_from_channel(excess_user_ids, discord_channel)
            log.debug(f"[.] removed {num_removed} users from channel")

    @tasks.loop(seconds=30)
    async def channel_event_loop(self):
        try:
            if not self.initialised:
                log.debug("[++] Starting up the Channel Membership Controller loop")
                self.initialised = True

            channels = await async_get_all_current_game_channels()
            for channel in channels:
                await self.sync_channel_membership(channel)
        except Exception as e:
            log.error(f"[!] An unhandled exception has occured in the Channel Membership Controller Loop: " + str(e))
            self.initialised = False
