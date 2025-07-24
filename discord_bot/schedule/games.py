from discord.ext import tasks

from discord_bot.logs import logger as log
from config.settings import DEFAULT_CHANNEL_NAME, PRIORITY_CHANNEL_NAME
from discord_bot.utils.messaging import get_channel_by_name, async_get_bot_game_postings
from discord_bot.components.games import GameDetailEmbed, GameControlView
from discord_bot.utils.games import async_get_game_from_message, get_game_id_from_message
from discord_bot.utils.views import add_persistent_view
from core.utils.games import get_outstanding_games, async_check_game_expired


class GamesPoster:
    current_games = {}

    channel_general = None
    channel_priority = None

    def __init__(self):
        """initialisation function"""
        # self.refresh_state.start()
        self.check_and_post_games.start()

    async def fetch_message_state(self):
        """Perform async initialisation"""
        try:
            self.current_games = {}
            await self.get_bot_channels()
            await self.recover_message_state()
        except Exception as e:
            log.error(f"[!] Exception in fetch_message_state: {e}")

    async def get_bot_channels(self):
        """Attempt to get the specified channels"""
        self.channel_general = get_channel_by_name(DEFAULT_CHANNEL_NAME)
        self.channel_priority = get_channel_by_name(PRIORITY_CHANNEL_NAME)

    async def recover_message_state(self):
        """Pull game postings from posting history and reconstruct a game/message status from it"""
        for channel in [self.channel_priority, self.channel_general]:
            messages = await async_get_bot_game_postings(channel)
            for message in messages:
                game = await async_get_game_from_message(message)
                if not game:
                    game_id = get_game_id_from_message(message)
                    log.info(f"[-] Removing orphaned message (No matching game) for game ID {game_id}")
                    await message.delete()
                    continue

                # Rebuild view handlers
                control_view = GameControlView(game)
                control_view.message = message
                self.current_games[game.pk] = {
                    "game": game,
                    "message": message,
                    "view": control_view,
                    "channel": channel,
                    "jump_url": message.jump_url,
                }
                add_persistent_view(control_view)

    async def do_game_announcement(self, game, channel):
        """Build an announcement"""
        embeds = []
        details_embed = GameDetailEmbed(game)
        await details_embed.build()
        embeds.append(details_embed)

        control_view = GameControlView(game)
        if channel:
            message = await channel.send(embeds=embeds, view=control_view)
            control_view.message = message
            self.current_games[game.pk] = {
                "game": game,
                "message": message,
                "view": control_view,
                "channel": channel,
                "jump_url": message.jump_url,
            }
            add_persistent_view(control_view)

    def get_jump_url(self, game):
        """Retrieve a link to the posted game details"""
        if game.id not in self.current_games:
            return None
        return self.current_games[game.id]["jump_url"]

    def is_game_posted(self, game):
        """determine if the game referenced is currently posted, and in which channel"""
        if game.id not in self.current_games:
            return None
        return self.current_games[game.id]["channel"]

    async def remove_specific_game(self, game_id):
        """Pull a specific game ID from the game state and delete the associated message"""
        announcement = self.current_games[game_id]
        await announcement["message"].delete()
        self.current_games.pop(game_id)

    async def post_outstanding_games(self):
        """Create new messages for any games that need to be announced"""
        for priority in [False, True]:
            try:
                for game in await get_outstanding_games(priority):
                    channel = self.is_game_posted(game)
                    if not channel:
                        log.info(f"[-] Announcing new game: {game.name}")
                        await self.do_game_announcement(
                            game, self.channel_priority if priority else self.channel_general
                        )
                    elif not priority and channel == self.channel_priority:
                        log.info(f"[-] Moving game announcement to general")
                        await self.remove_specific_game(game.id)
                        await self.do_game_announcement(game, self.channel_general)
            except Exception as e:
                log.error(f"[!] Exception caught in post_outstanding_games: {e.__class__}")

    async def remove_stale_games(self):
        """Go through existing games and check for anything stale"""
        for key in self.current_games:
            try:
                log.debug(f"Getting announcement")
                announcement = self.current_games[key]
                log.debug(f"Checking game expiration")
                if await async_check_game_expired(announcement["game"]):
                    log.debug(f"Game expired")
                    log.info(f"Deleteing expired game - {announcement['game']}")
                    await announcement["message"].delete()
                    self.current_games.pop(key)
                    break  # because we've modified current_games we can't continue to iterate on it
                log.debug(f"Done")
            except Exception as e:
                log.error(f"[!] Exception caught in remove_stale_games: {e.__class__}, key = {key}")

    @tasks.loop(seconds=30)
    async def check_and_post_games(self):
        try:
            await self.fetch_message_state()

            if self.channel_priority and self.channel_general:
                await self.remove_stale_games()
                await self.post_outstanding_games()
        except Exception as e:
            log.error(f"[!] An unhandled exception has occured in the GamesPoster Loop: " + str(e))
