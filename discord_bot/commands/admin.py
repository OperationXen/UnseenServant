from discord.ext.commands import has_any_role


import discord_bot.core
from discord_bot.bot import bot
from config.settings import DISCORD_GUILDS, DISCORD_ADMIN_ROLES


@bot.slash_command(
    guild_ids=DISCORD_GUILDS, description="Resummon the Unseen Servant - rebuilding posts from the arcane store"
)
@has_any_role(*DISCORD_ADMIN_ROLES)
async def resummon(ctx):
    """Force the bot to rebuild its internal state"""
    discord_bot.core.game_controller.initialised = False
    await ctx.respond(
        f"Redraw the summoning circle and light the candles - the Unseen Servant is invoked",
        ephemeral=True,
        delete_after=10,
    )
