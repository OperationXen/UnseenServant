from asgiref.sync import sync_to_async
from discord.ext import tasks

from discordbot.bot import bot
from discordbot.utils.messaging import get_channel_by_name, send_channel_message
from core.utils.games import get_outstanding_games

class GamesPoster():
    channel = None

    def __init__(self):
        self.check_and_post_games.start()
        
    @tasks.loop(seconds=10)
    async def check_and_post_games(self):
        print("Checking for games")
        if not self.channel:
            self.channel = get_channel_by_name('bot-test-channel')

        outstanding_games = await get_outstanding_games()
        for game in outstanding_games:
            message = f"New game ready for signups! {game.name}"
            await send_channel_message(message, self.channel)

scheduled_poster = GamesPoster()
