from discord.ext import tasks

from config.settings import DEFAULT_CHANNEL_NAME, PRIORITY_CHANNEL_NAME
from discordbot.utils.messaging import get_channel_by_name, get_bot_game_postings, get_guild_channel
from discordbot.components.banners import GameAnnounceBanner
from discordbot.components.games import GameDetailEmbed, GameControlView
from discordbot.utils.games import get_game_id_from_message, add_persistent_view
from core.utils.games import get_outstanding_games, set_game_announced, get_game_by_id, check_game_expired

class GamesPoster():
    initialised = False
    messages_priority = []
    messages_general = []
    current_games = {}

    channel_general = None
    channel_priority = None

    def __init__(self):
        """ initialisation function """
        self.check_and_post_games.start()

    async def startup(self):
        """ Perform async """
        await self.get_bot_channels()
        await self.recover_message_state()
        self.initialised = True

    async def get_bot_channels(self):
        """ Attempt to get the specified channels """
        self.channel_general = get_channel_by_name(DEFAULT_CHANNEL_NAME)
        self.channel_priority = get_channel_by_name(PRIORITY_CHANNEL_NAME)

    async def recover_message_state(self):
        """ Pull game postings from posting history and reconstruct a game/message status from it """
        self.messages_priority = await get_bot_game_postings(self.channel_priority)
        self.messages_general = await get_bot_game_postings(self.channel_general)

        for message_group in [self.messages_general, self.messages_priority]:
            for message in message_group:
                game_id = get_game_id_from_message(message)
                game = await get_game_by_id(game_id)
                if not game:
                    await message.delete()
                    continue

                control_view = GameControlView(game)
                control_view.message = message
                self.current_games[game.pk] = {'game': game, 'message': message, 'view': control_view}
                add_persistent_view(control_view)

    async def announce_games(self, games, priority=False):
        for game in games:
            await self.do_game_announcement(game, priority)
            await set_game_announced(game)

    async def do_game_announcement(self, game, priority):
        """ Build an announcement """
        if priority:
            channel = self.channel_priority
        else:
            channel = self.channel_general

        embeds = []
        details_embed = GameDetailEmbed(game)
        await details_embed.build()
        embeds.append(details_embed)

        control_view = GameControlView(game)
        if channel:
            control_view.message = await channel.send(embeds=embeds, view=control_view)
            self.current_games[game.pk] = {'game': game, 'message': control_view.message, 'view': control_view}
            add_persistent_view(control_view)

    async def post_outstanding_games(self):
        """ Create new messages for any games that need to be announced """
        # get games for general release
        outstanding_games = await get_outstanding_games(priority=False)
        await self.announce_games(outstanding_games, priority=False)

        # get games for priority release
        outstanding_games = await get_outstanding_games(priority=True)
        await self.announce_games(outstanding_games, priority=True)

    async def remove_stale_games(self):
        """ Go through existing games and check for anything stale """
        for key in self.current_games:
            announcement = self.current_games[key]
            if await check_game_expired(announcement['game']):
                print(f"Deleteing expired game - {announcement['game']}")
                await announcement['message'].delete()
                self.current_games.pop(key)
                break
        
    @tasks.loop(seconds=10)
    async def check_and_post_games(self):
        if not self.initialised:
            await self.startup()

        if self.channel_priority and self.channel_general:
            await self.remove_stale_games()
            await self.post_outstanding_games()
