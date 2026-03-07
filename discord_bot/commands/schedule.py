from discord import Option
from discord.ext.commands import has_any_role

from config.settings import DISCORD_GUILDS, DISCORD_ADMIN_ROLES
from discord_bot.bot import bot
from discord_bot.logs import logger as log

from core.utils.games import async_get_upcoming_games, async_get_dm, calc_game_tier
from discord_bot.utils.time import discord_time


@bot.slash_command(guild_ids=DISCORD_GUILDS, description="Generate a schedule of res DM games")
@has_any_role(*DISCORD_ADMIN_ROLES)
async def generate_schedule(ctx, days: Option(int, "Number of days", required=False) = 90):
    log.debug(f"[/] [/generate_schedule] used by User [{ctx.author.name}]")
    await ctx.defer(ephemeral=True)
    outstanding_games = await async_get_upcoming_games(days)

    message = ""
    if not outstanding_games:
        return await ctx.respond(f"No upcoming unannounced games in the next 90 days")
    
    for game in outstanding_games:
        # Should be done as a prefetch really - possible optimisation
        dm = await async_get_dm(game)
        hammer_time = discord_time(game.datetime)
        tier = calc_game_tier(game)

        if game.duration:
            message = message + f"{hammer_time} **Tier {tier}** {game.module} {game.name} ({dm.name}) {game.duration} hours\n"
        else:
            message = message + f"{hammer_time} **Tier {tier}** {game.module} {game.name} ({dm.name})\n"
    # Escape the return as code so that it can be copy / pasted
    return await ctx.respond(f"```{message}```")
