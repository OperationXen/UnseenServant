from threading import Thread, Lock
from config.settings import DISCORD_TOKEN

from discordbot.bot import bot, game_controller
from discordbot.commands import *
from discordbot.schedule.games import *

def run_bot():
    while True:
        print("Starting bot...")
        bot.run(DISCORD_TOKEN)
        print("Bot died... performing some light necromancy")

def start_bot():
    bot_thread = Thread(target=run_bot, daemon=True)
    print("Creating dedicated bot thread")
    bot_thread.start()

@bot.event
async def on_ready():
    global game_controller
    print(f"{bot.user.name} has connected to discord")

    print("Creating Game Controller")
    game_controller = GamesPoster()

### Django Stuff to run the bot within the Django context ###
urlpatterns = []
start_bot()
