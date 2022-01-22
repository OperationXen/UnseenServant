from threading import Thread, Lock
from config.settings import DISCORD_TOKEN, DEFAULT_CHANNEL_NAME, PRIORITY_CHANNEL_NAME

from discordbot.bot import bot
from discordbot.commands import *
from discordbot.schedule.games import *
from discordbot.utils.messaging import remove_existing_messages
from discordbot.utils.announce import repost_all_current_games

mutex = Lock()

def run_bot():
    while True:
        mutex.acquire()
        bot.run(DISCORD_TOKEN)
        print("Bot died... performing some light necromancy")
        mutex.release()

def start_bot():
    bot_thread = Thread(target=run_bot, daemon=True)
    bot_thread.start()

@bot.event
async def on_ready():
    print(f"{bot.user.name} has connected to discord")

    print("Creating Game Controller")
    game_controller = GamesPoster()

### Django Stuff to run the bot within the Django context ###
urlpatterns = []
start_bot()


