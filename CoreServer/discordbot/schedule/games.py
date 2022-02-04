from discord.ext import tasks

from config.settings import DEFAULT_CHANNEL_NAME, PRIORITY_CHANNEL_NAME
from discordbot.utils.messaging import get_channel_by_name, get_bot_game_postings
from discordbot.components.games import GameDetailEmbed, GameControlView
from discordbot.utils.games import get_game_id_from_message, add_persistent_view
from core.utils.games import get_outstanding_games, get_game_by_id, check_game_expired

class GamesPoster():
    initialised = False
    current_games = {}

    channel_general = None
    channel_priority = None

    def __init__(self):
        """ initialisation function """
        self.refresh_state.start()
        self.check_and_post_games.start()

    async def startup(self):
        """ Perform async initialisation """
        self.current_games = {}
        await self.get_bot_channels()
        await self.recover_message_state()
        self.initialised = True

    async def get_bot_channels(self):
        """ Attempt to get the specified channels """
        self.channel_general = get_channel_by_name(DEFAULT_CHANNEL_NAME)
        self.channel_priority = get_channel_by_name(PRIORITY_CHANNEL_NAME)

    async def recover_message_state(self):
        """ Pull game postings from posting history and reconstruct a game/message status from it """
        print("Rebuilding internal message state")
        for channel in [self.channel_priority, self.channel_general]:
            messages = await get_bot_game_postings(channel)
            for message in messages:
                game_id = get_game_id_from_message(message)
                game = await get_game_by_id(game_id)
                if not game:
                    await message.delete()
                    continue

                # Rebuild view handlers
                control_view = GameControlView(game)
                control_view.message = message
                self.current_games[game.pk] = {'game': game, 'message': message, 'view': control_view, 'channel': channel, 'jump_url': message.jump_url}
                add_persistent_view(control_view)
            
    async def do_game_announcement(self, game, channel):
        """ Build an announcement """
        embeds = []
        details_embed = GameDetailEmbed(game)
        await details_embed.build()
        embeds.append(details_embed)

        control_view = GameControlView(game)
        if channel:
            message = await channel.send(embeds=embeds, view=control_view)
            control_view.message = message
            self.current_games[game.pk] = {'game': game, 'message': message, 'view': control_view, 'channel': channel, 'jump_url': message.jump_url}
            add_persistent_view(control_view)

    def get_jump_url(self, game):
        """ Retrieve a link to the posted game details """
        if game.id not in self.current_games:
            return None
        return self.current_games[game.id]['jump_url']

    def is_game_posted(self, game):
        """ determine if the game referenced is currently posted, and in which channel """
        if game.id not in self.current_games:
            return None
        return self.current_games[game.id]['channel']

    async def remove_specific_game(self, game_id):
        """ Pull a specific game ID from the game state and delete the associated message """
        announcement = self.current_games[game_id]
        await announcement['message'].delete()
        self.current_games.pop(game_id)

    async def post_outstanding_games(self):
        """ Create new messages for any games that need to be announced """
        for priority in [False, True]:
            for game in await get_outstanding_games(priority):
                channel = self.is_game_posted(game)
                if not channel:
                    print(f"Announcing new game: {game.name}")
                    await self.do_game_announcement(game, self.channel_priority if priority else self.channel_general)
                elif (not priority and channel == self.channel_priority):
                    print(f"Moving game announcement to general")
                    await self.remove_specific_game(game.id)
                    await self.do_game_announcement(game, self.channel_general)

    async def remove_stale_games(self):
        """ Go through existing games and check for anything stale """
        for key in self.current_games:
            announcement = self.current_games[key]
            if await check_game_expired(announcement['game']):
                print(f"Deleteing expired game - {announcement['game']}")
                await announcement['message'].delete()
                self.current_games.pop(key)
                break  # because we've modified current_games we can't continue to iterate on it
        
    @tasks.loop(seconds=10)
    async def check_and_post_games(self):
        if not self.initialised:
            await self.startup()

        if self.channel_priority and self.channel_general:
            await self.remove_stale_games()
            await self.post_outstanding_games()

    @tasks.loop(seconds=60)
    async def refresh_state(self):
        """ Force a refresh every minute """
        if self.initialised:
            self.initialised = False
