from discord import User

from discord.errors import Forbidden
from discordbot.logs import logger as log
from config.settings import DISCORD_ADMIN_ROLES

async def grant_role_to_user(role_name, user):
    """ Give an arbitrarily named permission to a user """
    log.info(f"Attempting to add role '{role_name}' to user '{user.name}#{user.discriminator}'")
    for role in user.guild.roles:
        if role.name == role_name:
            try:
                await user.add_roles(role)
                log.info(' - SUCCESS')
                return True
            except Forbidden:
                log.info(f" - FAILED (Insufficent permissions)")
                log.error(f"Failed to add role '{role_name}' to user '{user.name}#{user.discriminator}'")
                return False
    log.error(f"Failed to locate role '{role_name}'")
    return False

async def set_user_dm_registered(user):
    """ Given a discord user, grant them the 'bot-registered' permission """
    result = await grant_role_to_user('bot-registered', user)
    return result

def get_user_role_names(discord_user: User) -> list[str]:
    """ Fetch a list of the users role names (slight hack - could use actual roles) """
    user_role_names = [role.name for role in discord_user.roles]
    return user_role_names

def discord_user_is_admin(discord_user: User) -> bool:
    """ Check if user has any of the specified admin permissions """
    user_role_names = get_user_role_names(discord_user)
    matching_roles = list(set(user_role_names) & set(DISCORD_ADMIN_ROLES))
    if matching_roles:
        return True
    return False
