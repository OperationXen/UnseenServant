from discord.errors import Forbidden
from discordbot.logs import logger as log

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
