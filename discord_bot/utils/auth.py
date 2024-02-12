from discord import Member as DiscordMember

from discord_bot.logs import logger as log
from core.models.auth import CustomUser
from core.utils.ranks import get_ranks_for_discord_roles


def create_user_from_discord_member(discord_member: DiscordMember) -> CustomUser:
    """Create an Unseen Servant user to represent a discord user"""
    try:
        log.info(f"[-] Creating a new Unseen Servant user for {discord_member.name}")
        user = CustomUser.objects.create_user(
            username=discord_member.name,
            discord_name=discord_member.display_name.title(),
            discord_id=discord_member.id,
            avatar=discord_member.display_avatar,
        )
        # Discord Users can only access the application when authenticated by discord, no admin login
        user.set_unusable_password()
        # Match any Unseen Servant ranks to the passed role list and assign
        ranks = get_ranks_for_discord_roles(discord_member.roles)
        user.ranks.set(ranks)
        user.save()

        return user
    except Exception as e:
        log.error(f"[!] Exception occured creating new user: {e.message}")
        return None
