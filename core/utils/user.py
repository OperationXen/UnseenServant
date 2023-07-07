from core.utils.players import get_bonus_credits, get_user_pending_games_count
from core.utils.ranks import get_highest_rank
from core.models.auth import CustomUser


def get_user_max_credit(user: CustomUser) -> int:
    """Get the maximum credit balance for a given user"""
    try:
        ranks = list(user.ranks.all())
        rank = get_highest_rank(ranks)
    except Exception as e:
        print(e)
    if rank:
        max_games = rank.max_games
    bonuses = get_bonus_credits(user.discord_id)
    return max_games + bonuses


def get_user_available_credit(user: CustomUser) -> int:
    """Attempt to get the available credits for a logged in user"""
    total_credits = get_user_max_credit(user)
    used_credits = get_user_pending_games_count(user.discord_id)
    return total_credits - used_credits


def get_user_by_discord_id(discord_id: str) -> CustomUser:
    try:
        return CustomUser.objects.get(discord_id=discord_id)
    except CustomUser.DoesNotExist:
        return None
