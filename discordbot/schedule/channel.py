from discord.ext import tasks
from discord.utils import get

from discordbot.logs import logger as log
from discordbot.utils.time import get_hammertime
from core.utils.games import get_dm, get_player_list
from core.utils.channels import get_game_channels_pending_reminder, get_game_channels_pending_warning
from core.utils.channels import get_game_channels_pending_creation, set_game_channel_created
from discordbot.components.channels import MusteringBanner, MusteringView


class ChannelManager:
    """Manager class for performing channel based functions"""
    initialised = False
    guild = None
    parent_category = None

    def __init__(self, guild):
        """ initialisation function """
        self.guild = guild
        self.channel_event_loop.start()

    async def get_topic_text(self, game):
        """ build the game channel topic header """
        dm = await get_dm(game)
        topic_text = "This thread is for mustering for the following game: "
        topic_text+= f"{game.module} ({game.name}) | DMed by {dm.name} | "
        topic_text+= f"Game is scheduled for {get_hammertime(game.datetime)}"
        return topic_text

    async def send_banner_message(self, channel, game):
        """send the welcome banner"""
        control_view = MusteringView(game)
        banner = MusteringBanner(game)
        await banner.build()

        players = await get_player_list(game)
        ping_text = 'Players: '
        ping_text+= ','.join(f"<@{p.discord_id}>" for p in players if not p.standby)
        message = await channel.send(ping_text, embed=banner, view=control_view)
        control_view.message = message

    async def check_and_create_channels(self):
        """ Get outstanding channels needed and create them where missing """
        pending_games = await get_game_channels_pending_creation()
        for upcoming_game in pending_games:
            log.info(f"Creating channel for game: {upcoming_game.name}")
            channel_name = upcoming_game.datetime.strftime("%Y%m%d-") + upcoming_game.module            
            channel_topic = await self.get_topic_text(upcoming_game)
            channel = await self.guild.create_text_channel(category=self.parent_category, name=channel_name, topic=channel_topic)
            if channel:
                game_channel = await set_game_channel_created(upcoming_game, channel.id, channel.jump_url, channel.name)
                await self.send_banner_message(channel, upcoming_game)

    @tasks.loop(seconds=10)
    async def channel_event_loop(self):
        if not self.initialised:
            log.debug('Starting up the channel watcher')
            self.parent_category = get(self.guild.categories, name="Upcoming Games")
            self.initialised = True

        await self.check_and_create_channels()
