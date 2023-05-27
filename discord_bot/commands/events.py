import discord_bot.core
from discord_bot.bot import bot
from config.settings import DISCORD_GUILDS, EVENT_PLAYER_ROLE_NAME
from discord_bot.logs import logger as log

from discord_bot.utils.roles import get_role_by_name


@bot.slash_command(guild_ids=DISCORD_GUILDS, description="Join an event")
async def join_event(ctx):
    """Sign the player up for the upcoming event"""
    await ctx.response.defer(ephemeral=True)
    log.info(f"{ctx.author.name} used command /join_event")

    event_role = get_role_by_name(discord_bot.core.guild.roles, EVENT_PLAYER_ROLE_NAME)
    if not event_role:
        log.error(f"Could not find a role named '{EVENT_PLAYER_ROLE_NAME}'")
        await ctx.followup.send(f"Unable to find the appropriate role")
    success = await ctx.author.add_roles([event_role], reason="User signed up for event")
    if not success:
        log.error(f"Could not grant role {event_role.name} to user {ctx.author.name}")
        await ctx.followup.send(f"Unable to grant role")
    log.info(f"Role {event_role.name} granted to user {ctx.author.name}")
    await ctx.followup.send(f"Added you to the event")


@bot.slash_command(guild_ids=DISCORD_GUILDS, description="Join an event")
async def leave_event(ctx):
    """Remove the player from the upcoming event"""
    await ctx.response.defer(ephemeral=True)
    log.info(f"{ctx.author.name} used command /leave_event")

    return await ctx.followup.send(f"Removed you from the event")
