from discord import Forbidden, HTTPException
from discord.ext.commands import has_any_role

from config.settings import DISCORD_GUILDS, EVENT_PLAYER_ROLE_NAME, DISCORD_ADMIN_ROLES
from config.settings import DISCORD_EVENT_COORDINATOR_ROLES, DISCORD_EVENT_USER_ROLES
import discord_bot.core
from discord_bot.bot import bot
from discord_bot.logs import logger as log
from discord_bot.utils.roles import get_role_by_name


@bot.slash_command(guild_ids=DISCORD_GUILDS, description="Join an event")
async def join_event(ctx):
    """Sign the player up for the upcoming event"""
    await ctx.response.defer(ephemeral=True)
    log.info(f"{ctx.author.name} used command /join_event")

    try:
        event_role = get_role_by_name(discord_bot.core.guild.roles, EVENT_PLAYER_ROLE_NAME)
        await ctx.author.add_roles(event_role, reason="User signed up for event")
    except ValueError:
        log.error(f"Could not find a role named '{EVENT_PLAYER_ROLE_NAME}'")
        await ctx.followup.send(f"Unable to find the appropriate role")
    except [Forbidden, HTTPException]:
        log.error(f"Could not grant role {event_role.name} to user {ctx.author.name}")
        await ctx.followup.send(f"Unable to grant role")

    log.info(f"Role {event_role.name} granted to user {ctx.author.name}")
    await ctx.followup.send(f"Added you to the event")


@bot.slash_command(guild_ids=DISCORD_GUILDS, description="Join an event")
async def leave_event(ctx):
    """Remove the player from the upcoming event"""
    await ctx.response.defer(ephemeral=True)
    log.info(f"{ctx.author.name} used command /leave_event")

    try:
        event_role = get_role_by_name(discord_bot.core.guild.roles, EVENT_PLAYER_ROLE_NAME)
        await ctx.author.remove_roles(event_role, reason="User dropped out of event")
    except ValueError:
        log.error(f"Could not find a role named '{EVENT_PLAYER_ROLE_NAME}'")
        await ctx.followup.send(f"Unable to find the appropriate role")
    except [Forbidden, HTTPException]:
        log.error(f"Could not remove role {event_role.name} from user {ctx.author.name}")
        await ctx.followup.send(f"Unable to revoke role")

    log.info(f"Role {event_role.name} removed from user {ctx.author.name}")
    await ctx.followup.send(f"Removed you from the event")


@bot.slash_command(guild_ids=DISCORD_GUILDS, description="Reset event roles")
@has_any_role(*DISCORD_ADMIN_ROLES, *DISCORD_EVENT_COORDINATOR_ROLES)
async def reset_event_roles(ctx):
    """Remove all event roles for users"""
    await ctx.response.defer(ephemeral=True)
    log.info(f"{ctx.author.name} used command /reset_event_roles")
    affected_members: list[str] = []

    try:
        for role_name in DISCORD_EVENT_USER_ROLES:
            event_role = get_role_by_name(discord_bot.core.guild.roles, role_name)
            for member in event_role.members:
                await member.remove_roles(event_role, reason="All event roles removed")
                affected_members.append(member.display_name)

    except ValueError:
        log.error(f"Could not find a role named '{role_name}'")
    except [Forbidden, HTTPException]:
        log.error(f"Could not remove role {event_role.name} from user {member.name}")

    log.info(f"User event roles removed from all users")
    await ctx.followup.send(f"Role removal process finished, affected members: {','.join(affected_members)}")
