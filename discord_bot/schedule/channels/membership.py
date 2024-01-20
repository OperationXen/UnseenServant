from discord.ext import tasks
from discord.utils import get as discord_get

from discord_bot.logs import logger as log
from core.models.channel import GameChannel
from core.utils.games import async_get_dm, async_get_player_list
from core.utils.channels import async_get_all_current_game_channels, async_get_game_channel_members
from discord_bot.utils.channel import async_channel_add_player, async_get_channel_current_members, get_discord_channel


class ChannelMembershipController:
    """Manager class for syncing channel membership to database state"""

    initialised = False
    guild = None
    parent_category = None

    def __init__(self, guild):
        """initialisation function"""
        self.guild = guild
        self.channel_event_loop.start()

    async def sync_channel_membership(self, game_channel: GameChannel):
        """Update the channel membership to match that expected in the database state"""
        discord_channel = get_discord_channel(game_channel)

        expected_members = await async_get_game_channel_members(game_channel)
        actual_members = await async_get_channel_current_members(discord_channel)

        print(expected_members)
        print(actual_members)

    @tasks.loop(seconds=42)
    async def channel_event_loop(self):
        if not self.initialised:
            log.debug("[++] Starting up the Channel Membership Controller loop")
            self.parent_category = discord_get(self.guild.categories, name="Your Upcoming Games")
            self.initialised = True

        channels = await async_get_all_current_game_channels()
        for channel in channels:
            await self.sync_channel_membership(channel)
