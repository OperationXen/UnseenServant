import asyncio
from threading import Thread

from discordbot.bot import bot

async def _send_async(discord_id, message):
    user = await bot.get_or_fetch_user(discord_id)
    print("User")

def _send_dm(discord_id, message):
    """ send a message to a specified discord ID """
    print("Sending DM")
    asyncio.run(_send_async(discord_id, message))

def send_dm(discord_id, message):
    dm_thread = Thread(target = _send_dm, args= (discord_id, message))
    dm_thread.run()
