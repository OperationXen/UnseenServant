from discord import Intents
from discord.ext import commands

# Required to get permissions to query channel memberships
intents = Intents.default()
intents.message_content = True
intents.members = True

bot = commands.Bot(intents=intents)
