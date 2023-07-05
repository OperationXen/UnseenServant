from asgiref.sync import async_to_sync

from discord import Member, Guild

from discord_bot.bot import bot
from config.settings import DISCORD_GUILDS
from core.utils.players import get_user_highest_rank, get_bonus_credits, get_user_pending_games_count


def get_member_from_guild(guild: Guild, member_id: str) -> Member:
    """Get a member instance from specified guild"""
    member = guild.fetch_member(member_id)
    return member


@async_to_sync
async def get_roles_for_user_id(discord_id: str) -> list[str] | None:
    """Ask discord for the roles for a given user ID"""
    for guild_id in DISCORD_GUILDS:
        guild = await bot.fetch_guild(guild_id)
        member = await get_member_from_guild(guild, discord_id)
        if member:
            return member.roles
    return None


def get_user_max_credit(discord_id: str) -> int:
    """Get the maximum credit balance for a given user"""
    roles = get_roles_for_user_id(discord_id)
    rank = get_user_highest_rank(roles)
    if rank:
        max_games = rank.max_games
    bonuses = get_bonus_credits(discord_id)
    return max_games + bonuses


def get_user_available_credit(discord_id: str) -> int:
    """Attempt to get the available credits for a discord user"""
    total_credits = get_user_max_credit(discord_id)
    used_credits = get_user_pending_games_count(discord_id)
    return total_credits - used_credits
