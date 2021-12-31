from discord.ext import commands
from config.settings import DISCORD_GUILDS as guilds

bot = commands.Bot(command_prefix='!')

@bot.event
async def on_ready():
    print(f"{bot.user.name} has connected to discord")

