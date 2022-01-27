import discord
from discord.commands import Option, has_any_role

from discordbot.bot import bot
from config.settings import DISCORD_GUILDS, DISCORD_ADMIN_ROLES

@bot.slash_command(guild_ids=DISCORD_GUILDS, description='Resummon the Unseen Servant')
@has_any_role(*DISCORD_ADMIN_ROLES)
async def resummon(ctx):
    """ Restart bot """
    await ctx.respond(f"Light the candles, start the chants - it's all getting a bit existential around here...", delete_after=10)
    bot.clear()