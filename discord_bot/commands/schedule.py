from typing import List

from discord import Option
from discord.ext.commands import has_any_role

from config.settings import DISCORD_GUILDS, DISCORD_ADMIN_ROLES
from discord_bot.bot import bot
from discord_bot.logs import logger as log

from core.utils.games import async_get_upcoming_games, async_get_dm, calc_game_tier
from discord_bot.utils.time import discord_time
from discord_bot.utils.messaging import DISCORD_MAX_MESSAGE_LENGTH


async def send_escaped_message(ctx, message):
    """ Send the message to the identified interaction context, using backticks to escape it """
    try:
        return await ctx.respond(f"```{message}```")
    except Exception as e:
        log.error(f"[!] Unable to send message are reply to context, message length was {len(message)}")
        await ctx.respond(f"I had a problem sending the response.")


@bot.slash_command(guild_ids=DISCORD_GUILDS, description="Generate a schedule of res DM games")
@has_any_role(*DISCORD_ADMIN_ROLES)
async def generate_schedule(ctx, days: Option(int, "Number of days", required=False) = 90):
    log.debug(f"[/] [/generate_schedule] used by User [{ctx.author.name}]")
    await ctx.defer(ephemeral=True)
    outstanding_games = await async_get_upcoming_games(days)

    schedule: List[str] = []
    if not outstanding_games:
        return await ctx.respond(f"No upcoming unannounced games in the next 90 days")
    
    for game in outstanding_games:
        # Should be done as a prefetch really - possible optimisation
        dm = await async_get_dm(game)
        hammer_time = discord_time(game.datetime)
        tier = calc_game_tier(game)

        if game.duration:
            schedule.append(f"{hammer_time} **Tier {tier}** {game.module} {game.name} ({dm.name}) {game.duration} hours\n")
        else:
            schedule.append(f"{hammer_time} **Tier {tier}** {game.module} {game.name} ({dm.name})\n")
    
    message = ""
    for line in schedule:
        # Check line does not make the message too long before adding it
        if len(message) + len(line) < DISCORD_MAX_MESSAGE_LENGTH - 10:
            message = message + line
        else:
            # send what we have build so far, start a new message with the line that would have overspilled
            await send_escaped_message(ctx, message)
            message = line

    if len(message):
        await send_escaped_message(ctx, message)
