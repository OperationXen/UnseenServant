from discord.commands import Option, has_any_role
from django.db import IntegrityError
from django.forms import ValidationError

from discordbot.bot import bot
from discordbot.components.admin import AdminUserCreatedEmbed
from config.settings import DISCORD_GUILDS, DISCORD_ADMIN_ROLES
from core.utils.admin import create_new_dm_from_discord_user, create_new_admin_user

@bot.slash_command(guild_ids=DISCORD_GUILDS, description='Resummon the Unseen Servant')
@has_any_role(*DISCORD_ADMIN_ROLES)
async def register_as_dm(ctx, 
        name: Option(str, 'The display name you want to use as your DM name', required=False) = None,  
        description: Option(str, 'A brief blurb about you and your Dungeoneering preferences', required=False) = None):
    """ Registers the user as a DM and creates them an admin page user """
    try:
        await create_new_dm_from_discord_user(ctx.user, name, description)
        username, password = await create_new_admin_user(name or ctx.user.name)
    except (ValidationError, IntegrityError):
        await ctx.respond(f"Failed to create new Dungeon Master, are you already registered?", ephemeral=True, delete_after=10)
        return

    await ctx.user.send(f"", embed = AdminUserCreatedEmbed(username=username, password = password))
    await ctx.respond(f"Registration successful, please check your PMs", ephemeral=True, delete_after=10)
