from discord import Intents
from discord.ext import commands

from discord_bot.schedule.embeds import EmbedController

# Required to get permissions to query channel memberships
intents = Intents.default()
intents.message_content = True
intents.members = True

bot = commands.Bot(intents=intents)

# Register cogs
bot.add_cog(EmbedController)
