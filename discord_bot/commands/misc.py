from discord_bot.bot import bot
from discord_bot.components.misc import HelpMessageEmbed
from config.settings import DISCORD_GUILDS

@bot.slash_command(guild_ids=DISCORD_GUILDS, description='Display help message')
async def help(ctx):
    """ Display help message """
    message_embed = HelpMessageEmbed()
    await ctx.respond(embed=message_embed, ephemeral=True)
