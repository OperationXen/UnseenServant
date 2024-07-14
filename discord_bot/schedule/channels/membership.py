from typing import List
import traceback

from discord import Member as DiscordMember
from discord.ext import tasks
from discord.errors import NotFound

from discord_bot.logs import logger as log
from core.models.channel import GameChannel, GameChannelMember

from core.utils.channels import async_get_all_current_game_channels, async_get_game_channel_members
from discord_bot.utils.channel import async_get_channel_current_members, refresh_discord_channel
from discord_bot.utils.channel import async_remove_discord_id_from_channel, async_add_member_to_channel
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

    def get_discord_user_id_list(self, members: List[DiscordMember]) -> List[str]:
        member_ids = set(map(lambda x: str(x.id), members))
        return member_ids

    def get_game_channel_member_id_list(self, gcm: List[GameChannelMember]) -> List[str]:
        """get a list of all game channel member ids"""
        gcm_ids = set(map(lambda x: x.user.discord_id, gcm))
        return gcm_ids

    ###### Member adding logic ######
    def get_missing_users(self, actual: List[DiscordMember], gcm: List[GameChannelMember]) -> List[GameChannelMember]:
        """Get all users which should be added to the channel"""
        missing = []
        member_ids = self.get_discord_user_id_list(actual)

        for game_channel_member in gcm:
            if game_channel_member.user.discord_id in member_ids:
                continue
            missing.append(game_channel_member)
        return missing

    async def async_add_missing_members_to_channel(self, actual, expected, discord_channel):
        """Identify players missing from the channel and add them"""
        to_add = self.get_missing_users(actual, expected)

        log.debug(f"[.] Adding {len(to_add)} users to channel {discord_channel.name}")
        for missing_user in to_add:
            if await async_add_member_to_channel(missing_user, discord_channel):
                log.debug(f"[.] added user {missing_user.user.discord_name} to channel {discord_channel.name}")
                await async_game_channel_tag_promoted_discord_id(discord_channel, missing_user)
            else:
                log.warn(f"[!] Failed to add user {missing_user.user.discord_name} to channel {discord_channel.name}")

    ###### Member removal logic ######
    def get_excess_users(self, actual: List[DiscordMember], gcm: List[GameChannelMember]) -> List[GameChannelMember]:
        """Get all users which should be removed from the channel"""
        excess = []
        gcm_ids = self.get_game_channel_member_id_list(gcm)
        for discord_member in actual:
            if discord_member in gcm_ids:
                continue
            excess.append(discord_member)
        return excess

    async def async_remove_excess_members_from_channel(self, actual, expected, discord_channel):
        """Identify any members who need to be removed and remove them"""
        to_remove = self.get_excess_users(actual, expected)

        log.debug(f"[.] Removing {len(to_remove)} users from channel {discord_channel.name}")
        for excess_user in to_remove:
            if await async_remove_discord_id_from_channel(excess_user.id, discord_channel):
                log.info(f"[-] Removed user {excess_user.name} from channel {discord_channel.name}")
            else:
                log.warn(f"[!] Failed to remove {excess_user.name} from channel {discord_channel.name}")

    ###### Member update logic ######
    def get_updated_users(self, actual, expected) -> List[GameChannelMember]:
        """Get all users who have outdated channel permissions"""
        users_pending_update = []
        try:
            for discord_member in actual:
                expected_user = [x for x in expected if x.user.discord_id == str(discord_member.id)][0]
                print(expected_user)
                # insert check for permissions
                users_pending_update.append(expected_user)
        except IndexError:
            pass  # user is not expected to be in channel
        return users_pending_update

    async def async_apply_permission_updates(self, actual, expected, discord_channel):
        to_update = self.get_updated_users(actual, expected)
        pass

    # ######################################################################## #
    async def sync_channel_membership(self, game_channel: GameChannel):
        """Update the channel membership to match that expected in the database state"""
        try:
            discord_channel = await refresh_discord_channel(game_channel)
        except NotFound:
            log.warn(f"[!] Unable to retrieve a channel from discord for {game_channel.name}")
            return

        expected_members = await async_get_game_channel_members(game_channel)
        actual_members = await async_get_channel_current_members(discord_channel)

        await self.async_remove_excess_members_from_channel(actual_members, expected_members, discord_channel)
        await self.async_add_missing_members_to_channel(actual_members, expected_members, discord_channel)
        await self.async_apply_permission_updates(actual_members, expected_members, discord_channel)

    # ################################### Worker loop definition ################################## #
    @tasks.loop(seconds=30)
    async def channel_event_loop(self):
        try:
            if not self.initialised:
                log.info("[++] Starting up the Channel Membership Controller loop")
                self.initialised = True

            channels = await async_get_all_current_game_channels()
            for channel in channels:
                await self.sync_channel_membership(channel)
        except Exception as e:
            log.error(f"[!] An unhandled exception has occured in the Channel Membership Controller Loop: " + str(e))
            log.debug(f"{traceback.format_exc()}")
            self.initialised = False
