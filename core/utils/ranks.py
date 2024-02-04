from django.db.models import Q
from discord.role import Role as DiscordRole

from core.models import Rank


def get_ranks_for_discord_roles(discord_user_roles: list) -> list[Rank]:
    """Gather a list of rank objects for a given list of rank names, identifiers or discord roles"""
    user_ranks = []

    for role in discord_user_roles:
        try:
            if type(role) is DiscordRole:
                rank = Rank.objects.get(name__iexact=role.name)
            elif type(role) is str:
                rank = Rank.objects.get(Q(discord_id=role) | Q(name__iexact=role))
            user_ranks.append(rank)
        except Exception as e:
            pass
    return user_ranks


def get_highest_rank(ranks: list[Rank]) -> Rank:
    """Given a list of ranks, return the highest"""
    ranks.sort(key=lambda x: x.priority, reverse=True)
    try:
        return ranks[0]
    except Exception as e:
        return None


def get_user_highest_rank(discord_user_roles: list) -> Rank:
    """Given a users list of roles, returns their highest matching rank"""
    user_ranks = get_ranks_for_discord_roles(discord_user_roles)
    highest_rank = get_highest_rank(user_ranks)
    return highest_rank
