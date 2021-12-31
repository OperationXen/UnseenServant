from threading import Thread, Lock
from config.settings import DISCORD_TOKEN

from discordbot.bot import bot
from discordbot.commands import *


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

urlpatterns = []
start_bot()